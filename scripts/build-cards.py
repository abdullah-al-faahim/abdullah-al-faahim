"""Build the Featured Projects cards for the profile README.

Each project gets a light and a dark SVG in assets/cards/, which README.md
shows through <picture> so the card follows the viewer's GitHub theme.
Colors come from the profile design system (violet scale built on #3A10AD).

Run from the repository root:  python scripts/build-cards.py
"""

from pathlib import Path
from xml.sax.saxutils import escape

PROJECTS = [
    {
        "slug": "finutopia",
        "eyebrow": "Personal finance · Android",
        "title": "FinUtopia",
        "lines": ["A private, offline money manager built for", "Bangladesh, in Bangla and English."],
        "tags": ["Android", "Offline"],
    },
    {
        "slug": "zakat-calculator-app",
        "eyebrow": "Bangla tools · Android",
        "title": "Zakat Calculator",
        "lines": ["A Bangla-first Android app for zakat, ushr", "and fitra, with Quran and hadith evidence."],
        "tags": ["Android", "Bangla"],
    },
    {
        "slug": "channel-i-mcr-leave",
        "eyebrow": "Broadcast operations · Web",
        "title": "Channel i MCR Leave Application",
        "lines": ["Leave applications for the Master Control", "Room team at Channel i."],
        "tags": ["HTML", "Internal tool"],
    },
    {
        "slug": "telecast-time-calculator",
        "eyebrow": "Broadcast operations · Android",
        "title": "Telecast Time Calculator",
        "lines": ["Add, compare and convert on-air durations.", "Works fully offline."],
        "tags": ["Android", "HTML/JS"],
    },
    {
        "slug": "windows-11-customization",
        "eyebrow": "Desktop setup · PowerShell",
        "title": "Windows 11 Customization",
        "lines": ["GlazeWM, yasb, Windhawk and Flow Launcher", "configs for a focused Windows 11 workspace."],
        "tags": ["PowerShell", "Windows"],
    },
    {
        "slug": "pantone-colorbooks",
        "eyebrow": "Design resources · Illustrator",
        "title": "PANTONE Color Books",
        "lines": ["PANTONE color book libraries for Adobe", "Illustrator 2024 and newer."],
        "tags": ["Illustrator", "Color"],
    },
    {
        "slug": "bijoy-typing-practice",
        "eyebrow": "Bangla tools · Web",
        "title": "Bijoy Bangla Typing Practice",
        "lines": ["Build speed and accuracy on the Bijoy", "Bangla keyboard layout."],
        "tags": ["HTML", "Bangla"],
    },
    {
        "slug": "electronics-circuit",
        "eyebrow": "Electronics · NI Multisim",
        "title": "Electronics Circuits Lab",
        "lines": ["23 NI Multisim projects: op-amps, flip-flops,", "logic gates, diodes and AC analysis."],
        "tags": ["Multisim", "ECE"],
    },
]

# Design system tokens per theme
THEMES = {
    "light": {
        "surface": "#F6F8FA", "border": "#D0D7DE", "ink": "#1F2328", "muted": "#59636E",
        "accent": "#3A10AD", "arc": "#E9E7FF",
    },
    "dark": {
        "surface": "#161B22", "border": "#30363D", "ink": "#E6EDF3", "muted": "#9198A1",
        "accent": "#B4ADFF", "arc": "#1E066F",
    },
}
FILL_PRIMARY = "#6B4AFF"    # brand-500, white text 5.2:1
FILL_SECONDARY = "#6E6A86"  # neutral-500, white text 5.2:1

W, H, PAD = 420, 196, 24
SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans', Helvetica, Arial, sans-serif"
BADGE = "Verdana, Geneva, 'DejaVu Sans', sans-serif"


def tag_width(label):
    return round(len(label) * 6.9 + 14)


def card(project, theme):
    t = THEMES[theme]
    tags, x = [], PAD
    for label in project["tags"]:
        w = tag_width(label)
        tags.append(
            f'<rect x="{x}" y="152" width="{w}" height="20" fill="{FILL_SECONDARY}"/>'
            f'<text x="{x + w / 2}" y="166" text-anchor="middle" font-family="{BADGE}" font-size="11" fill="#FFFFFF">{escape(label)}</text>'
        )
        x += w + 4
    lines = "".join(
        f'<text x="{PAD}" y="{102 + i * 20}" font-family="{SANS}" font-size="14" fill="{t["muted"]}">{escape(line)}</text>'
        for i, line in enumerate(project["lines"])
    )
    title = escape(project["title"])
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{title}">
<title>{title}</title>
<defs><clipPath id="c"><rect width="{W}" height="{H}" rx="12"/></clipPath></defs>
<g clip-path="url(#c)">
<rect width="{W}" height="{H}" fill="{t["surface"]}"/>
<g fill="none" stroke="{t["arc"]}" stroke-width="8"><circle cx="{W}" cy="0" r="48"/><circle cx="{W}" cy="0" r="96"/><circle cx="{W}" cy="0" r="144"/></g>
<circle cx="{W}" cy="0" r="16" fill="{t["arc"]}"/>
</g>
<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="11.5" fill="none" stroke="{t["border"]}"/>
<text x="{PAD}" y="40" font-family="{SANS}" font-size="11" font-weight="600" letter-spacing="1.2" fill="{t["accent"]}">{escape(project["eyebrow"].upper())}</text>
<text x="{PAD}" y="70" font-family="{SANS}" font-size="20" font-weight="600" fill="{t["ink"]}">{title}</text>
{lines}
{"".join(tags)}
<rect x="{W - PAD - 124}" y="148" width="124" height="28" fill="{FILL_PRIMARY}"/>
<text x="{W - PAD - 62}" y="166" text-anchor="middle" font-family="{BADGE}" font-size="10" font-weight="700" letter-spacing="1" fill="#FFFFFF">VIEW PROJECT</text>
</svg>
'''


def main():
    out = Path(__file__).resolve().parent.parent / "assets" / "cards"
    out.mkdir(parents=True, exist_ok=True)
    for project in PROJECTS:
        for theme in THEMES:
            (out / f'{project["slug"]}-{theme}.svg').write_text(card(project, theme), encoding="utf-8", newline="\n")
    print(f"Wrote {len(PROJECTS) * len(THEMES)} cards to {out}")


if __name__ == "__main__":
    main()
