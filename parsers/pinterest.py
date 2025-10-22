import hashlib
import json
import os
import random
import re
import time
from dataclasses import dataclass
from typing import List, Optional

import requests
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from config import USER_AGENT, PINIMG_HOSTS
@dataclass
class Options:
    url: str
    out_dir: str
    timeout: int = 20
    cookie: Optional[str] = None
    proxy: Optional[str] = None


class PinterestDownloader:
    def __init__(self, opts: Options):
        self.opts = opts
        self.session = self.make_session()

    def make_session(self) -> requests.Session:
        s = requests.Session()
        headers = {
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
            "Referer": "https://www.pinterest.com/",
        }
        if self.opts.cookie:
            headers["Cookie"] = self.opts.cookie
        s.headers.update(headers)
        if self.opts.proxy:
            s.proxies.update({"http": self.opts.proxy, "https": self.opts.proxy})
        s.timeout = self.opts.timeout
        return s

    @staticmethod
    def setup_chrome_driver(headless: bool = True) -> webdriver.Chrome:
        chrome_options = ChromeOptions()
        if headless:
            chrome_options.add_argument("--headless=new")
        chrome_options.add_argument(f"--user-agent={USER_AGENT}")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-plugins-discovery")
        chrome_options.add_argument("--disable-web-security")
        prefs = {
            "profile.default_content_setting_values.notifications": 2,
            "profile.default_content_settings.popups": 0,
            "profile.managed_default_content_settings.images": 2
        }
        chrome_options.add_experimental_option("prefs", prefs)
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        driver = webdriver.Chrome(options=chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        return driver

    @classmethod
    def fetch_html_selenium(cls, url: str, headless: bool = True, max_retries: int = 3) -> str:
        for attempt in range(max_retries):
            driver = cls.setup_chrome_driver(headless)
            print(f"Попытка {attempt + 1}: Загружаем страницу...")
            driver.get(url)
            wait = WebDriverWait(driver, 15)
            wait.until(lambda d: d.find_element(By.TAG_NAME, "img") or d.find_element(By.ID, "__PWS_DATA__"))
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
            time.sleep(2)
            driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(1)
            html = driver.page_source
            driver.quit()
            if len(html) < 1000:
                raise ValueError("Получена слишком короткая страница")
            return html

    @staticmethod
    def extract_image_urls(html: str) -> List[str]:
        soup = BeautifulSoup(html, "html.parser")
        urls: List[str] = []
        data_script = soup.find("script", {"id": "__PWS_DATA__"})
        if data_script and data_script.string:
            data = json.loads(data_script.string)
            pins = data.get("props", {}).get("initialReduxState", {}).get("pins", {})
            for _, pin_data in pins.items():
                images = pin_data.get("images", {})
                for size in images.values():
                    if isinstance(size, dict) and "url" in size:
                        urls.append(size["url"])
        for img in soup.find_all("img"):
            if img.has_attr("src"):
                src = img["src"]
                if any(host in src for host in PINIMG_HOSTS):
                    urls.append(src)
            if img.has_attr("data-src"):
                data_src = img["data-src"]
                if any(host in data_src for host in PINIMG_HOSTS):
                    urls.append(data_src)
            if img.has_attr("srcset"):
                for candidate in img["srcset"].split(","):
                    u = candidate.strip().split(" ")[0]
                    if any(host in u for host in PINIMG_HOSTS):
                        urls.append(u)
        for element in soup.find_all(attrs={"data-pin-media": True}):
            media_url = element.get("data-pin-media")
            if media_url and any(host in media_url for host in PINIMG_HOSTS):
                urls.append(media_url)
        unique_urls = list(set(urls))
        filtered_urls = []
        for url in unique_urls:
            if re.search(r'/\d{2,3}x\d{2,3}/', url):
                continue
            if any(word in url.lower() for word in ['avatar', 'icon', 'logo']):
                continue
            filtered_urls.append(url)
        return filtered_urls

    @staticmethod
    def upgrade_to_original(url: str) -> str:
        url = re.sub(r'/\d{2,4}x\d{0,4}/', '/originals/', url)
        url = re.sub(r'/\d{2,4}x/', '/originals/', url)
        return url

    @classmethod
    def pick_random(cls, urls: List[str]) -> Optional[str]:
        pinimg_urls = [u for u in urls if any(host in u for host in PINIMG_HOSTS)]
        if not pinimg_urls:
            return None
        large_urls = [u for u in pinimg_urls if '/736x/' in u or '/originals/' in u]
        chosen = random.choice(large_urls) if large_urls else random.choice(pinimg_urls)
        return cls.upgrade_to_original(chosen)

    @staticmethod
    def filename_for(url: str, content_type: Optional[str] = None) -> str:
        name_hash = hashlib.sha256(url.encode("utf-8")).hexdigest()[:16]
        if content_type:
            if "jpeg" in content_type or "jpg" in content_type:
                ext = ".jpg"
            elif "png" in content_type:
                ext = ".png"
            elif "webp" in content_type:
                ext = ".webp"
            elif "gif" in content_type:
                ext = ".gif"
            else:
                ext = ".jpg"
        else:
            parsed_ext = os.path.splitext(url.split("?")[0])[1].lower()
            if parsed_ext in [".jpg", ".jpeg", ".png", ".webp", ".gif"]:
                ext = parsed_ext if parsed_ext != ".jpeg" else ".jpg"
            else:
                ext = ".jpg"
        return f"pinterest_{name_hash}{ext}"

    def download_image(self, url: str, out_dir: str) -> str:
        os.makedirs(out_dir, exist_ok=True)
        headers = {
            "Referer": "https://www.pinterest.com/",
            "User-Agent": USER_AGENT,
            "Accept": "image/webp,image/apng,image/*,*/*;q=0.8"
        }
        r = self.session.get(url, headers=headers, stream=True, timeout=30)
        r.raise_for_status()
        content_type = r.headers.get("Content-Type", "")
        if not content_type.startswith("image/"):
            raise ValueError(f"Не картинка: {url} (Content-Type={content_type})")
        fname = self.filename_for(url, content_type)
        path = os.path.join(out_dir, fname)
        with open(path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        print(f"Скачано: {fname} ({os.path.getsize(path)} bytes)")
        return path

    def try_download_with_fallback(self, url: str, out_dir: str) -> str:
        original_url = self.upgrade_to_original(url)
        urls_to_try = [
            original_url,
            re.sub(r'/originals/', '/736x/', original_url),
            re.sub(r'/originals/', '/564x/', original_url),
            url
        ]
        for attempt_url in urls_to_try:
            return self.download_image(attempt_url, out_dir)

    def run(self) -> int:
        print(f"Начинаем обработку: {self.opts.url}")
        html = self.fetch_html_selenium(self.opts.url)
        print(f"HTML загружен, размер: {len(html)} символов")
        urls = self.extract_image_urls(html)
        print(f"Найдено URL изображений: {len(urls)}")
        print("Примеры найденных URL:")
        for i, url in enumerate(urls[:5]):
            print(f"  {i+1}. {url}")
        random_url = self.pick_random(urls)
        print(f"Выбрано для скачивания: {random_url}")
        out_path = self.try_download_with_fallback(random_url, self.opts.out_dir)
        print(f"Успешно скачано: {out_path}")
        return 0