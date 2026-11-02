"""Build bordered callout boxes for lines the README should highlight.

Each callout gets four SVGs in assets/callouts/: light and dark, each in a
wide version and a narrow one for phones, so the text stays 20px on any
screen. README.md picks one through <picture> media queries. The border is
Acid Lime on dark and brand-500 violet on light, where lime would vanish.

Run from the repository root:  python scripts/build-callouts.py
"""

from pathlib import Path
from xml.sax.saxutils import escape

from brand_fonts import font_face, text_width

CALLOUTS = [
    ("also", "I also write technical documentation, run training sessions, and plan events across teams."),
]

THEMES = {
    "light": {"fill": "#F3F2FF", "border": "#6B4AFF", "ink": "#1F2328"},  # brand-50, brand-500
    "dark": {"fill": "#161B22", "border": "#D4FF24", "ink": "#E6EDF3"},   # surface, highlight-500
}
SIZES = {"wide": (560, 24), "narrow": (340, 20)}  # box width, side padding
FONT = ("Sora", 500, 20)
LEADING = 30


def wrap(text, width):
    lines, line = [], ""
    for word in text.split():
        trial = f"{line} {word}".strip()
        if line and text_width(*FONT, trial) > width:
            lines.append(line)
            line = word
        else:
            line = trial
    return lines + [line]


def callout(text, theme, size):
    t = THEMES[theme]
    w, pad = SIZES[size]
    lines = wrap(text, w - 2 * pad)
    h = 2 * pad + len(lines) * LEADING - 6
    rows = "".join(
        f'<text x="{pad}" y="{pad + 20 + i * LEADING}">{escape(line)}</text>' for i, line in enumerate(lines)
    )
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{escape(text)}">
<title>{escape(text)}</title>
<style>{font_face(FONT[0], FONT[1], text)}</style>
<rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="12" fill="{t["fill"]}" stroke="{t["border"]}" stroke-width="2"/>
<g font-family="Sora, sans-serif" font-size="{FONT[2]}" font-weight="{FONT[1]}" fill="{t["ink"]}">{rows}</g>
</svg>
'''


def main():
    out = Path(__file__).resolve().parent.parent / "assets" / "callouts"
    out.mkdir(parents=True, exist_ok=True)
    for slug, text in CALLOUTS:
        for theme in THEMES:
            for size in SIZES:
                (out / f"{slug}-{theme}-{size}.svg").write_text(callout(text, theme, size), encoding="utf-8", newline="\n")
        print(f"{slug}: wide {len(wrap(text, SIZES['wide'][0] - 2 * SIZES['wide'][1]))} lines, "
              f"narrow {len(wrap(text, SIZES['narrow'][0] - 2 * SIZES['narrow'][1]))} lines")


if __name__ == "__main__":
    main()
