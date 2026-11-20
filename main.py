import base64

import cv2
import numpy as np
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import db
from detect import detect_plates
from ocr import read_plate
from plates import nearest, normalize, resolve

MAX_BYTES = 8 * 1024 * 1024

app = FastAPI(title="Plate Service")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)
db.init()


class PlateIn(BaseModel):
    plate: str
    label: str = ""


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/plates")
def list_plates():
    return db.all_plates()


@app.post("/plates", status_code=201)
def add_plate(body: PlateIn):
    plate = normalize(body.plate)
    if not plate:
        raise HTTPException(400, "Plate is empty")
    row = db.add(plate, body.label.strip())
    if row is None:
        raise HTTPException(409, "Plate already saved")
    return row


@app.delete("/plates/{plate_id}")
def delete_plate(plate_id: int):
    if not db.remove(plate_id):
        raise HTTPException(404, "Not found")
    return {"deleted": plate_id}


@app.post("/verify")
async def verify(image: UploadFile = File(...)):
    if not (image.content_type or "").startswith("image/"):
        raise HTTPException(400, "File must be an image")
    data = await image.read()
    if len(data) > MAX_BYTES:
        raise HTTPException(413, "Image too large")

    img = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
    if img is None:
        raise HTTPException(400, "Could not decode image")

    found = detect_plates(img)
    if not found:
        return {"status": "no_plate"}

    best = max(found, key=lambda p: p["score"])
    readings = read_plate(best["crop"])
    if not readings:
        return {"status": "no_text", "box": best["box"]}

    top = readings[0]
    plate, fmt, corrected = resolve(top["text"])

    ok, buf = cv2.imencode(".jpg", best["crop"])
    crop = "data:image/jpeg;base64," + base64.b64encode(buf).decode()

    saved = db.find(plate)
    near = None
    if saved:
        status = "match"
    else:
        near = nearest(plate, db.all_plates())
        status = "possible_match" if near else "not_registered"

    return {
        "status": status,
        "plate": plate,
        "raw_text": top["text"],
        "corrected": corrected,
        "format": fmt,
        "valid_format": fmt is not None,
        "ocr_confidence": top["confidence"],
        "detection_score": round(best["score"], 3),
        "match": saved or near,
        "crop": crop,
    }