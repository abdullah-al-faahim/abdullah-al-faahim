"""Embed the profile's brand fonts in SVG images.

GitHub strips CSS from README files, so Sora and JetBrains Mono can only
appear inside images. Each SVG carries its own @font-face: the variable font
pinned to one weight and cut down to the characters that SVG uses, as a
base64 WOFF. Fonts are in scripts/fonts/ under the SIL Open Font License.

Needs fontTools:  pip install fonttools
"""

import base64
import io
from functools import lru_cache
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

FONTS = Path(__file__).resolve().parent / "fonts"
FILES = {"Sora": "Sora-Variable.ttf", "JetBrains Mono": "JetBrainsMono-Variable.ttf"}


@lru_cache(maxsize=None)
def _static(family, weight):
    font = TTFont(FONTS / FILES[family])
    return instancer.instantiateVariableFont(font, {"wght": weight})


def text_width(family, weight, size, text, letter_spacing=0.0):
    """Advance width of text in px, including letter-spacing after each character."""
    font = _static(family, weight)
    cmap, hmtx = font.getBestCmap(), font["hmtx"]
    units = sum(hmtx[cmap[ord(ch)]][0] for ch in text)
    return units * size / font["head"].unitsPerEm + letter_spacing * len(text)


def font_face(family, weight, text):
    """An @font-face rule holding only the glyphs needed for text."""
    font = TTFont(io.BytesIO(_bytes(family, weight)))
    options = subset.Options()
    options.flavor = "woff"
    options.layout_features = ["kern", "liga"]
    options.name_IDs = []
    options.notdef_outline = True
    subsetter = subset.Subsetter(options)
    subsetter.populate(text="".join(sorted(set(text + " "))))
    subsetter.subset(font)
    out = io.BytesIO()
    font.flavor = "woff"
    font.save(out)
    data = base64.b64encode(out.getvalue()).decode("ascii")
    return (f"@font-face{{font-family:'{family}';font-weight:{weight};"
            f"src:url(data:font/woff;base64,{data}) format('woff')}}")


@lru_cache(maxsize=None)
def _bytes(family, weight):
    out = io.BytesIO()
    _static(family, weight).save(out)
    return out.getvalue()
