"""Build the Achievements tiles for the profile README, straight from GitHub.

GitHub has no API for achievements, so this reads the public achievements tab
(github.com/abdullah-al-faahim?tab=achievements), works out every badge and its
tier (x2 Bronze, x3 Silver, x4 Gold) and saves the list to
scripts/achievements.json. New badge art is downloaded into scripts/badges/.
Each achievement then gets a light and a dark tile in assets/achievements/,
and the Achievements block in README.md is rewritten to match. Tiles are
136px wide so four fit on one row at every desktop README width and two on
phones.

If GitHub can't be reached, the last saved list is used, so nothing is lost.
The "Sync GitHub achievements" workflow runs this every day.

Needs Pillow:  pip install pillow
Run from the repository root:  python scripts/build-achievements.py
  --force    rebuild tiles even if nothing changed
  --offline  rebuild from scripts/achievements.json without asking GitHub
"""

import base64
import io
import json
import re
import sys
import urllib.request
from pathlib import Path
from xml.sax.saxutils import escape

from PIL import Image

from brand_fonts import font_face, text_width

USER = "abdullah-al-faahim"
GUIDE = "https://github.com/abdullah-al-faahim/github-achievements/blob/main/achievements/{slug}.md"
UA = {"User-Agent": "Mozilla/5.0 (achievement sync)"}
TIER_NAMES = {2: "Bronze", 3: "Silver", 4: "Gold"}
HERE = Path(__file__).resolve().parent
DATA = HERE / "achievements.json"

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


def _get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
        return r.read()


def fetch():
    """Achievements from the public profile tab, tiered ones first."""
    page = _get(f"https://github.com/{USER}?tab=achievements").decode("utf-8", "replace")
    found, order = {}, []
    for chunk in page.split('data-achievement-slug="')[1:]:
        slug = chunk.split('"', 1)[0]
        if slug in found or not re.fullmatch(r"[a-z0-9-]+", slug):
            continue
        title = re.search(r'alt="Achievement: ([^"]+)"', chunk)
        img = re.search(r'src="(https://github\.githubassets\.com/assets/([a-z0-9-]+?)-[0-9a-f]{8,}\.png)"', chunk)
        if not (title and img):
            continue
        tier = re.search(r'achievement-tier-label--(\w+)[^>]*>\s*x(\d+)\s*<', chunk)
        count = int(tier.group(2)) if tier else 1
        name = (TIER_NAMES.get(count) or tier.group(1).title()) if tier else None
        badge = HERE / "badges" / f"{img.group(2)}.png"
        if not badge.exists():
            badge.write_bytes(_get(img.group(1)))
            print("New badge art:", badge.name)
        found[slug] = {
            "slug": slug,
            "badge": img.group(2),
            "title": title.group(1).replace("&amp;", "&"),
            "count": count,
            "tier": f"×{count} {name}" if name else None,
        }
        order.append(slug)
    return sorted((found[s] for s in order), key=lambda a: -a["count"])


def load_achievements(offline=False):
    """(achievements, changed): the live list, or the saved one if GitHub fails."""
    saved = json.loads(DATA.read_text(encoding="utf-8")) if DATA.exists() else None
    if not offline:
        try:
            items = fetch()
            if items:
                if items != saved:
                    DATA.write_text(json.dumps(items, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
                return items, items != saved
            print("No achievements found on the page; using the saved list.")
        except Exception as e:
            print("Could not read GitHub achievements, using the saved list:", e)
    return saved, False


def badge_png(name):
    """The badge at 2x display size, as base64 PNG."""
    image = Image.open(HERE / "badges" / f"{name}.png")
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


def readme_block(items):
    rows = []
    for a in items:
        tier = a["tier"].replace("×", "x").replace(" ", ", ", 1) if a["tier"] else "earned"
        alt = escape(f'{a["title"]} achievement, {tier}', {'"': "&quot;"})
        rows.append(
            f'  <a href="{GUIDE.format(slug=a["slug"])}"><picture>'
            f'<source media="(prefers-color-scheme: dark)" srcset="assets/achievements/{a["slug"]}-dark.svg" />'
            f'<img src="assets/achievements/{a["slug"]}-light.svg" width="136" alt="{alt}" title="{escape(a["title"])}" />'
            f'</picture></a>'
        )
    return "\n".join(rows)


def main():
    items, changed = load_achievements(offline="--offline" in sys.argv)
    root = HERE.parent
    out = root / "assets" / "achievements"
    # Tiles embed font subsets whose bytes differ run to run, so only rebuild
    # when a badge was earned or upgraded (or with --offline / --force)
    tiles_exist = all((out / f'{a["slug"]}-light.svg').exists() for a in items)
    if not changed and tiles_exist and "--force" not in sys.argv and "--offline" not in sys.argv:
        print("No change:", ", ".join(f'{a["title"]} ({a["tier"] or "earned"})' for a in items))
        return
    out.mkdir(parents=True, exist_ok=True)
    for achievement in items:
        png = badge_png(achievement["badge"])
        for theme in THEMES:
            (out / f'{achievement["slug"]}-{theme}.svg').write_text(tile(achievement, theme, png), encoding="utf-8", newline="\n")
    print(f"Wrote {len(items) * len(THEMES)} tiles to {out}")

    readme = root / "README.md"
    text = readme.read_text(encoding="utf-8")
    block = re.compile(r'(alt="Achievements" /></picture></h2>\s*<p align="center">\n).*?(\n</p>)', re.S)
    new = block.sub(lambda m: m.group(1) + readme_block(items) + m.group(2), text, count=1)
    if new != text:
        readme.write_text(new, encoding="utf-8", newline="\n")
        print("README achievements updated")
    print(", ".join(f'{a["title"]} ({a["tier"] or "earned"})' for a in items))


if __name__ == "__main__":
    main()
