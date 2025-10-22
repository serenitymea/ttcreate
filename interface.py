import gradio as gr
import os
import subprocess
import platform
from imggenerator import BreakcoreGenerator, Settings
from parsers.pinterest import PinterestDownloader, Options
from pin_to_input import ImageMover
from pompt_generator import PromptGenerator

from config import NEGATIVE_PROMPT, OUT_DIR, INPUT_PATH, READY_FOLDER


settings = Settings(
    height=512,
    width=512,
    num_inference_steps=40,
    guidance_scale=7.5,
    strength=0.3,
    lora_scale=0.8
)

processor = BreakcoreGenerator(settings)
mover = ImageMover()
prompt_gen = PromptGenerator()

def get_current_image():
    """Получить текущее изображение для отображения"""
    if os.path.exists(INPUT_PATH):
        return INPUT_PATH
    return None

def move_image_action(url):
    """Переместить изображение и вернуть следующее"""
    options = Options(url=url, out_dir=OUT_DIR)
    downloader = PinterestDownloader(options)
    exit_code = downloader.run()
    print(f"Загрузка завершена, код: {exit_code}")
    mover.move_first_image()
    return get_current_image()

def upload_user_image(image_file):
    """Загрузить пользовательское изображение"""
    if image_file is not None:
        with open(image_file, "rb") as f:
            mover.move_user_image(f)
        print("Пользовательское изображение загружено")
        return get_current_image()
    return None

def open_ready_folder():
    """Открыть папку c готовыми изоб"""
    if not os.path.exists(READY_FOLDER):
        os.makedirs(READY_FOLDER, exist_ok=True)
        print(f"Создана папка {READY_FOLDER}")
    
    system = platform.system()
    try:
        if system == "Windows":
            os.startfile(READY_FOLDER)
        elif system == "Darwin":
            subprocess.run(["open", READY_FOLDER])
        else:
            subprocess.run(["xdg-open", READY_FOLDER])
        print(f"Открыта папка {READY_FOLDER}")
        return "Папка открыта"
    except Exception as e:
        print(f"Ошибка при открытии папки: {e}")
        return f"Ошибка: {e}"

def update_mode_visibility(mode):
    """Обновить видимость элементов в зависимости от режима"""
    is_img2img = mode == "img2img"
    return {
        source_image: gr.update(visible=is_img2img),
        move_btn: gr.update(visible=is_img2img),
        url_input: gr.update(visible=is_img2img),
        upload_image: gr.update(visible=is_img2img),
        upload_btn: gr.update(visible=is_img2img)
    }

def run_pipeline(mode, url, height, width, steps, guidance, strength, lora_scale, use_custom_prompt, custom_prompt, use_custom_negative, custom_negative):
    """Основной цикл загрузки и генерации"""
    
    custom_settings = Settings(
        height=height,
        width=width,
        num_inference_steps=steps,
        guidance_scale=guidance,
        strength=strength,
        lora_scale=lora_scale
    )
    processor.settings = custom_settings

    if use_custom_prompt and custom_prompt.strip():
        prompt = custom_prompt.strip()
    else:
        prompt = prompt_gen.generate_prompt()

    if use_custom_negative and custom_negative.strip():
        negative_prompt = custom_negative.strip()
    else:
        negative_prompt = NEGATIVE_PROMPT
    
    print(f"Промпт: {prompt}")
    print(f"Негативный промпт: {negative_prompt}")
    
    if mode == "img2img":
        
        result_image = processor.generate(prompt, negative_prompt)
    else:
        result_image = processor.generate_text2img(prompt, negative_prompt)
    
    print(f"Готово")
    
    return result_image

def start_infinite_generation(mode, url, height, width, steps, guidance, strength, lora_scale, use_custom_prompt, custom_prompt, use_custom_negative, custom_negative):
    """Запустить бесконечную генерацию"""
    
    generation_count = 0
    
    while True:
        generation_count += 1
        print(f"\n{'='*50}")
        print(f"Генерация #{generation_count}")
        print(f"{'='*50}\n")

        result_image = run_pipeline(
            mode, url, height, width, steps, guidance, strength, lora_scale,
            use_custom_prompt, custom_prompt, use_custom_negative, custom_negative
        )

        yield result_image, f"Сгенерировано изображений: {generation_count}", gr.update(interactive=False), gr.update(interactive=True)

def reset_buttons():
    """Сбросить состояние кнопок"""
    return gr.update(interactive=True), gr.update(interactive=False), "Генерация остановлена"

