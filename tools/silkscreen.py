#!/usr/bin/env python3
"""The show-face (back) silkscreen of dinolight.kicad_pcb: a line drawing of the mosasaurus, an outline round
every touch pad, a number by each spine LED (1 at the head, the order firmware addresses them in), and the
name in large letters. Run with KiCad's Python, after the board is routed and poured:

    $KPY tools/silkscreen.py              white board, the drawing left as bare solder mask ("reversed")
    $KPY tools/silkscreen.py lines        the drawing in white on the bare board
    $KPY tools/silkscreen.py lines look   only the picture of that style, the board is not touched

It replaces every board-level item on B.Silkscreen, adds the cell-polarity marks and instructions to the
parts side (FRONT below), leaves everything else alone, and writes
output/show_face_art.svg (and .png if rsvg-convert is there) to look at; with "look" the picture is
output/show_face_art_<style>.svg instead. The letters come from
art/lettering.json (tools/title_outline.py). All positions below are show-face millimetres: head left,
y down, as in outline/make_outline.py.

JLCPCB's limits for silkscreen (its capabilities page, "Legend", read 2026-11-24): lines 0.15 mm or wider,
text 1.0 mm or taller, 0.15 mm between silkscreen and a pad; "hollow-carved" lettering is a listed feature.
Here nothing printed and nothing left bare is narrower than MIN_INK / MIN_GAP.
"""
import json, math, os, subprocess, sys
import pcbnew

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'outline'))
import make_outline as mo

PCB = os.path.join(ROOT, 'dinolight.kicad_pcb')
MIRROR, YOFF = 240.0, 10.0
STYLE = sys.argv[1] if len(sys.argv) > 1 else 'reversed'
LOOK = 'look' in sys.argv[2:]
RIM = 0.5            # bare margin inside the board edge
LINE = 0.4           # the drawing's line
RING = (-0.15, 0.25) # a touch pad's outline: from this far inside the edge of its copper to this far outside, so the
                     # gap between two slider electrodes and the line each side of it print as one line
NUM_H, TITLE_H = 2.2, 9.3
MIN_INK, MIN_GAP = 0.2, 0.25
LAYER = pcbnew.B_SilkS
mm = pcbnew.FromMM
ERR = mm(0.005)


def B(x, y):
    return mm(MIRROR - x), mm(y + YOFF)


def poly(points):
    ch = pcbnew.SHAPE_LINE_CHAIN()
    for p in points:
        ch.Append(*B(*p))
    ch.SetClosed(True)
    ps = pcbnew.SHAPE_POLY_SET()
    ps.AddOutline(ch)
    return ps


def grow(ps, d):
    out = pcbnew.SHAPE_POLY_SET(ps)
    if d > 0:
        out.Inflate(mm(d), pcbnew.CORNER_STRATEGY_ROUND_ALL_CORNERS, ERR)
    elif d < 0:
        out.Deflate(mm(-d), pcbnew.CORNER_STRATEGY_ROUND_ALL_CORNERS, ERR)
    return out


def capsule(a, b, w, n=7):
    """the outline of a round-ended line from a to b, w wide"""
    ang = math.atan2(b[1] - a[1], b[0] - a[0])
    pts = [(b[0] + w / 2 * math.cos(ang - math.pi / 2 + math.pi * k / n), b[1] + w / 2 * math.sin(ang - math.pi / 2 + math.pi * k / n)) for k in range(n + 1)]
    pts += [(a[0] + w / 2 * math.cos(ang + math.pi / 2 + math.pi * k / n), a[1] + w / 2 * math.sin(ang + math.pi / 2 + math.pi * k / n)) for k in range(n + 1)]
    return pts


class Art:
    def __init__(self):
        self.ps = pcbnew.SHAPE_POLY_SET()

    def stroke(self, pts, w=LINE):
        for a, b in zip(pts, pts[1:]):
            if math.dist(a, b) > 1e-6:
                self.ps.BooleanAdd(poly(capsule(a, b, w)))

    def disc(self, c, r, n=32):
        self.ps.BooleanAdd(poly([(c[0] + r * math.cos(2 * math.pi * k / n), c[1] + r * math.sin(2 * math.pi * k / n)) for k in range(n)]))

    def add(self, ps):
        self.ps.BooleanAdd(ps)


