from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from models import ConvertRequest
from Services.figma_service import get_figma_file
from Services.layout_parser import parse_figma_layout
from Services.ai_services import generate_code
from storedb import save_figma_file, get_cached_figma
import os
import zipfile
import shutil


app = FastAPI()


@app.get("/")
def root():
    return {"message": "welcome to figma to code"}


@app.post("/convert")
def convert_design(req: ConvertRequest):
    try:
        figma_url = str(req.figma_url)

        cached = get_cached_figma(figma_url, req.framework)

        if cached and cached.get("figma_json") and cached.get("parsed_layout"):
            figma_json = cached["figma_json"]
            layout = cached["parsed_layout"]
        else:
            figma_json = get_figma_file(figma_url)
            layout = parse_figma_layout(figma_json)

            save_figma_file(
                figma_url=figma_url,
                figma_json=figma_json,
                layout=layout,
                framework=req.framework
            )

        # Create temp output folder
        out_dir = "generated_site"
        if os.path.exists(out_dir):
            shutil.rmtree(out_dir)
        os.makedirs(out_dir)

        pages = layout.get("pages", [])

        if not pages:
            raise Exception("No pages found in parsed layout")

        # CORE LOOP 
        for page in pages:
            for screen in page["screens"]:
                screen_name = screen["screen"].lower().replace(" ", "_")
                filename = f"{screen_name}.html"

                print(f"[AI] Generating: {screen_name}") # debug log

                # send ONLY one screen to AI
                screen_layout = {
                    "page": page["page"],
                    "screen": screen["screen"],
                    "box": screen["box"],
                    "tree": screen["tree"]
                }

                code = generate_code(screen_layout, req.framework)

                if not code:
                    raise Exception(f"AI returned empty for {screen_name}")

                with open(os.path.join(out_dir, filename), "w", encoding="utf-8") as f:
                    f.write(code)
                
                print(f"[OK] Saved: {filename}") # debug log

        # zip everything
        zip_path = "figma_site.zip"
        if os.path.exists(zip_path):
            os.remove(zip_path)

        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(out_dir):
                for file in files:
                    zipf.write(
                        os.path.join(root, file),
                        arcname=file
                    )

        return FileResponse(zip_path, filename="figma_site.zip")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
