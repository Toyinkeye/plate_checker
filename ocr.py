import sys

import cv2
import easyocr

from preprocess import variants

# English only, and restricted to the characters that can appear on a plate
ALLOWED = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
reader = easyocr.Reader(["en"], gpu=False)  # first run downloads the model


def read_plate(crop):
    """Try each cleanup variant and return all readings, best first."""
    readings = []
    for name, img in variants(crop).items():
        results = reader.readtext(img, allowlist=ALLOWED, detail=1, paragraph=False)
        if not results:
            continue
        # join pieces left to right (some plates get split into two chunks)
        results.sort(key=lambda r: r[0][0][0])
        text = "".join(r[1] for r in results).upper()
        conf = sum(r[2] for r in results) / len(results)
        readings.append({"variant": name, "text": text, "confidence": round(conf, 3)})
    return sorted(readings, key=lambda r: r["confidence"], reverse=True)


if __name__ == "__main__":
    crop = cv2.imread(sys.argv[1])
    for r in read_plate(crop):
        print(f'{r["variant"]:10} {r["text"]:12} {r["confidence"]}')