with gr.Blocks(title="Breakcore Generator") as demo:
    gr.Markdown("## Breakcore Image Generator")
    gr.Markdown("Генерация изображений в стиле Breakcore")

    with gr.Row():
        mode_radio = gr.Radio(
            choices=["img2img", "txt2img"],
            value="img2img",
            label="Режим генерации",
            scale=1
        )

    with gr.Row():
        url_input = gr.Textbox(
            label="Pinterest URL",
            value="https://ru.pinterest.com/search/pins/?q=breakcore%20anime&rs=typed",
            lines=1
        )

    gr.Markdown("### Параметры генерации")
    
    with gr.Row():
        height_slider = gr.Slider(label="Высота", minimum=256, maximum=1024, step=64, value=512)
        width_slider = gr.Slider(label="Ширина", minimum=256, maximum=1024, step=64, value=512)
    
    with gr.Row():
        steps_slider = gr.Slider(label="Шаги инференса", minimum=10, maximum=100, step=5, value=40)
        guidance_slider = gr.Slider(label="Guidance Scale", minimum=1.0, maximum=20.0, step=0.5, value=7.5)
    
    with gr.Row():
        strength_slider = gr.Slider(label="Strength", minimum=0.1, maximum=1.0, step=0.1, value=0.3)
        lora_scale_slider = gr.Slider(label="LoRA Scale", minimum=0.0, maximum=2.0, step=0.1, value=0.8)

    gr.Markdown("### Промпты")
    
    with gr.Row():
        use_custom_prompt_checkbox = gr.Checkbox(label="Использовать свой промпт", value=False)
        custom_prompt_input = gr.Textbox(
            label="Свой промпт",
            placeholder="Введите свой промпт...",
            lines=2
        )
    
    with gr.Row():
        use_custom_negative_checkbox = gr.Checkbox(label="Использовать свой негативный промпт", value=False)
        custom_negative_input = gr.Textbox(
            label="Свой негативный промпт",
            placeholder="Введите свой негативный промпт...",
            lines=2
        )

    with gr.Row():
        generate_btn = gr.Button("Запустить генерацию", variant="primary", size="lg")
        infinite_generate_btn = gr.Button("Бесконечная генерация", variant="primary", size="lg")
        stop_btn = gr.Button("Остановить", variant="stop", size="lg", interactive=False)
    
    output_image = gr.Image(label="Результат")

    generation_status = gr.Textbox(label="Статус генерации", value="", visible=True)
    
    open_folder_btn = gr.Button("Открыть папку с скачеными готовыми изображениями", variant="secondary")
    folder_status = gr.Textbox(label="Статус", visible=False)

    gr.Markdown("### Исходное изображение")
    
    source_image = gr.Image(label="Текущее изображение", type="filepath")
    
    with gr.Row():
        move_btn = gr.Button("Скачать и поставить следующее изображение")
    
    gr.Markdown("**Или загрузите свое изображение:**")
    
    with gr.Row():
        upload_image = gr.Image(label="Загрузить свое изображение", type="filepath")
        upload_btn = gr.Button("Использовать это изображение")
    
    move_btn.click(
        fn=move_image_action,
        inputs=url_input,
        outputs=source_image
    )
    
    upload_btn.click(
        fn=upload_user_image,
        inputs=upload_image,
        outputs=source_image
    )
    
    open_folder_btn.click(
        fn=open_ready_folder,
        outputs=folder_status
    )

    mode_radio.change(
        fn=update_mode_visibility,
        inputs=mode_radio,
        outputs=[source_image, move_btn, url_input, upload_image, upload_btn]
    )

    generate_btn.click(
        fn=run_pipeline,
        inputs=[
            mode_radio,
            url_input, 
            height_slider, 
            width_slider, 
            steps_slider, 
            guidance_slider, 
            strength_slider, 
            lora_scale_slider,
            use_custom_prompt_checkbox,
            custom_prompt_input,
            use_custom_negative_checkbox,
            custom_negative_input
        ],
        outputs=output_image
    )

    infinite_gen_event = infinite_generate_btn.click(
        fn=start_infinite_generation,
        inputs=[
            mode_radio,
            url_input, 
            height_slider, 
            width_slider, 
            steps_slider, 
            guidance_slider, 
            strength_slider, 
            lora_scale_slider,
            use_custom_prompt_checkbox,
            custom_prompt_input,
            use_custom_negative_checkbox,
            custom_negative_input
        ],
        outputs=[output_image, generation_status, infinite_generate_btn, stop_btn]
    )

    stop_btn.click(
        fn=reset_buttons,
        outputs=[infinite_generate_btn, stop_btn, generation_status],
        cancels=[infinite_gen_event]
    )

    demo.load(fn=get_current_image, outputs=source_image)

demo.launch()