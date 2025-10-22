from imggenerator import BreakcoreGenerator, Settings
from parsers.pinterest import PinterestDownloader, Options
from pin_to_input import ImageMover
from pompt_generator import PromptGenerator
from config import OUT_DIR

from config import NEGATIVE_PROMPT, TEST_PROMPT

def main():
    
    """все класы и функции"""
    # ###############################
    # settings = Settings(
    # height=512,
    # width=512,
    # num_inference_steps=40,
    # guidance_scale=7.5,
    # strength=0.3,
    # lora_scale=0.8
    # )
    # processor = BreakcoreGenerator()
    
    # processor.settings = settings
    # processor.generate(TEST_PROMPT, NEGATIVE_PROMPT)
    
    # processor.settings = settings
    # processor.generate_text2img(TEST_PROMPT, NEGATIVE_PROMPT)
    
    # ################################
    # mover = ImageMover()
    
    # mover.move_first_image()
    
    # mover.move_user_image()
    # ################################
    # prompt_gen = PromptGenerator()
    
    # prompt_gen.generate_prompt()
    # ################################
    # options = Options(
    # url="https://ru.pinterest.com/search/pins/?q=breackcore%20anime&rs=typed",
    # out_dir = OUT_DIR
    # )
    # downloader = PinterestDownloader(options)
    # downloader.run()    
    # ###############################
    
    print("Мейн запущен, раскомментируйте строки для проверки функций")
    
if __name__ == "__main__":
    main()