def smooth(pts, per=10):
    """a Catmull-Rom curve through the points"""
    p = [pts[0]] + list(pts) + [pts[-1]]
    out = []
    for i in range(1, len(p) - 2):
        for k in range(per):
            t = k / per
            out.append(tuple(0.5 * ((2 * p[i][j]) + (-p[i - 1][j] + p[i + 1][j]) * t + (2 * p[i - 1][j] - 5 * p[i][j] + 4 * p[i + 1][j] - p[i + 2][j]) * t * t
                                    + (-p[i - 1][j] + 3 * p[i][j] - 3 * p[i + 1][j] + p[i + 2][j]) * t ** 3) for j in (0, 1)))
    return out + [pts[-1]]


def resample(pts, step):
    out, d, carry = [pts[0]], 0.0, 0.0
    for a, b in zip(pts, pts[1:]):
        L = math.dist(a, b)
        s = step - carry
        while s <= L:
            out.append((a[0] + (b[0] - a[0]) * s / L, a[1] + (b[1] - a[1]) * s / L))
            s += step
        carry = (carry + L) % step
    return out


def zigzag(pts, pitch, amp):
    """teeth: the path with every other point pushed to one side and the rest to the other"""
    q = resample(pts, pitch / 2)
    out = [q[0]]
    for i in range(1, len(q) - 1):
        tx, ty = q[i + 1][0] - q[i - 1][0], q[i + 1][1] - q[i - 1][1]
        L = math.hypot(tx, ty)
        s = amp if i % 2 else -amp
        out.append((q[i][0] - ty / L * s, q[i][1] + tx / L * s))
    return out + [q[-1]]


def lettering(entry, origin, angle, height, centre=False):
    """letter outlines placed with their baseline starting (or centred) at origin, running at `angle`"""
    tx, ty = math.cos(math.radians(angle)), math.sin(math.radians(angle))
    ux, uy = ty, -tx                                     # "up" for the letters
    off = -entry['w'] * height / 2 if centre else 0.0
    ps = pcbnew.SHAPE_POLY_SET()
    for c in entry['contours']:
        ps.BooleanXor(poly([(origin[0] + (gx * height + off) * tx + gy * height * ux,
                             origin[1] + (gx * height + off) * ty + gy * height * uy) for gx, gy in c[:-1]]))
    return ps


# Parts side: which way round the cell goes, by the battery connector's mouth and inside the battery
# rectangle (BOARD millimetres). J2 pad 1 is + and pad 2 is - with the polarity jumpers as made (SJ1 and
# SJ2 bridged 1-2); the marks line up with the two pins, which leave the connector 2 mm apart.
FRONT = [('-', (111.5, 56.0), 1.6, 0.25), ('+', (111.5, 58.7), 1.6, 0.25),
         ('CELL + MUST BE ON THE SIDE MARKED +', (128.0, 63.9), 1.0, 0.15),
         ('CHECK WITH A METER BEFORE USB', (128.0, 65.5), 1.0, 0.15),
         ('IF REVERSED: UNPLUG, CUT SJ1 + SJ2', (128.0, 67.1), 1.0, 0.15),
         ('AND SOLDER THE OTHER SIDE OF EACH', (128.0, 68.7), 1.0, 0.15)]


def front_marks(board):
    words = {t[0] for t in FRONT}
    for d in list(board.GetDrawings()):
        if d.GetLayer() == pcbnew.F_SilkS and d.GetClass() == 'PCB_TEXT' and d.GetText() in words:
            board.RemoveNative(d)
    for text, (x, y), size, thick in FRONT:
        t = pcbnew.PCB_TEXT(board)
        t.SetText(text)
        t.SetPosition(pcbnew.VECTOR2I(mm(x), mm(y)))
        t.SetLayer(pcbnew.F_SilkS)
        t.SetTextSize(pcbnew.VECTOR2I(mm(size), mm(size)))
        t.SetTextThickness(mm(thick))
        board.Add(t)


