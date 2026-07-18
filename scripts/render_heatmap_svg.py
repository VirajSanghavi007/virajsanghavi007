import json
import os
from datetime import datetime, timedelta

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "contributions.json")
OUT_PATH = os.path.join(os.path.dirname(__file__), "..", "contrib-heatmap.svg")

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]

BOX = 11
GAP = 3
LEFT_PAD = 30
TOP_PAD = 26
BOTTOM_PAD = 46
WEEKS = 53
DAYS = 7

WIDTH = LEFT_PAD + WEEKS * (BOX + GAP)
HEIGHT = TOP_PAD + DAYS * (BOX + GAP) + BOTTOM_PAD


def load_data():
    with open(DATA_PATH, encoding="utf-8") as f:
        return json.load(f)


def level_color(level):
    level = max(0, min(level, len(PALETTE) - 1))
    return PALETTE[level]


def build_grid(days):
    by_date = {d["date"]: d for d in days}
    last_date = datetime.strptime(days[-1]["date"], "%Y-%m-%d").date()
    start = last_date - timedelta(days=WEEKS * 7 - 1)
    start -= timedelta(days=(start.weekday() + 1) % 7)  # align to Sunday

    grid = []
    cursor = start
    for week in range(WEEKS):
        col = []
        for dow in range(DAYS):
            key = cursor.strftime("%Y-%m-%d")
            entry = by_date.get(key, {"count": 0, "level": 0})
            col.append((cursor, entry["count"], entry["level"]))
            cursor += timedelta(days=1)
        grid.append(col)
    return grid


def render(payload):
    days = payload["days"]
    stats = payload.get("stats", {})
    grid = build_grid(days)

    boxes = []
    delay_step = 0.008
    idx = 0
    for week, col in enumerate(grid):
        for dow, (day, count, level) in enumerate(col):
            x = LEFT_PAD + week * (BOX + GAP)
            y = TOP_PAD + dow * (BOX + GAP)
            color = level_color(level)
            delay = idx * delay_step
            title = f"{day.isoformat()} • {count} contribution{'s' if count != 1 else ''}"
            boxes.append(
                f'<rect class="cell" x="{x}" y="{y}" width="{BOX}" height="{BOX}" '
                f'rx="2" ry="2" fill="{color}" style="animation-delay:{delay:.3f}s">'
                f'<title>{title}</title></rect>'
            )
            idx += 1

    total = stats.get("total", sum(d["count"] for d in days))
    streak = stats.get("current_streak", 0)
    longest = stats.get("longest_streak", 0)

    legend_x = WIDTH - LEFT_PAD - (len(PALETTE) * (BOX + 4)) - 40
    legend_y = HEIGHT - BOTTOM_PAD + 22
    legend_boxes = "".join(
        f'<rect x="{legend_x + 34 + i * (BOX + 4)}" y="{legend_y - BOX + 3}" '
        f'width="{BOX}" height="{BOX}" rx="2" fill="{c}"/>'
        for i, c in enumerate(PALETTE)
    )

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}"
     viewBox="0 0 {WIDTH} {HEIGHT}" font-family="Consolas, Menlo, monospace">
  <style>
    .cell {{
      opacity: 0;
      transform: translate(-6px, -6px);
      animation: cellIn 0.35s ease-out forwards;
    }}
    @keyframes cellIn {{
      from {{ opacity: 0; transform: translate(-6px, -6px); }}
      to   {{ opacity: 1; transform: translate(0, 0); }}
    }}
    .label {{ fill: #8b949e; font-size: 11px; }}
    .stat  {{ fill: #c9d1d9; font-size: 12px; }}
  </style>
  <rect width="{WIDTH}" height="{HEIGHT}" fill="#0d1117"/>
  <text x="{LEFT_PAD}" y="16" class="label">{total} contributions in the last year</text>
  {''.join(boxes)}
  <text x="{legend_x}" y="{legend_y + 3}" class="label">Less</text>
  {legend_boxes}
  <text x="{legend_x + 34 + len(PALETTE) * (BOX + 4) + 6}" y="{legend_y + 3}" class="label">More</text>
  <text x="{LEFT_PAD}" y="{HEIGHT - 10}" class="stat">current streak: {streak}d &#8226; longest streak: {longest}d</text>
</svg>"""
    return svg


def main():
    payload = load_data()
    svg = render(payload)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
