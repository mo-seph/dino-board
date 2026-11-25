#!/usr/bin/env python3
"""Letter outlines for the show-face silkscreen, from a font file, as plain polygons: art/lettering.json.
KiCad's Python cannot be handed a font, so the outlines are made here once (needs matplotlib) and
tools/silkscreen.py only reads the JSON. Run again only to change the words or the font.

    python3 tools/title_outline.py ["Title"] [font file]

Each entry is {"contours": [[[x, y], ...], ...], "w": width, "h": height of a capital}: y up, the
baseline at 0, the left edge at 0, in units where the font's capital letters are 1 high. Contours are
even-odd: a letter's counter (the hole in an "o") is a contour inside another."""
import json, os, sys
from matplotlib.textpath import TextPath
from matplotlib.font_manager import FontProperties

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TITLE = sys.argv[1] if len(sys.argv) > 1 else 'Mosasauraboard'
FONT = sys.argv[2] if len(sys.argv) > 2 else '/System/Library/Fonts/Supplemental/Arial Rounded Bold.ttf'
prop = FontProperties(fname=FONT)


def outline(text, cap):
    polys = TextPath((0, 0), text, size=100, prop=prop).to_polygons(closed_only=True)
    x0 = min(p[:, 0].min() for p in polys)
    return {'contours': [[[round((x - x0) / cap, 4), round(y / cap, 4)] for x, y in p] for p in polys],
            'w': round((max(p[:, 0].max() for p in polys) - x0) / cap, 4)}


cap = max(p[:, 1].max() for p in TextPath((0, 0), 'H', size=100, prop=prop).to_polygons())
out = {'font': os.path.basename(FONT), 'title': dict(outline(TITLE, cap), text=TITLE),
       'numbers': {str(n): outline(str(n), cap) for n in range(1, 31)}}
os.makedirs(os.path.join(ROOT, 'art'), exist_ok=True)
json.dump(out, open(os.path.join(ROOT, 'art', 'lettering.json'), 'w'))
print('%s in %s: %.2f capital heights wide, %d contours' % (TITLE, out['font'], out['title']['w'], len(out['title']['contours'])))
