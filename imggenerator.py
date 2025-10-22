import os
from diffusers import StableDiffusionXLPipeline, StableDiffusionXLImg2ImgPipeline
import torch
from PIL import Image
from huggingface_hub import login
from datetime import datetime
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

from config import LORA_PATH, CACHE_DIR, INPUT_PATH, OUTPUT_DIR

load_dotenv()
api_key = os.getenv("HUGGINGFACE_TOKEN")
login(token=api_key)

@dataclass
class Settings:    
    height: int = 512
    width: int = 512
    num_inference_steps: int = 40
    guidance_scale: float = 7.5
    strength: float = 0.3
    lora_scale: float = 0.8

class BreakcoreGenerator:
    def __init__(self, settings: Optional[Settings] = None):
        if settings is None:
            settings = Settings()
        
        self.settings = settings
        self.output_dir = OUTPUT_DIR

    def generate_text2img(self, prompt, neg_prompt):
        
        pipe = StableDiffusionXLPipeline.from_pretrained(
            "stabilityai/stable-diffusion-xl-base-1.0",
            torch_dtype=torch.float16,
            use_safetensors=True,
            cache_dir=CACHE_DIR,
            variant="fp16"
        ).to("cuda")
        
        pipe.safety_checker = None
        pipe.load_lora_weights(LORA_PATH)
        
        seed = torch.seed()
        generator = torch.Generator(device="cuda").manual_seed(seed)
        
        result = pipe(
            prompt=prompt,
            negative_prompt=neg_prompt,
            height=self.settings.height,
            width=self.settings.width,
            num_inference_steps=self.settings.num_inference_steps,
            guidance_scale=self.settings.guidance_scale,
            generator=generator,
            cross_attention_kwargs={"scale": self.settings.lora_scale}
        )
        
        del pipe
        torch.cuda.empty_cache()
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(self.output_dir, f"txt2img{timestamp}.png")
        result.images[0].save(filename)
        print(f"Сохранено: {filename}\n")
        
        return result.images[0]
        
    def generate(self, prompt, neg_prompt):
        
        pipe = StableDiffusionXLImg2ImgPipeline.from_pretrained(
            "stabilityai/stable-diffusion-xl-base-1.0",
            torch_dtype=torch.float16,
            use_safetensors=True,
            cache_dir=CACHE_DIR,
            variant="fp16"
        ).to("cuda")
        
        pipe.safety_checker = None
        pipe.load_lora_weights(LORA_PATH)
        
        init_image = Image.open(INPUT_PATH).convert("RGB").resize((self.settings.width, self.settings.height))
        print(f"Загружено входное изображение: {INPUT_PATH}")
        
        seed = torch.seed()
        generator = torch.Generator(device="cuda").manual_seed(seed)
        
        print(f"Prompt: {prompt}")
        print("Генерация img2img...")
        
        result = pipe(
            prompt=prompt,
            image=init_image,
            negative_prompt=neg_prompt,
            strength=self.settings.strength,
            num_inference_steps=self.settings.num_inference_steps,
            guidance_scale=self.settings.guidance_scale,
            generator=generator,
            cross_attention_kwargs={"scale": self.settings.lora_scale}
        )
        
        del pipe
        torch.cuda.empty_cache()
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(self.output_dir, f"img2img{timestamp}.png")
        result.images[0].save(filename)
        print(f"Сохранено: {filename}\n")
        
        return result.images[0]