import sys

import cv2


def variants(crop):
    # make small plates bigger; OCR reads characters better at ~100+ px height
    h, w = crop.shape[:2]
    if h < 100:
        scale = 100 / h
        crop = cv2.resize(crop, (int(w * scale), 100), interpolation=cv2.INTER_CUBIC)

    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)

    # even out lighting and boost contrast
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(gray)

    # pure black and white
    _, thresh = cv2.threshold(clahe, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    return {"original": crop, "gray": gray, "clahe": clahe, "thresh": thresh}


if __name__ == "__main__":
    img = cv2.imread(sys.argv[1])
    for name, v in variants(img).items():
        cv2.imwrite(f"prep_{name}.jpg", v)
        print("saved", f"prep_{name}.jpg")