import sys
from pathlib import Path

import cv2
from ultralytics import YOLO

WEIGHTS = "models/plate_detector/best.pt"  # change to the path find printed

model = YOLO(WEIGHTS)


def detect_plates(img, conf=0.25, pad=0.05):
    h, w = img.shape[:2]
    result = model.predict(img, conf=conf, device="mps", verbose=False)[0]

    plates = []
    for box in result.boxes:
        x1, y1, x2, y2 = box.xyxy[0].tolist()
        score = float(box.conf[0])

        # small padding so characters at the edges aren't cut off
        pw, ph = (x2 - x1) * pad, (y2 - y1) * pad
        x1, y1 = max(0, int(x1 - pw)), max(0, int(y1 - ph))
        x2, y2 = min(w, int(x2 + pw)), min(h, int(y2 + ph))

        plates.append({
            "box": [x1, y1, x2, y2],
            "score": score,
            "crop": img[y1:y2, x1:x2],
        })
    return plates


if __name__ == "__main__":
    src = Path(sys.argv[1])
    img = cv2.imread(str(src))
    found = detect_plates(img)
    print(f"{len(found)} plate(s) found")
    for i, p in enumerate(found):
        out = f"crop_{i}.jpg"
        cv2.imwrite(out, p["crop"])
        print(i, p["box"], round(p["score"], 2), "->", out)