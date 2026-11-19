from fastapi import FastAPI, File, UploadFile, HTTPException

app = FastAPI(title="Plate Service")

MAX_BYTES = 8 * 1024 * 1024  # 8 MB


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/verify")
async def verify(image: UploadFile = File(...)):
    if not (image.content_type or "").startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    data = await image.read()
    if len(data) > MAX_BYTES:
        raise HTTPException(status_code=413, detail="Image too large")

    # Stub: real detection and OCR come in steps 2 to 4
    return {
        "plate": "ABC123DE",
        "confidence": 0.0,
        "status": "stub",
        "bytes_received": len(data),
    }