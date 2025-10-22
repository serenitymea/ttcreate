import os
import shutil
from PIL import Image

class ImageMover:
    def __init__(self):
        self.source_folder = "D:/ttcreate/pin_downloads"
        self.target_folder = "D:/ttcreate/input_folder"
        self.image_extensions = ['.png', '.jpg', '.jpeg']

    def clear_target_folder(self):
        """Полностью очищает папку назначения."""
        try:
            if os.path.exists(self.target_folder):
                for entry in os.scandir(self.target_folder):
                    path = entry.path
                    if entry.is_file() or entry.is_symlink():
                        os.remove(path)
                    elif entry.is_dir():
                        shutil.rmtree(path)
                print(f"Папка {self.target_folder} очищена")
            else:
                os.makedirs(self.target_folder, exist_ok=True)
                print(f"Создана папка {self.target_folder}")
        except Exception as e:
            print(f"Не удалось очистить папку {self.target_folder}: {e}")


    def move_first_image(self):
        """Перемещает и конвертирует первое найденное изображение в PNG"""
        self.clear_target_folder()

        files = os.listdir(self.source_folder)

        for file in sorted(files):
            file_lower = file.lower()
            if any(file_lower.endswith(ext) for ext in self.image_extensions):
                old_path = os.path.join(self.source_folder, file)
                new_path = os.path.join(self.target_folder, "input.png")

                with Image.open(old_path) as img:
                    if img.mode not in ("RGB", "RGBA"):
                        img = img.convert("RGBA")
                    img.save(new_path, format="PNG")

                if os.path.exists(new_path):
                    os.remove(old_path)

                print(f"перемещено -> input.png")
                return
            
    def move_user_image(self, image_file):
        """Принимает файл изображения и конвертирует его в PNG
        """
        self.clear_target_folder()

        new_path = os.path.join(self.target_folder, "input.png")

        try:
            img = Image.open(image_file)
            if img.mode not in ("RGB", "RGBA"):
                img = img.convert("RGBA")
            img.save(new_path, format="PNG")

            print(f"перемещено -> input.png")
            return new_path
        except Exception as e:
            print(f"Ошибка при обработке изображения: {e}")
            return None