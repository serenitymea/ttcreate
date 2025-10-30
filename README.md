# Pinterest → Stable Diffusion XL + Lora (Gradio UI)

Скрипт, который позволяет быстро скачать изображения с Pinterest и использовать их как референсы для генерации через **Stable Diffusion XL** с удобным интерфейсом на **Gradio**.

## Что умеет

- качает картинки с Pinterest по ключевым словам, доскам или аккаунтам;  
- подключается к локальной SDXL через `diffusers`;  
- поднимает Gradio-интерфейс для генерации по референсу;  
- позволяет настраивать strength, steps, seed, guidance и т.д.


<img width="401" height="339" alt="image" src="https://github.com/user-attachments/assets/49281bb3-2c39-4de6-a4a8-c3a626e58a2e" />
<img width="288" height="349" alt="image" src="https://github.com/user-attachments/assets/396ca627-f3d9-4f88-bb85-2cbea92aa325" />


## Установка
1. Download Python 310
2. python -m venv .venv 
3. .\.venv\Scripts\Activate.ps1
4. pip install -r requirements.txt
5. pip3 install torch torchvision --index-url https://download.pytorch.org/whl/cu126
6. python interface.py
7. open url in terminal
