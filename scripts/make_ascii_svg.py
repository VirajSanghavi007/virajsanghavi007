import os

from PIL import Image

SRC_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "source-prepped.png")
OUT_PATH = os.path.join(os.path.dirname(__file__), "..", "avi-ascii.svg")

RAMP = " .`:-=+*cs#%@"  # bright (sparse) -> dark (dense); leading space = blank

COLS = 100
ROWS = 53
CELL_W = 6.2
CELL_H = 11
FILL = "#8b949e"


def to_grid(img):
    img = img.convert("L").resize((COLS, ROWS))
    px = img.load()
    grid = []
    n = len(RAMP) - 1
    for y in range(ROWS):
        row = []
        for x in range(COLS):
            brightness = px[x, y] / 255.0
            idx = int((1 - brightness) * n)
            row.append(RAMP[max(0, min(idx, n))])
        grid.append("".join(row))
    return grid


def render(grid):
    width = COLS * CELL_W
    height = ROWS * CELL_H

    rows_svg = []
    row_delay_step = 0.05
    for y, row in enumerate(grid):
        text = row.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        delay = y * row_delay_step
        clip_id = f"clip{y}"
        rows_svg.append(
            f'<clipPath id="{clip_id}">'
            f'<rect class="wipe" x="0" y="{y * CELL_H}" width="0" height="{CELL_H}" '
            f'style="animation-delay:{delay:.2f}s"/></clipPath>'
            f'<text x="0" y="{(y + 1) * CELL_H - 2}" clip-path="url(#{clip_id})" '
            f'fill="{FILL}" font-family="Consolas, Menlo, monospace" '
            f'font-size="{CELL_H - 1}px" xml:space="preserve">{text}</text>'
        )

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}"
     viewBox="0 0 {width} {height}">
  <style>
    .wipe {{ animation: wipeIn 0.6s steps(30) forwards; }}
    @keyframes wipeIn {{ to {{ width: {width}px; }} }}
  </style>
  <rect width="{width}" height="{height}" fill="none"/>
  {''.join(rows_svg)}
</svg>"""
    return svg


def main():
    if not os.path.exists(SRC_PATH):
        raise SystemExit(f"missing {SRC_PATH} — run prep_photo.py first")
    img = Image.open(SRC_PATH)
    grid = to_grid(img)
    svg = render(grid)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
