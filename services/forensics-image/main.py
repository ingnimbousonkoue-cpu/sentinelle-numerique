
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from tempfile import NamedTemporaryFile
import os

from exif_extractor import EXIFExtractor

app = FastAPI(
    title="Sentinelle Numérique - Forensics Image API",
    version="1.0.0"
)

extractor = EXIFExtractor()


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/analyze/exif")
async def analyze_exif(file: UploadFile = File(...)):
    allowed = ["image/jpeg", "image/png", "image/webp"]

    if file.content_type not in allowed:
        raise HTTPException(
            status_code=422,
            detail="Format image non supporté"
        )

    suffix = file.filename.split(".")[-1]

    try:
        with NamedTemporaryFile(delete=False, suffix=f".{suffix}") as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name

        result = extractor.extract(tmp_path)

        return JSONResponse(
            status_code=200,
            content=result.model_dump()
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    finally:
        if 'tmp_path' in locals() and os.path.exists(tmp_path):
            os.remove(tmp_path)
