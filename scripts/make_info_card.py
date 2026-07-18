import os

OUT_PATH = os.path.join(os.path.dirname(__file__), "..", "info-card.svg")

# Edit these to taste.
ROWS = [
    ("os", "Windows 11"),
    ("now", "AI cash-flow forecasting @ SPD Constructions"),
    ("prev", "internship / software eng."),
    ("stack", "Python, Flask, PostgreSQL, Chronos-2"),
    ("editor", "Claude Code"),
    ("highlights", "shipped Chronos-2 forecasting pipeline"),
]

WIDTH = 490
HEIGHT = 44 + len(ROWS) * 26 + 20
BG = "#0d1117"
TITLEBAR = "#161b22"
KEY_COLOR = "#39d353"
VAL_COLOR = "#c9d1d9"
BORDER = "#30363d"

STATIC = os.environ.get("STATIC") == "1"


def render():
    rows_svg = []
    for i, (key, val) in enumerate(ROWS):
        y = 60 + i * 26
        delay = 0 if STATIC else i * 0.12
        cls = "" if STATIC else 'class="line"'
        style = "" if STATIC else f'style="animation-delay:{delay:.2f}s"'
        rows_svg.append(
            f'<g {cls} {style}>'
            f'<text x="26" y="{y}" fill="{KEY_COLOR}" font-weight="600">{key}</text>'
            f'<text x="140" y="{y}" fill="{VAL_COLOR}">{val}</text>'
            f'</g>'
        )

    anim_css = ""
    if not STATIC:
        anim_css = """
    .line { opacity: 0; transform: translateX(-8px); animation: lineIn 0.4s ease-out forwards; }
    @keyframes lineIn { to { opacity: 1; transform: translateX(0); } }
        """

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}"
     viewBox="0 0 {WIDTH} {HEIGHT}" font-family="Consolas, Menlo, monospace" font-size="13">
  <style>{anim_css}</style>
  <rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{HEIGHT - 1}" rx="8" ry="8"
        fill="{BG}" stroke="{BORDER}"/>
  <rect x="0.5" y="0.5" width="{WIDTH - 1}" height="30" rx="8" ry="8" fill="{TITLEBAR}"/>
  <rect x="0.5" y="22" width="{WIDTH - 1}" height="8" fill="{TITLEBAR}"/>
  <circle cx="20" cy="15" r="5" fill="#ff5f56"/>
  <circle cx="38" cy="15" r="5" fill="#ffbd2e"/>
  <circle cx="56" cy="15" r="5" fill="#27c93f"/>
  <text x="{WIDTH / 2}" y="19" fill="#8b949e" text-anchor="middle" font-size="11">neofetch</text>
  {''.join(rows_svg)}
</svg>"""
    return svg


def main():
    svg = render()
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
