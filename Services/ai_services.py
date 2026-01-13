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
You are a senior frontend engineer converting a Figma-derived design schema
into a high-fidelity, production-ready HTML + Tailwind UI.

The input is NOT raw Figma — it is a cleaned, hierarchical layout extracted
from Figma.

Your job is to:
- Preserve section hierarchy
- Preserve visual intent
- Preserve component grouping
- Match spacing, typography, and layout density as closely as possible

You are allowed to:
- Use flexbox, grid, and modern layout systems
- Improve alignment where raw pixel data is messy
- Convert rigid Figma coordinates into real web layout

=========================
OUTPUT RULES
=========================
- Output a single complete HTML document
- Use Tailwind CDN
- No JavaScript
- No explanations
- No markdown outside code
- Use semantic HTML

The document MUST include:
<!DOCTYPE html>
<html>
<head>
<body>

=========================
DESIGN FIDELITY
=========================
- Respect typography hierarchy (headers, body, labels, prices)
- Respect grouping (navbars, cards, product tiles, grids, forms)
- Respect spacing (ecommerce layouts are dense but structured)
- Use Tailwind utility classes for everything
- Use realistic ecommerce / SaaS patterns

Do NOT collapse everything into one column.
Do NOT ignore sections or screens.

=========================
MULTI-SCREEN HANDLING
=========================
If multiple screens exist in the input:
- Render each as a full page section stacked vertically
- Wrap each with:

<!-- SCREEN: Screen Name -->
<section>...</section>

=========================
IMAGES
=========================
Use placeholders for images:
<img src="https://placehold.co/600x400?text=Image" />

=========================
INPUT DESIGN SCHEMA
=========================
{layout}
"""

    retries = 5
    delay = 3

    for attempt in range(retries):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash", # or other available model
                contents=prompt
            )

            text = _extract_text(response)

            if not text or not text.strip():
                raise ValueError("Empty model response")

            return text

        except Exception as e:
            if "503" in str(e) or "UNAVAILABLE" in str(e):
                print(f"[AI] Overloaded, retrying in {delay}s... ({attempt+1}/{retries})")
                time.sleep(delay)
                delay *= 2   # exponential backoff
                continue

            raise

    raise RuntimeError("AI failed after multiple retries")
