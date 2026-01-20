import os
import time
from google.genai import Client
from dotenv import load_dotenv

load_dotenv()
client = Client(api_key=os.getenv("GEMINI_API_KEY"))


def _extract_text(response):
    if hasattr(response, "text") and response.text:
        return response.text

    if hasattr(response, "candidates"):
        for c in response.candidates:
            if hasattr(c, "content"):
                for p in c.content.parts:
                    if hasattr(p, "text") and p.text:
                        return p.text
    return None


def generate_code(layout: dict, framework: str) -> str:
    prompt = f"""
YOU MUST OUTPUT ONLY RAW HTML.
DO NOT WRITE MARKDOWN.
DO NOT WRITE PYTHON.
DO NOT WRITE EXPLANATIONS.
DO NOT USE CODE FENCES.

You are a senior frontend engineer building a production website from a Figma scene graph.

Your job is to reconstruct the same UI but improve it for real-world web usage.

RULES:

1.  Preserve structure and hierarchy exactly.
2.  Preserve visual intent (layout, spacing, grouping, typography).
3.  Replace absolute positioning with natural document flow whenever possible.
4.  Only use absolute positioning for small decorative or overlay elements.
5.  Convert inline styles into Tailwind utility classes.
6.  Use responsive classes (w-full, max-w-7xl, mx-auto, px-6, grid, flex).
7.  Use semantic tags: header, nav, main, section, footer, article, button.
8.  Optimize for desktop, tablet, and mobile.
9.  Keep code clean and readable.
10. Preserve font family, font size, font weight, line-height, and text alignment exactly as provided in layout.style.
11. Preserve colors exactly as provided in layout.style (use exact hex or rgba values).
12. Do NOT invent or modify fonts or colors.
13. If a font family is not available by default, load it from Google Fonts using the same family name.


Preserve decorative and visual storytelling elements exactly.
Use absolute positioning only for decorative overlays such as:
- Step numbers
- Background shapes
- Floating badges

All functional layout should remain responsive.


IMAGE RULE:
If style.image == true → 
<img src="https://placehold.co/600x400?text=Image" />

OUTPUT:
ONE COMPLETE HTML DOCUMENT using Tailwind only.

INPUT:
{layout}
"""

    retries = 5
    delay = 3

    for attempt in range(retries):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash-lite", #or gemini-2.5-flash
                contents=prompt
            )

            text = _extract_text(response)

            if not text or not text.strip():
                raise ValueError("Empty model response")

            # HARD CLEAN
            text = text.strip()
            text = text.replace("```html", "").replace("```", "").strip()

            # HARD VALIDATION
            if "<html" not in text.lower():
                raise Exception("AI did not return HTML")

            return text

        except Exception as e:
            if "503" in str(e) or "UNAVAILABLE" in str(e):
                print(f"[AI] Overloaded, retrying in {delay}s... ({attempt+1}/{retries})")
                time.sleep(delay)
                delay *= 2
                continue

            raise

    raise RuntimeError("AI failed after multiple retries")
