"""Build the Achievements tiles for the profile README.

Each earned GitHub achievement gets a light and a dark tile in
assets/achievements/, which README.md shows through <picture> and links to
its page in the github-achievements guide. Tiles are 136px wide so four fit
on one row at every desktop README width and two on phones.

Badge art is GitHub's own, kept in scripts/badges/ and embedded as a 2x PNG.
Add a badge there and an entry below when a new one is earned.

Needs Pillow:  pip install pillow
Run from the repository root:  python scripts/build-achievements.py
"""

import base64
import io
from pathlib import Path
from xml.sax.saxutils import escape

from PIL import Image

from brand_fonts import font_face, text_width

ACHIEVEMENTS = [
    {"slug": "starstruck", "badge": "starstruck-bronze", "title": "Starstruck", "tier": "×2 Bronze"},
    {"slug": "pull-shark", "badge": "pull-shark-bronze", "title": "Pull Shark", "tier": "×2 Bronze"},
    {"slug": "pair-extraordinaire", "badge": "pair-extraordinaire-default", "title": "Pair Extraordinaire", "tier": None},
    {"slug": "yolo", "badge": "yolo-default", "title": "YOLO", "tier": None},
]

# Design system tokens per theme, as on the project cards
THEMES = {
    "light": {"surface": "#F6F8FA", "border": "#D0D7DE", "ink": "#1F2328"},
    "dark": {"surface": "#161B22", "border": "#30363D", "ink": "#E6EDF3"},
}
FILL_PRIMARY = "#6B4AFF"    # brand-500, tiered badges
FILL_SECONDARY = "#6E6A86"  # neutral-500, single-level badges

W, H, BADGE = 136, 172, 88
TITLE = ("Sora", 600, 13)
LABEL = ("JetBrains Mono", 600, 10)
SPACING = 0.6


def badge_png(name):
    """The badge at 2x display size, as base64 PNG."""
    image = Image.open(Path(__file__).resolve().parent / "badges" / f"{name}.png")
    image = image.resize((BADGE * 2, BADGE * 2), Image.LANCZOS)
    out = io.BytesIO()
    image.save(out, "PNG", optimize=True)
    return base64.b64encode(out.getvalue()).decode("ascii")


def tile(achievement, theme, png):
    t = THEMES[theme]
    label = (achievement["tier"] or "Earned").upper()
    fill = FILL_PRIMARY if achievement["tier"] else FILL_SECONDARY
    pill = round(text_width(*LABEL, label, SPACING) + 14)
    title = escape(achievement["title"])
    style = font_face(*TITLE[:2], achievement["title"]) + font_face(*LABEL[:2], label)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{title}">
<title>{title}</title>
<style>{style}</style>
<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="11.5" fill="{t["surface"]}" stroke="{t["border"]}"/>
<image x="{(W - BADGE) / 2}" y="14" width="{BADGE}" height="{BADGE}" xlink:href="data:image/png;base64,{png}" href="data:image/png;base64,{png}"/>
<text x="{W / 2}" y="125" text-anchor="middle" font-family="Sora, sans-serif" font-size="{TITLE[2]}" font-weight="{TITLE[1]}" fill="{t["ink"]}">{title}</text>
<rect x="{(W - pill) / 2}" y="138" width="{pill}" height="18" fill="{fill}"/>
<text x="{W / 2 + SPACING / 2}" y="150.5" text-anchor="middle" font-family="'JetBrains Mono', monospace" font-size="{LABEL[2]}" font-weight="{LABEL[1]}" letter-spacing="{SPACING}" fill="#FFFFFF">{escape(label)}</text>
</svg>
'''


def main():
    out = Path(__file__).resolve().parent.parent / "assets" / "achievements"
    out.mkdir(parents=True, exist_ok=True)
    for achievement in ACHIEVEMENTS:
        png = badge_png(achievement["badge"])
        for theme in THEMES:
            (out / f'{achievement["slug"]}-{theme}.svg').write_text(tile(achievement, theme, png), encoding="utf-8", newline="\n")
    print(f"Wrote {len(ACHIEVEMENTS) * len(THEMES)} tiles to {out}")


if __name__ == "__main__":
    main()
