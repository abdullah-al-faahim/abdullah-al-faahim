"""Build bordered callout boxes for lines the README should highlight.

The box fills the README width with text at GitHub's body size (14px), so
each callout is drawn at three widths, the README width at each screen size:

- wide (840px, screens 1280px and up): light and dark files, picked by the
  <picture> color-scheme sources, so they follow the viewer's GitHub theme.
- medium (576px, screens 601-1279px) and narrow (343px, phones): one file
  each that switches light and dark inside the SVG. GitHub's themed-picture
  script rewrites any <source> whose media mentions prefers-color-scheme,
  so width sources must not mention it.

The border is Acid Lime on dark and brand-500 violet on light, where lime
would vanish.

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
WIDTHS = {"wide": 840, "medium": 576, "narrow": 343}
FONT = ("Sora", 500, 14)
LEADING, PAD_X, PAD_Y = 22, 20, 15


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


def colors(theme):
    """Fixed colors for one theme, or CSS that follows the viewer's color scheme."""
    if theme != "auto":
        t = THEMES[theme]
        return "", f'fill="{t["fill"]}" stroke="{t["border"]}"', f'fill="{t["ink"]}"'
    l, d = THEMES["light"], THEMES["dark"]
    css = (f'.box{{fill:{l["fill"]};stroke:{l["border"]}}}.ink{{fill:{l["ink"]}}}'
           f'@media (prefers-color-scheme: dark){{.box{{fill:{d["fill"]};stroke:{d["border"]}}}.ink{{fill:{d["ink"]}}}}}')
    return css, 'class="box"', 'class="ink"'


def callout(text, theme, size):
    w = WIDTHS[size]
    lines = wrap(text, w - 2 * PAD_X)
    h = 2 * PAD_Y + len(lines) * LEADING - 8
    css, box, ink = colors(theme)
    rows = "".join(
        f'<text x="{PAD_X}" y="{PAD_Y + 11 + i * LEADING}">{escape(line)}</text>' for i, line in enumerate(lines)
    )
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{escape(text)}">
<title>{escape(text)}</title>
<style>{font_face(FONT[0], FONT[1], text)}{css}</style>
<rect x="0.75" y="0.75" width="{w - 1.5}" height="{h - 1.5}" rx="8" stroke-width="1.5" {box}/>
<g font-family="Sora, sans-serif" font-size="{FONT[2]}" font-weight="{FONT[1]}" {ink}>{rows}</g>
</svg>
'''


def main():
    out = Path(__file__).resolve().parent.parent / "assets" / "callouts"
    out.mkdir(parents=True, exist_ok=True)
    for old in out.glob("*.svg"):
        old.unlink()
    for slug, text in CALLOUTS:
        files = [(f"{slug}-light-wide.svg", "light", "wide"), (f"{slug}-dark-wide.svg", "dark", "wide"),
                 (f"{slug}-medium.svg", "auto", "medium"), (f"{slug}-narrow.svg", "auto", "narrow")]
        for name, theme, size in files:
            (out / name).write_text(callout(text, theme, size), encoding="utf-8", newline="\n")
        print(slug, {size: len(wrap(text, w - 2 * PAD_X)) for size, w in WIDTHS.items()}, "lines")


if __name__ == "__main__":
    main()
