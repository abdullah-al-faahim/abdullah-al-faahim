"""Build the README section headings in Sora, with a JetBrains Mono index.

Each heading gets a light and a dark SVG in assets/headings/, which README.md
shows through <picture> inside an <h2>. Prints the width to put on each <img>.

Run from the repository root:  python scripts/build-headings.py
"""

from pathlib import Path
from xml.sax.saxutils import escape

from brand_fonts import font_face, text_width

HEADINGS = [
    ("about", "About"),
    ("experience", "Experience"),
    ("toolbox", "Toolbox"),
    ("featured-projects", "Featured projects"),
    ("achievements", "Achievements"),
]

# Design system tokens per theme: ink for the title, accent for the index
THEMES = {
    "light": {"ink": "#1F2328", "accent": "#3A10AD"},
    "dark": {"ink": "#E6EDF3", "accent": "#B4ADFF"},
}

H = 38
TITLE = ("Sora", 600, 24)
INDEX = ("JetBrains Mono", 500, 13)
GAP = 12


def heading(number, title, theme):
    t = THEMES[theme]
    index = f"{number:02d}"
    x = round(text_width(*INDEX, index) + GAP, 1)
    w = round(x + text_width(*TITLE, title) + 2)
    style = font_face(TITLE[0], TITLE[1], title) + font_face(INDEX[0], INDEX[1], index)
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{H}" viewBox="0 0 {w} {H}" role="img" aria-label="{escape(title)}">
<title>{escape(title)}</title>
<style>{style}</style>
<text x="0" y="27" font-family="'JetBrains Mono', monospace" font-size="{INDEX[2]}" font-weight="{INDEX[1]}" fill="{t["accent"]}">{index}</text>
<text x="{x}" y="28" font-family="Sora, sans-serif" font-size="{TITLE[2]}" font-weight="{TITLE[1]}" letter-spacing="-0.3" fill="{t["ink"]}">{escape(title)}</text>
</svg>
'''
    return svg, w


def main():
    out = Path(__file__).resolve().parent.parent / "assets" / "headings"
    out.mkdir(parents=True, exist_ok=True)
    for number, (slug, title) in enumerate(HEADINGS, start=1):
        for theme in THEMES:
            svg, w = heading(number, title, theme)
            (out / f"{slug}-{theme}.svg").write_text(svg, encoding="utf-8", newline="\n")
        print(f"{slug}: width {w}")


if __name__ == "__main__":
    main()
