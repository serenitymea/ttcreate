import os
from diffusers import StableDiffusionXLPipeline, StableDiffusionXLImg2ImgPipeline
import torch
from datetime import datetime
from huggingface_hub import login
from PIL import Image
from dotenv import load_dotenv

from config import LORA_PATH, CACHE_DIR, TEST_OUTPUT, INPUT_PATH, TEST_PROMPT, NEGATIVE_PROMPT, SEED

load_dotenv()
api_key = os.getenv("HUGGINGFACE_TOKEN")
login(token=api_key)

os.makedirs(TEST_OUTPUT, exist_ok=True)

def test_without_lora():
    """Тест без LoRA"""
    
    pipe = StableDiffusionXLPipeline.from_pretrained(
        "stabilityai/stable-diffusion-xl-base-1.0",
        torch_dtype=torch.float16,
        use_safetensors=True,
        cache_dir=CACHE_DIR,
        variant="fp16"
    ).to("cuda")
    
    pipe.safety_checker = None

    generator = torch.Generator(device="cuda").manual_seed(SEED)
    
    print(f"Prompt: {TEST_PROMPT}")
    print("Генерация...")
    
    result = pipe(
        prompt=TEST_PROMPT,
        negative_prompt=NEGATIVE_PROMPT,
        height=512,
        width=512,
        num_inference_steps=40,
        guidance_scale=7.5,
        generator=generator
    )
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(TEST_OUTPUT, f"test_WITHOUT_lora_{timestamp}.png")
    result.images[0].save(filename)
    print(f"Сохранено: {filename}\n")

    del pipe
    torch.cuda.empty_cache()
    
    return filename

def test_with_lora():
    """Тест с LoRA"""
    
    pipe = StableDiffusionXLPipeline.from_pretrained(
        "stabilityai/stable-diffusion-xl-base-1.0",
        torch_dtype=torch.float16,
        use_safetensors=True,
        cache_dir=CACHE_DIR,
        variant="fp16"
    ).to("cuda")
    
    pipe.safety_checker = None

    print(f"Загрузка LoRA: {LORA_PATH}")
    pipe.load_lora_weights(LORA_PATH)
    print("LoRA загружена")

    generator = torch.Generator(device="cuda").manual_seed(SEED)
    
    print(f"Prompt: {TEST_PROMPT}")
    print("Генерация...")
    
    result = pipe(
        prompt=TEST_PROMPT,
        negative_prompt=NEGATIVE_PROMPT,
        height=512,
        width=512,
        num_inference_steps=40,
        guidance_scale=7.5,
        generator=generator,
        cross_attention_kwargs={"scale": 0.8}  # LoRA scale
    )
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(TEST_OUTPUT, f"test_WITH_lora_scale08_{timestamp}.png")
    result.images[0].save(filename)
    print(f"Сохранено: {filename}\n")

    del pipe
    torch.cuda.empty_cache()
    
    return filename

def test_img2img_without_lora():
    """Тест img2img БЕЗ LoRA"""

    if not os.path.exists(INPUT_PATH):
        print(f"Файл {INPUT_PATH} не найден!")
        print("Создаю тестовое изображение...")
        test_img = Image.new('RGB', (1024, 1024), color=(100, 150, 200))
        test_img.save(INPUT_PATH)
        print(f"Создано тестовое изображение: {INPUT_PATH}")
    
    pipe = StableDiffusionXLImg2ImgPipeline.from_pretrained(
        "stabilityai/stable-diffusion-xl-base-1.0",
        torch_dtype=torch.float16,
        use_safetensors=True,
        cache_dir=CACHE_DIR,
        variant="fp16"
    ).to("cuda")
    
    pipe.safety_checker = None

    init_image = Image.open(INPUT_PATH).convert("RGB").resize((1024, 1024))
    print(f"Загружено входное изображение: {INPUT_PATH}")
    
    generator = torch.Generator(device="cuda").manual_seed(SEED)
    
    print(f"Prompt: {TEST_PROMPT}")
    print("Генерация img2img...")
    
    result = pipe(
        prompt=TEST_PROMPT,
        image=init_image,
        negative_prompt=NEGATIVE_PROMPT,
        strength=0.5,
        num_inference_steps=40,
        guidance_scale=7.5,
        generator=generator
    )
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(TEST_OUTPUT, f"test_img2img_WITHOUT_lora_{timestamp}.png")
    result.images[0].save(filename)
    print(f"Сохранено: {filename}\n")
    
    del pipe
    torch.cuda.empty_cache()
    
    return filename

def test_img2img_with_lora():
    """Тест img2img С LoRA"""
    
    if not os.path.exists(INPUT_PATH):
        print(f"Файл {INPUT_PATH} не найден!")
        print("Создаю тестовое изображение...")
        test_img = Image.new('RGB', (1024, 1024), color=(100, 150, 200))
        test_img.save(INPUT_PATH)
        print(f"Создано тестовое изображение: {INPUT_PATH}")
    
    pipe = StableDiffusionXLImg2ImgPipeline.from_pretrained(
        "stabilityai/stable-diffusion-xl-base-1.0",
        torch_dtype=torch.float16,
        use_safetensors=True,
        cache_dir=CACHE_DIR,
        variant="fp16"
    ).to("cuda")
    
    pipe.safety_checker = None

    print(f"Загрузка LoRA: {LORA_PATH}")
    pipe.load_lora_weights(LORA_PATH)
    print("LoRA загружена")
    
    init_image = Image.open(INPUT_PATH).convert("RGB").resize((1024, 1024))
    print(f"Загружено входное изображение: {INPUT_PATH}")
    
    generator = torch.Generator(device="cuda").manual_seed(SEED)
    
    print(f"Prompt: {TEST_PROMPT}")
    print("Генерация img2img...")
    
    result = pipe(
        prompt=TEST_PROMPT,
        image=init_image,
        negative_prompt=NEGATIVE_PROMPT,
        strength=0.5,
        num_inference_steps=40,
        guidance_scale=7.5,
        generator=generator,
        cross_attention_kwargs={"scale": 0.8}
    )
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(TEST_OUTPUT, f"test_img2img_WITH_lora_scale08_{timestamp}.png")
    result.images[0].save(filename)
    print(f"Сохранено: {filename}\n")
    
    del pipe
    torch.cuda.empty_cache()
    
    return filename

if __name__ == "__main__":

    print("ТЕСТИРОВАНИЕ")
    
    try:
        file1 = test_without_lora()
        file2 = test_with_lora()

        file4 = test_img2img_without_lora()
        file5 = test_img2img_with_lora()
        
        print("\n" + "=" * 60)
        print("✓ ВСЕ ТЕСТЫ ЗАВЕРШЕНЫ")
        print("=" * 60)
        print("\nПапка с результатами:", TEST_OUTPUT)
        
    except Exception as e:
        print(f"\nОШИБКА: {e}")
        import traceback
        traceback.print_exc()