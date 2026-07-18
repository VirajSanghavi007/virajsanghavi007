import sys
import os

import numpy as np
import cv2
from PIL import Image
from rembg import remove

OUT_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "source-prepped.png")


def main():
    if len(sys.argv) < 2:
        print("usage: python prep_photo.py <source-photo.jpg>", file=sys.stderr)
        sys.exit(1)

    src_path = sys.argv[1]
    with open(src_path, "rb") as f:
        input_bytes = f.read()

    cutout = remove(input_bytes)
    img = Image.open(__import__("io").BytesIO(cutout)).convert("RGBA")

    bg = Image.new("RGBA", img.size, (255, 255, 255, 255))
    bg.paste(img, (0, 0), img)
    flat = bg.convert("L")

    arr = np.array(flat)
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    arr = clahe.apply(arr)

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    Image.fromarray(arr).save(OUT_PATH)
    print(f"wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