def main():
    board = pcbnew.LoadBoard(PCB)
    letters = json.load(open(os.path.join(ROOT, 'art', 'lettering.json')))

    # ---- what is on the board already: touch pads, and everything the ink must stay off
    pads = pcbnew.SHAPE_POLY_SET()
    for d in board.GetDrawings():
        if d.GetLayer() == pcbnew.B_Cu and d.GetClass() == 'PCB_SHAPE' and d.GetNetname().startswith('PAD_'):
            pads.BooleanAdd(d.GetPolyShape())
    bare = pcbnew.SHAPE_POLY_SET()                       # mask openings and holes on the show face
    for f in board.GetFootprints():
        for p in f.Pads():
            if p.IsOnLayer(pcbnew.B_Mask):          # the touch pads' own 0.3 mm holes are tented, like vias
                one = pcbnew.SHAPE_POLY_SET()
                p.TransformShapeToPolygon(one, pcbnew.B_Cu if p.IsOnLayer(pcbnew.B_Cu) else pcbnew.F_Cu, mm(0.3), ERR, pcbnew.ERROR_OUTSIDE)
                bare.BooleanAdd(one)
                if p.GetDrillSize().x > 0:
                    c, r = p.GetPosition(), max(p.GetDrillSize().x, p.GetDrillSize().y) / 2 + mm(0.4)
                    hole = pcbnew.SHAPE_POLY_SET()
                    ch = pcbnew.SHAPE_LINE_CHAIN()
                    for k in range(24):
                        ch.Append(int(c.x + r * math.cos(2 * math.pi * k / 24)), int(c.y + r * math.sin(2 * math.pi * k / 24)))
                    ch.SetClosed(True)
                    hole.AddOutline(ch)
                    bare.BooleanAdd(hole)
    body = grow(poly(mo.OUTLINE), -RIM)

    # ---- the drawing
    art = Art()
    # eye, brow
    ex, ey = mo.EYE
    ring = poly([(ex + 2.6 * math.cos(2 * math.pi * k / 40), ey + 2.6 * math.sin(2 * math.pi * k / 40)) for k in range(40)])
    ring.BooleanSubtract(poly([(ex + 2.1 * math.cos(2 * math.pi * k / 40), ey + 2.1 * math.sin(2 * math.pi * k / 40)) for k in range(40)]))
    art.add(ring)
    art.disc((ex + 0.3, ey + 0.1), 1.0)
    art.stroke(smooth([(ex - 4.6, ey - 2.3), (ex - 1.5, ey - 4.2), (ex + 2.2, ey - 4.1), (ex + 5.2, ey - 2.4)]))
    # mouth: teeth from the snout to the snout pad, and from the pad to the corner of the jaw
    sx, sy, srx, sry, srot = 24, 46.5, 9, 3.2, 8          # the snout pad (build_board.PADS['E9'])
    c8, s8 = math.cos(math.radians(srot)), math.sin(math.radians(srot))
    tip_l, tip_r = (sx - (srx + 0.6) * c8, sy - (srx + 0.6) * s8), (sx + (srx + 0.6) * c8, sy + (srx + 0.6) * s8)
    art.stroke(zigzag(smooth([(4.6, 46.7), (8.5, 46.3), tip_l]), 1.9, 0.7), 0.36)
    jaw = smooth([tip_r, (40, 49.6), (47, 51.6), (52.0, 52.7)])
    art.stroke(zigzag(jaw, 1.9, 0.7), 0.36)
    art.stroke(smooth([(52.0, 52.7), (54.6, 52.6), (56.4, 51.2), (57.0, 49.4)]))
    # belly line, from behind the jaw to the rear flipper
    art.stroke(smooth([(60, 58.3), (70, 60.0), (84, 61.3), (100, 61.5), (115, 60.7), (128, 61.0), (137.2, 61.0)]))   # above the USB socket's pins
    # the tail: the backbone turns down into the lower lobe (as a mosasaur's did); rays in the upper lobe
    backbone = smooth([(168, 49.3), (182, 46.6), (194, 45.4), (203, 46.6), (209.5, 50.5), (214.2, 55.6)])
    art.stroke(backbone)

    def backbone_y(x):
        return min(backbone, key=lambda q: abs(q[0] - x))[1]

    def edge_y(x):
        ring_ = mo.OUTLINE + mo.OUTLINE[:1]
        return sorted(a[1] + (b[1] - a[1]) * (x - a[0]) / (b[0] - a[0]) for a, b in zip(ring_, ring_[1:]) if (a[0] - x) * (b[0] - x) <= 0 and a[0] != b[0])
    for a, b in (((206.5, 41.2), (220.6, 25.8)), ((209.6, 43.2), (221.6, 30.4)), ((212.4, 45.6), (220.4, 37.4))):
        art.stroke([a, b], 0.32)
    # bands across the tail stem, above and below the backbone
    for x in (189.5, 194.0, 198.5, 203.0):
        top, mid = edge_y(x)[0], backbone_y(x)
        art.stroke(smooth([(x - 0.9, top + 2.2), (x + 0.5, (top + mid) / 2), (x - 0.4, mid - 1.6)]), 0.36)
    for x in (192.0, 196.5, 201.0):
        mid, bot = backbone_y(x), edge_y(x)[-1]
        art.stroke(smooth([(x - 0.3, mid + 1.6), (x + 0.4, bot - 2.0)]), 0.36)
    art.ps.BooleanSubtract(grow(pads, RING[1] + 0.3))   # the drawing stops short of every touch pad

    # touch pad outlines
    rings = grow(pads, RING[1])
    rings.BooleanSubtract(grow(pads, RING[0]))
    art.add(rings)

    # LED numbers, 1 at the head, each with a tick at the LED's centre
    for i in range(mo.N_LED):
        s = mo.LED_MARGIN + mo.LED_PITCH * i
        x, y, ang = mo.at(mo.SPINE, s, 4.2)
        art.add(lettering(letters['numbers'][str(i + 1)], (x, y), ang, NUM_H, centre=True))
        art.stroke([mo.at(mo.SPINE, s, 0.3)[:2], mo.at(mo.SPINE, s, 1.35)[:2]], 0.4)

    # the name
    art.add(lettering(letters['title'], (58.5, 55.4), -2.2, TITLE_H))

    # ---- ink
    if STYLE == 'reversed':
        ink = pcbnew.SHAPE_POLY_SET(body)
        ink.BooleanSubtract(grow(grow(art.ps, -MIN_GAP / 2), MIN_GAP / 2))     # no bare line thinner than MIN_GAP
    else:
        ink = pcbnew.SHAPE_POLY_SET(art.ps)
        ink.BooleanIntersection(body)
    ink.BooleanSubtract(bare)
    ink = grow(grow(ink, -MIN_INK / 2), MIN_INK / 2)                           # no ink thinner than MIN_INK
    ink.BooleanIntersection(body)
    ink.Simplify()

    # ---- a picture to look at
    def path(ch):
        return 'M ' + ' L '.join('%.3f %.3f' % (MIRROR - pcbnew.ToMM(ch.CPoint(k).x), pcbnew.ToMM(ch.CPoint(k).y) - YOFF) for k in range(ch.PointCount())) + ' Z'

    def paths(ps):
        return ' '.join(path(ps.Outline(i)) + ' ' + ' '.join(path(ps.Hole(i, j)) for j in range(ps.HoleCount(i))) for i in range(ps.OutlineCount()))
    xs, ys = [p[0] for p in mo.OUTLINE], [p[1] for p in mo.OUTLINE]
    x0, y0, w, h = min(xs) - 4, min(ys) - 4, max(xs) - min(xs) + 8, max(ys) - min(ys) + 8
    svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="%.1f %.1f %.1f %.1f">' % (w * 12, h * 12, x0, y0, w, h),
           '<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#e9e6df"/>' % (x0, y0, w, h),
           '<path d="M %s Z" fill="#1f6a43"/>' % ' L '.join('%.3f %.3f' % p for p in mo.OUTLINE),
           '<path d="%s" fill="#2c7c50" fill-rule="evenodd"/>' % paths(pads),
           '<path d="%s" fill="#f7f7f2" fill-rule="evenodd"/>' % paths(ink),
           '<path d="%s" fill="#c9a94a" fill-rule="evenodd"/>' % paths(bare), '</svg>']
    out = os.path.join(ROOT, 'output', 'show_face_art_%s.svg' % STYLE if LOOK else 'show_face_art.svg')
    open(out, 'w').write('\n'.join(svg))
    try:
        subprocess.run(['rsvg-convert', out, '-o', out[:-4] + '.png'], check=True)
    except Exception as e:
        print('no PNG:', e)

    if LOOK:
        print('%s: picture only, %s' % (STYLE, os.path.relpath(out, ROOT)))
        return

    # ---- onto the board
    old = [d for d in board.GetDrawings() if d.GetLayer() == LAYER]
    for d in old:
        board.RemoveNative(d)
    area = ink.Area()
    ink.Fracture()
    for i in range(ink.OutlineCount()):
        one = pcbnew.SHAPE_POLY_SET()
        one.AddOutline(ink.Outline(i))
        g = pcbnew.PCB_SHAPE(board)
        g.SetShape(pcbnew.SHAPE_T_POLY)
        g.SetPolyShape(one)
        g.SetLayer(LAYER)
        g.SetFilled(True)
        g.SetWidth(0)
        board.Add(g)
    front_marks(board)
    board.Save(PCB)
    total = poly(mo.OUTLINE).Area()
    print('%s: %d silkscreen shapes in place of %d; ink covers %.0f %% of the show face' % (STYLE, ink.OutlineCount(), len(old), 100 * abs(area) / abs(total)))


main()
