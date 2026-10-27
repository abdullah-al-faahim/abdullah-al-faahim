"""Keep the years of brand identity work in README.md current.

Counts whole calendar years since START_YEAR and rewrites every place the
README shows that number. Run by .github/workflows/years.yml on the first of
each month; it only changes the file when the number has gone up.

Run from the repository root:  python scripts/update-years.py
"""

import re
from datetime import date
from pathlib import Path

START_YEAR = 2018

README = Path(__file__).resolve().parent.parent / "README.md"

years = date.today().year - START_YEAR

PATTERNS = [
    # Plain text: <!--years-->8<!--/years-->
    (r"(<!--years-->)\d+(<!--/years-->)", rf"\g<1>{years}\g<2>"),
    # Typing intro line, URL-encoded: Brand+Identity+Designer+%C2%B7+8+years
    (r"(Brand\+Identity\+Designer\+%C2%B7\+)\d+(\+years)", rf"\g<1>{years}\g<2>"),
    # Typing intro alt text: Brand Identity Designer, 8 years.
    (r"(Brand Identity Designer, )\d+( years)", rf"\g<1>{years}\g<2>"),
]


def main():
    text = README.read_text(encoding="utf-8")
    updated = text
    for pattern, replacement in PATTERNS:
        updated = re.sub(pattern, replacement, updated)
    if updated == text:
        print(f"README already shows {years} years.")
        return
    README.write_text(updated, encoding="utf-8", newline="\n")
    print(f"README updated to {years} years.")


if __name__ == "__main__":
    main()
