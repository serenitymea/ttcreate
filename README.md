# Pinterest → Stable Diffusion XL + LoRA (Gradio UI)

A script that lets you quickly download images from Pinterest and use them as references for generation with **Stable Diffusion XL**, featuring a convenient **Gradio** interface.

## Features

- Downloads images from Pinterest by link  
- Connects to a local SDXL setup via `diffusers`  
- Launches a Gradio interface for reference-based generation  
- Allows adjusting parameters such as strength, steps, seed, guidance, and more  


<img width="401" height="339" alt="image" src="https://github.com/user-attachments/assets/49281bb3-2c39-4de6-a4a8-c3a626e58a2e" />
<img width="288" height="349" alt="image" src="https://github.com/user-attachments/assets/396ca627-f3d9-4f88-bb85-2cbea92aa325" />


## Installation
1. Download Python 310
2. python -m venv .venv 
3. .\.venv\Scripts\Activate.ps1
4. pip install -r requirements.txt
5. pip3 install torch torchvision --index-url https://download.pytorch.org/whl/cu126
6. python interface.py
7. open url in terminal
