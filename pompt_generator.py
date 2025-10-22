import os
from dotenv import load_dotenv
from openai import OpenAI


class PromptGenerator:
    """генератор промптов"""

    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key)

    def generate_prompt(self) -> str:
        """
        Генерирует промпт
        """
        system_prompt = """You are an expert in generating prompts for Stable Diffusion XL 
that create breakcore/glitch/datamosh aesthetic images with anime girls.

CRITICAL STYLE ELEMENTS TO INCLUDE:
- Glitch effects: datamoshing, pixel sorting, RGB chromatic aberration, scan lines
- Digital corruption: compression artifacts, noise, distortion, bit crushing
- Visual layers: overlapping UI elements, code snippets, error messages, digital text
- Color palette: neon cyan, lime green, hot pink, electric blue, harsh whites, deep blacks
- High contrast with crushed blacks and blown highlights
- Matrix-style digital rain, terminal windows, cyberpunk UI elements
- Heavy post-processing effects

TECHNICAL KEYWORDS TO USE:
glitch art, datamosh, pixel sorting, chromatic aberration, RGB split, scan lines, 
VHS distortion, digital noise, compression artifacts, cyberpunk, net art, 
terminal aesthetic, code overlay, corrupted data, bit crushed, overexposed, 
high contrast, neon colors, cybercore, webcore

Generate ONE detailed positive prompt mixing these elements."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": (
                            "Generate a detailed Stable Diffusion XL prompt for an anime girl "
                            "with EXTREME breakcore/glitch/datamosh aesthetic.\n\n"
                            "Must include:\n"
                            "1. Specific glitch effects (RGB split, pixel sorting, scan lines)\n"
                            "2. Digital corruption elements (code overlay, terminal windows, UI glitches)\n"
                            "3. Neon color scheme (cyan, lime green, hot pink, electric blue)\n"
                            "4. High contrast with crushed blacks\n"
                            "5. Character details (hair, eyes, expression)\n"
                            "6. Atmosphere (cyberpunk, digital chaos, corrupted data)\n\n"
                            "Style references: datamosh art, net art, cybercore, webcore, Y2K aesthetic\n\n"
                            "Format: single paragraph, comma-separated keywords, no negative prompt."
                        )
                    }
                ],
                max_tokens=250,
                temperature=0.95
            )
            
            prompt = response.choices[0].message.content.strip()

            essential_tags = [
                "glitch art", "datamosh", "chromatic aberration", 
                "high contrast", "neon colors", "digital corruption"
            ]
            
            prompt_lower = prompt.lower()
            missing_tags = [tag for tag in essential_tags if tag not in prompt_lower]
            
            if missing_tags:
                prompt += ", " + ", ".join(missing_tags)
            
            return prompt
            
        except Exception as e:
            raise Exception(f"ошибка при генерации промпта: {str(e)}")