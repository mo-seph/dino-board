#!/usr/bin/env python3
"""The board's shape for the web simulator: web/sim/shape.json, from dinolight.kicad_pcb and
outline/make_outline.py. Run with KiCad's Python, only when the board's shape changes:

    $KPY tools/sim_shape.py

Coordinates are the show face in mm (head left, y down): x = 240 - board X, y = board Y - 10."""
import json, math, os, sys
import pcbnew

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'outline'))
import make_outline as mo

mm = pcbnew.ToMM
show = lambda p: (round(240 - mm(p.x), 2), round(mm(p.y) - 10, 2))


def simplify(pts, tol):
    """Douglas-Peucker on a closed ring."""
    def dp(seg):
        if len(seg) < 3:
            return seg
        (x0, y0), (x1, y1) = seg[0], seg[-1]
        L = math.hypot(x1 - x0, y1 - y0) or 1e-9
        far, at = 0.0, 0
        for i in range(1, len(seg) - 1):
            d = abs((x1 - x0) * (y0 - seg[i][1]) - (x0 - seg[i][0]) * (y1 - y0)) / L
            if d > far:
                far, at = d, i
        return dp(seg[:at + 1])[:-1] + dp(seg[at:]) if far > tol else [seg[0], seg[-1]]
    half = len(pts) // 2
    return dp(pts[:half + 1])[:-1] + dp(pts[half:] + pts[:1])[:-1]


board = pcbnew.LoadBoard(os.path.join(ROOT, 'dinolight.kicad_pcb'))
NAMES = {'PAD_SNOUT': 'snout', 'PAD_TAIL': 'tail', 'PAD_FLIP_F': 'front_flipper', 'PAD_FLIP_R': 'rear_flipper'}
pads, spine = {}, {}
for d in board.GetDrawings():
    if d.GetClass() != 'PCB_SHAPE' or d.GetLayer() != pcbnew.B_Cu or not d.GetNetname().startswith('PAD_'):
        continue
    poly = d.GetPolyShape()
    for k in range(poly.OutlineCount()):
        ring = poly.Outline(k)
        pts = simplify([show(ring.CPoint(i)) for i in range(ring.PointCount())], 0.12)
        net = d.GetNetname()
        if net in NAMES:
            pads.setdefault(NAMES[net], []).append(pts)
        elif net.startswith('PAD_SPINE'):
            spine.setdefault(int(net[9:]), []).append(pts)
leds = []
for n in range(1, 19):
    f = board.FindFootprintByReference('D%d' % n)
    leds.append(list(show(f.GetPosition())))
eye = list(show(board.FindFootprintByReference('D21').GetPosition()))
out = {
    'outline': [[round(x, 2), round(y, 2)] for x, y in simplify(mo.OUTLINE, 0.05)],
    'leds': leds, 'eye': eye,
    'pads': pads,
    'spine': [spine[i] for i in sorted(spine)],
}
path = os.path.join(ROOT, 'web', 'sim', 'shape.json')
json.dump(out, open(path, 'w'), separators=(',', ':'))
count = lambda rings: sum(len(r) for r in rings)
print('outline %d points; LEDs %d, first %s last %s; eye %s; pads %s; spine %s; %d bytes'
      % (len(out['outline']), len(leds), leds[0], leds[-1], eye, {k: count(v) for k, v in pads.items()},
         [count(v) for v in out['spine']], os.path.getsize(path)))
