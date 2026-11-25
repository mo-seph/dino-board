#!/usr/bin/env python3
"""Build the DinoLight board from the schematic's netlist: outline, every footprint placed and linked to
its schematic symbol, every pad on its net, touch electrodes on the show face. No tracks.

Run with KiCad's Python from the project folder, after `python3 tools/schematic.py verify`
(which writes build/sch/netlist.net):

    export KICAD_DOCUMENTS_HOME="$PWD/kicad-user"
    $KPY tools/build_board.py

Writes dinolight.kicad_pcb. IT OVERWRITES THE BOARD: once the board has tracks or hand edits, do not
run this again without asking.

Coordinates in this file are on the SHOW face in mm (head left, as in outline/make_outline.py).
Parts sit on the other side, which is KiCad's front copper, so x is mirrored: X = MIRROR - x.
Everything along an edge (LEDs, connectors on the belly flat, the touch slider) is computed from the
outline; the clusters and single parts below are placed by hand for this outline.
"""
import math
import os
import re
import sys

import pcbnew

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'outline'))
import make_outline as mo
sys.path.insert(0, os.path.join(ROOT, 'tools'))
import touch_block as tb

KFP = '/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints/'
MYLIB = os.path.join(ROOT, 'lib', 'DinoLight.pretty')
NETLIST = os.path.join(ROOT, 'build', 'sch', 'netlist.net')
OUT = os.path.join(ROOT, 'dinolight.kicad_pcb')
MIRROR, YOFF = 240.0, 10.0
GAP = 0.65                                   # between courtyards when packing: room for a track or two
mm = pcbnew.FromMM

# ---------------------------------------------------------------- where things go (show-face mm)
HOLES = {'H1': (27.5, 40.2), 'H2': (134.5, 57.5)}      # placeholders until the case is designed. The tail has none:
                                                        # it sticks out of the case (the owner, 2026-11-23)
BATTERY = (94, 34, 130, 60)                  # keep free of parts
USB_X, SWITCH_X = 115.0, 101.0               # along the belly flat
EXPLICIT = {                                 # ref: (x, y, board rotation)
    'U4': (63, 49.6, 180),                   # module in the neck, antenna end at the throat edge; its pad row
                                             # clears the eleven touch lanes above it
    'R14': (48.7, 34.2, 180),                # spine data resistor beside the first LED, output towards it
    'J2': (137, 47.8, 90),                   # battery connector, opening towards the battery
    'J3': (170.8, 47.6, 90),                 # Qwiic, opening towards the body so a cable stays inside the case; the
                                             # 7 mm in front of it is kept free of parts for the plug
    'C9': (188.5, 40.0, 0), 'TP11': (187.5, 44.0, 0),    # just past the tail end of the LED run and the slider
    'SW3': (19.5, 45.5, 0), 'SW2': (28, 46.9, 0),        # BOOT and RESET in the snout
    'R1': (108.3, 62.4, 90), 'R2': (121.7, 62.4, 90), 'U1': (126, 63.4, 0),
    'U9': (221.0, 25.6, 0), 'C41': (220.3, 28.0, 0),     # temperature / humidity on the tip of the tail
    'BZ1': (35.5, 51.5, 0), 'D24': (26.5, 51.65, 0), 'R37': (21.6, 50.9, 0),     # buzzer in the jaw, as far from the compass as the board allows
}
# packed clusters: name, rectangle (x0, y0, x1, y1), parts
CLUSTERS = [
    ('LED rail switch and module support', (72.2, 40, 91.4, 54.2),     # 91.4: room for the front flipper's touch line beside the battery
     'Q2 Q3 C8 R11 R13 C10 R12 R15 TP5 TP13 TP16 U6 C36 R32 R16 C32 TP12 R34 TP17 R6 R7 C7 R8 R9 TP6 TP7 TP8'),
    ('battery input', (131.0, 35.3, 143.1, 42.6), 'F1 SJ1 SJ2'),
    ('charger', (143.4, 40, 151.9, 56), 'Q1 U2 R3 C1 C2 R10 R19 TP3 TP4 TP15 TP9'),   # the I2C test points are here and in the next cluster
                                                        # because one sat behind the rear-flipper touch pad (layout review)
    ('regulator, enable', (152.8, 40.5, 162.5, 54.0), 'U3 C3 C4 D23 R4 R5 TP1 TP2 TP14 TP10'),     # clear of the Qwiic plug
    ('motion and pressure', (137.8, 56.5, 151.6, 66.5), 'U5 U11 R17 R18'),
    ('compass', (174.2, 45.6, 181.2, 51.4), 'U8'),        # in the tail stem, inside the case (the owner, 2026-11-23), between the
                                                          # end of the LED run and the Qwiic socket: the far end of the LED rail, where its
                                                          # current is smallest, and the furthest the case allows from battery, buzzer and USB shell
    ('light sensor', (7.6, 43.8, 12.5, 48.2), 'U10'),     # at the nose; the case gets a hole over it
    ('buzzer drive', (31.5, 43.3, 39.8, 48.6), 'Q4 R35 R36'),
]
# decoupling that has to sit beside its chip: chip -> [(capacitor, the chip pad it serves)]. Each chip is
# packed together with these as one block.
SATELLITES = {'U3': [('C3', '1'), ('C4', '5')], 'U2': [('C1', '4'), ('C2', '3')],
              'U5': [('C33', '8'), ('C34', '5')], 'U6': [('C36', '3')],
              'U8': [('C39', '2'), ('C40', '10')], 'U10': [('C42', '1')], 'U11': [('C43', '10'), ('C44', '1')]}
# single touch pads: electrode ref -> (centre x, y, half-width, half-length, rotation)
ANCHOR = {'E9': (13.5, 46.6)}                # where a pad's plated hole goes, if not at its centre
PADS = {'E9': (24, 46.5, 9, 3.2, 8), 'E10': (89, 78, 5.5, 9, -28), 'E11': (151, 68, 4.5, 7, -30), 'E12': (218, 60, 3.2, 9, -38)}
# Slider: 8 electrodes along the whole LED run, in a band this far in from the edge. Neighbours interleave
# with long teeth (after Atmel AT11805 "spatial interpolation": sections 3 to 4 mm tall, tips no thinner
# than 0.25 mm), so touch area passes linearly from one electrode to the next.
BAND = (5.5, 11.5)
END_PAD, CENTRE_FLAT, TIP, HALF_GAP_S = 4.0, 1.5, 0.3, 0.8

def B(x, y):
    return (MIRROR - x, y + YOFF)


def vec(x, y):
    return pcbnew.VECTOR2I(mm(x), mm(y))


# ---------------------------------------------------------------- the netlist
TOKEN = re.compile(r'\(|\)|"(?:[^"\\]|\\.)*"|[^\s()"]+')


def parse(text):
    stack, cur = [], None
    for tok in TOKEN.findall(text):
        if tok == '(':
            new = []
            if cur is not None:
                cur.append(new)
                stack.append(cur)
            cur = new
        elif tok == ')':
            if not stack:
                return cur
            cur = stack.pop()
        else:
            cur.append(tok[1:-1] if tok[0] == '"' else tok)
    return cur


def kids(node, head):
    return [c for c in node if isinstance(c, list) and c and c[0] == head]


def kid(node, head):
    k = kids(node, head)
    return k[0] if k else None


def read_netlist():
    tree = parse(open(NETLIST, encoding='utf-8').read())
    comps = {}
    for c in kids(kid(tree, 'components'), 'comp'):
        ref = kid(c, 'ref')[1]
        comps[ref] = dict(value=kid(c, 'value')[1], footprint=kid(c, 'footprint')[1],
                          path=kid(kid(c, 'sheetpath'), 'tstamps')[1] + kid(c, 'tstamps')[1])
    nets = {}
    for n in kids(kid(tree, 'nets'), 'net'):
        nets[kid(n, 'name')[1]] = [(kid(x, 'ref')[1], kid(x, 'pin')[1]) for x in kids(n, 'node')]
    return comps, nets


# ---------------------------------------------------------------- geometry helpers
def angle_for(nx, ny):
    """board rotation that turns a footprint's +Y to point along (nx, ny) in board coordinates"""
    return math.degrees(math.atan2(nx, ny))


def courtyard(fp):
    """courtyard box relative to the footprint position: (left, top, right, bottom) in mm"""
    try:
        fp.BuildCourtyardCaches()
    except Exception:
        pass
    bb = fp.GetCourtyard(pcbnew.F_CrtYd).BBox()
    if bb.GetWidth() == 0:
        bb = fp.GetBoundingBox(False)
    p = fp.GetPosition()
    return tuple(pcbnew.ToMM(v) for v in (bb.GetLeft() - p.x, bb.GetTop() - p.y, bb.GetRight() - p.x, bb.GetBottom() - p.y))


def main():
    comps, nets = read_netlist()
    board = pcbnew.NewBoard(OUT)
    board.SetCopperLayerCount(4)                 # parts side / ground plane / inner signals / show face
    ds = board.GetDesignSettings()
    ds.m_MinClearance = mm(0.15)                 # JLCPCB's comfortable working figure; the LGA and QFN need it
    ds.m_TrackMinWidth = mm(0.127)
    ds.m_ViasMinSize = mm(0.5)
    ds.m_MinThroughDrill = mm(0.3)
    nc = ds.m_NetSettings.GetDefaultNetclass()
    nc.SetClearance(mm(0.15))
    nc.SetTrackWidth(mm(0.15))                   # signals; supply nets are widened in tools/route_board.py
    nc.SetViaDiameter(mm(0.5))
    nc.SetViaDrill(mm(0.3))
    placed = {}

    def load(ref):
        lib, name = comps[ref]['footprint'].rsplit(':', 1)
        path = MYLIB if lib == 'DinoLight' else KFP + lib + '.pretty'
        fp = pcbnew.FootprintLoad(path, name)
        if fp is None:
            raise SystemExit('footprint not found for %s: %s' % (ref, comps[ref]['footprint']))
        fp.SetFPID(pcbnew.LIB_ID(lib, name))
        fp.SetReference(ref)
        fp.SetValue(comps[ref]['value'])
        fp.SetPath(pcbnew.KIID_PATH(comps[ref]['path']))
        if re.match(r'(R|C|D|E|TP|H)\d', ref):
            fp.Reference().SetVisible(False)
        return fp

    def put(ref, bx, by, rot=0):
        """place at BOARD coordinates"""
        fp = load(ref)
        fp.SetPosition(vec(bx, by))
        fp.SetOrientationDegrees(rot)
        board.Add(fp)
        placed[ref] = fp
        return fp

    # ---- outline, eye hole
    def chain(points):
        ch = pcbnew.SHAPE_LINE_CHAIN()
        for p in points:
            ch.Append(mm(B(*p)[0]), mm(B(*p)[1]))
        ch.SetClosed(True)
        return ch

    s = pcbnew.PCB_SHAPE(board)
    s.SetShape(pcbnew.SHAPE_T_POLY)
    edge = pcbnew.SHAPE_POLY_SET()
    edge.AddOutline(chain(mo.OUTLINE))
    s.SetPolyShape(edge)
    s.SetLayer(pcbnew.Edge_Cuts)
    s.SetFilled(False)
    s.SetWidth(mm(0.1))
    board.Add(s)
    ex, ey = mo.EYE

    # ---- nets
    netinfo = {}
    for name in nets:
        ni = pcbnew.NETINFO_ITEM(board, name)
        board.Add(ni)
        netinfo[name] = ni

    # ---- spine LEDs, D1 at the head. Each has its 100 nF standing radially just inboard of its VDD pad,
    #      supply end towards the LED, so the strip can be routed without crossings (tools/route_board.py).
    for i, (x, y, a) in enumerate(mo.leds, 1):
        nxs, nys = math.sin(math.radians(a)), -math.cos(math.radians(a))      # outward normal, show face
        nx, ny = -nxs, nys
        bx, by = B(x, y)
        rot = angle_for(nx, ny)
        led = put('D%d' % i, bx - nx * 1.46, by - ny * 1.46, rot)             # emitting face 0.1 mm inside the edge
        vdd = [p for p in led.Pads() if p.GetNumber() == '2'][0].GetPosition()
        vx, vy = pcbnew.ToMM(vdd.x), pcbnew.ToMM(vdd.y)
        cap = put('C%d' % (10 + i), vx - nx * 2.02, vy - ny * 2.02, rot + 90)
        p1 = [p for p in cap.Pads() if p.GetNumber() == '1'][0].GetPosition()
        if math.hypot(p1.x - vdd.x, p1.y - vdd.y) > mm(2.02):                 # pad 1 (supply) must be the near one
            cap.SetOrientationDegrees(rot - 90)

    # ---- eye: one top-emitting LED on the parts side, shining through a hole in the printed case; capacitor beside
    #      it. No hole in the board. The snout touch pad still keeps 4.6 mm clear of it (below).
    bx, by = B(ex, ey)
    put('D21', bx, by, 0)
    put('C31', *B(33.3, 41.0), 90)

    # ---- edge parts on the belly flat. USB: board edge is 2.66 mm in front of the footprint origin (maker's
    #      drawing: 5.79 from the rear shell slots). The slide switch sits wholly on the board, knob overhanging.
    fx0, fy, fx1, _ = mo.FLAT
    for ref, x, back in (('J1', USB_X, 2.66), ('SW1', SWITCH_X, 2.0)):
        if not fx0 + 4.4 <= x <= fx1 - 4.3:
            raise SystemExit('%s at x=%.1f is not on the belly flat (%.1f to %.1f)' % (ref, x, fx0, fx1))
        put(ref, *B(x, fy - back), 0)

    for ref, (x, y, rot) in EXPLICIT.items():
        put(ref, *B(x, y), rot)
    for ref, (x, y) in HOLES.items():
        put(ref, *B(x, y), 0)

    # ---- touch controller block, in the head (geometry in tools/touch_block.py)
    def put_towards(ref, x, y, axis, near):
        fp = put(ref, x, y, 0 if axis == 'h' else 90)
        d = {p.GetNumber(): math.hypot(pcbnew.ToMM(p.GetPosition().x) - near[0], pcbnew.ToMM(p.GetPosition().y) - near[1]) for p in fp.Pads()}
        if d['1'] > d['2']:
            fp.SetOrientationDegrees(fp.GetOrientationDegrees() + 180)
        return fp

    u7 = put('U7', tb.XC, tb.YC, tb.U7_ROT)
    at13 = [p for p in u7.Pads() if p.GetNumber() == '13'][0].GetPosition()
    at10 = [p for p in u7.Pads() if p.GetNumber() == '10'][0].GetPosition()
    if not (pcbnew.ToMM(at13.y) < tb.YC - 1 and pcbnew.ToMM(at10.x) > tb.XC + 1):
        raise SystemExit('U7 is not turned the way touch_block.py assumes')
    for ref, x, y, axis, near in tb.placements():
        put_towards(ref, x, y, axis, near)

    # ---- module decoupling next to its 3V3 pin (pad 3)
    u4 = placed['U4']
    p3 = [p for p in u4.Pads() if p.GetNumber() == '3'][0].GetPosition()
    px_, py_ = pcbnew.ToMM(p3.x), pcbnew.ToMM(p3.y)
    side = 1 if px_ > pcbnew.ToMM(u4.GetPosition().x) else -1
    put('C6', px_ + side * 1.9, py_, 90)
    put('C5', px_ + side * 2.7, py_ - 3.0, 90)        # clear of the three long touch lines beside R28..R31

    # ---- packed clusters, tallest parts first so each row wastes little height
    for title, (x0, y0, x1, y1), refs in CLUSTERS:
        bx0, bx1 = MIRROR - x1, MIRROR - x0
        by0, by1 = y0 + YOFF, y1 + YOFF
        cx, cy, rowh, used = bx0, by0, 0.0, 0.0
        sized = []
        riders = set(c for sats in SATELLITES.values() for c, pin in sats)
        for ref in refs.split():
            if ref in riders:
                continue
            fp = load(ref)
            fp.SetPosition(vec(0, 0))
            l, t_, r, b = courtyard(fp)
            members = []
            reach = {}                                     # how far out each side is already taken
            for cap, pin in SATELLITES.get(ref, ()):
                pp = [q for q in fp.Pads() if q.GetNumber() == pin][0].GetPosition()
                px, py = pcbnew.ToMM(pp.x), pcbnew.ToMM(pp.y)
                horizontal = abs(px) >= abs(py)
                sx, sy = ((1 if px > 0 else -1), 0) if horizontal else (0, (1 if py > 0 else -1))
                c = load(cap)
                c.SetPosition(vec(0, 0))
                # the capacitor stands across the direction it sits in (beside the chip, not sticking out from
                # it), slid along so that one of its pads is level with the pin
                c.SetOrientationDegrees(90 if horizontal else 0)
                cl, ct, cr, cb = courtyard(c)
                half = (cr - cl) / 2 if horizontal else (cb - ct) / 2
                pads_ = [q for q in c.Pads()]
                off = max(abs(pcbnew.ToMM(q.GetPosition().y if horizontal else q.GetPosition().x)) for q in pads_)
                edge = reach.get((sx, sy), (r if sx > 0 else -l) if horizontal else (b if sy > 0 else -t_))
                out = edge + 0.1 + half
                reach[(sx, sy)] = out + half
                if horizontal:
                    dx, dy = sx * out, py - (off if py > 0 else -off)
                else:
                    dx, dy = px - (off if px > 0 else -off), sy * out
                c.SetPosition(vec(dx, dy))
                # the capacitor pad on the chip pin's net is the one level with the pin
                want = [n_ for n_, nodes in nets.items() if (ref, pin) in nodes][0]
                mine = [q for q in c.Pads() if (cap, q.GetNumber()) in nets[want]][0].GetPosition()
                other = [q for q in c.Pads() if (cap, q.GetNumber()) not in nets[want]][0].GetPosition()
                near = lambda q: math.hypot(pcbnew.ToMM(q.x) - px, pcbnew.ToMM(q.y) - py)
                if near(mine) > near(other):
                    c.SetOrientationDegrees(c.GetOrientationDegrees() + 180)
                cl, ct, cr, cb = courtyard(c)
                l, t_, r, b = min(l, dx + cl), min(t_, dy + ct), max(r, dx + cr), max(b, dy + cb)
                members.append((cap, c, dx, dy))
            sized.append((ref, fp, l, t_, r, b, members))
        sized.sort(key=lambda s_: -(s_[5] - s_[3]))
        for ref, fp, l, t, r, b, members in sized:
            w, h = r - l, b - t
            if cx + w > bx1 + 1e-6:
                cx, cy, rowh = bx0, cy + rowh + GAP, 0.0
            if cx + w > bx1 + 1e-6:
                raise SystemExit('cluster "%s": %s and its capacitors are %.1f mm wide, the area is %.1f' % (title, ref, w, bx1 - bx0))
            if cy + h > by1 + 1e-6:
                raise SystemExit('cluster "%s" is full at %s (needs %.1f more mm of height)' % (title, ref, cy + h - by1))
            fp.SetPosition(vec(cx - l, cy - t))
            board.Add(fp)
            placed[ref] = fp
            for cap, c, dx, dy in members:
                c.SetPosition(vec(cx - l + dx, cy - t + dy))
                board.Add(c)
                placed[cap] = c
            cx += w + GAP
            rowh = max(rowh, h)
            used += w * h
        print('cluster %-56s %4.0f mm2 of courtyard in %4.0f mm2' % (title, used, (bx1 - bx0) * (by1 - by0)))

    # ---- touch electrodes on the show face (KiCad back copper, under solder mask), each on its net,
    #      kept 1 mm inside the board edge and clear of the eye LED and mounting holes
    inset = pcbnew.SHAPE_POLY_SET()
    inset.AddOutline(chain(mo.OUTLINE))
    inset.Inflate(-mm(1.0), pcbnew.CORNER_STRATEGY_ROUND_ALL_CORNERS, mm(0.01))
    for hx, hy, hr in [(ex, ey, 4.6)] + [(x, y, 1.35 + 1.5) for x, y in HOLES.values()]:
        hole = pcbnew.SHAPE_POLY_SET()
        hole.AddOutline(chain([(hx + hr * math.cos(2 * math.pi * k / 36), hy + hr * math.sin(2 * math.pi * k / 36)) for k in range(36)]))
        inset.BooleanSubtract(hole)
    for z in placed['U4'].Zones():               # no touch copper in the module's antenna keep-out, or within 0.3 mm of it
        if z.GetIsRuleArea():
            bb_ = z.GetBoundingBox()
            x0_, x1_ = MIRROR - pcbnew.ToMM(bb_.GetRight()) - 0.3, MIRROR - pcbnew.ToMM(bb_.GetLeft()) + 0.3
            y0_, y1_ = pcbnew.ToMM(bb_.GetTop()) - YOFF - 0.3, pcbnew.ToMM(bb_.GetBottom()) - YOFF + 0.3
            keep = pcbnew.SHAPE_POLY_SET()
            keep.AddOutline(chain([(x0_, y0_), (x1_, y0_), (x1_, y1_), (x0_, y1_)]))
            inset.BooleanSubtract(keep)
    stems = ['SPINE%d' % i for i in range(1, 9)] + ['SNOUT', 'FLIP_F', 'FLIP_R', 'TAIL']
    ref_to_stem = {'E%d' % (i + 1): s_ for i, s_ in enumerate(stems)}

    def electrode(ref, points, centre):
        g = pcbnew.PCB_SHAPE(board)
        g.SetShape(pcbnew.SHAPE_T_POLY)
        ps = pcbnew.SHAPE_POLY_SET()
        ps.AddOutline(chain(points))
        ps.BooleanIntersection(inset)
        g.SetPolyShape(ps)
        g.SetLayer(pcbnew.B_Cu)
        g.SetFilled(True)
        g.SetWidth(0)
        g.SetNet(netinfo['PAD_' + ref_to_stem[ref]])
        board.Add(g)
        put(ref, *B(*ANCHOR.get(ref, centre)), 0)

    def sp(s_, depth):
        return mo.at(mo.SLIDER, s_, depth)[:2]

    def line(a, b):
        """a straight run in (distance along the spine, depth) space, mapped onto the curved band"""
        n_ = max(1, int(math.hypot(b[0] - a[0], (b[1] - a[1]) * 3) / 2.0))
        return [sp(a[0] + (b[0] - a[0]) * q / n_, a[1] + (b[1] - a[1]) * q / n_) for q in range(n_ + 1)]

    d0, d1 = BAND
    dm, h = (d0 + d1) / 2, (BAND[1] - BAND[0]) / 2
    total = mo.slider_len
    centres = [END_PAD + (total - 2 * END_PAD) * k / 7 for k in range(8)]
    for j in range(8):
        pts = []
        # left end: either the square end of the slider, or two half-teeth reaching back towards the previous centre
        if j == 0:
            top_l = bot_l = 0.0
            left = []
        else:
            a = centres[j - 1] + CENTRE_FLAT + HALF_GAP_S         # where the half-teeth would come to a point
            b = centres[j] - CENTRE_FLAT + HALF_GAP_S             # bottom of the notch the neighbour's tooth sits in
            st = a + TIP * (b - a) / h                            # cut the points off where they are TIP wide
            top_l = bot_l = st
            left = line((st, d1), (st, d1 - TIP))[:-1] + line((st, d1 - TIP), (b, dm))[:-1] + \
                line((b, dm), (st, d0 + TIP))[:-1] + line((st, d0 + TIP), (st, d0))[:-1]
        # right end: the square end, or one central tooth reaching towards the next centre
        if j == 7:
            top_r = bot_r = total
            right = []
        else:
            a = centres[j] + CENTRE_FLAT - HALF_GAP_S
            b = centres[j + 1] - CENTRE_FLAT - HALF_GAP_S
            cut = b - (TIP / 2) * (b - a) / h
            top_r = bot_r = a
            right = line((a, d0), (cut, dm - TIP / 2))[:-1] + line((cut, dm - TIP / 2), (cut, dm + TIP / 2))[:-1] + \
                line((cut, dm + TIP / 2), (a, d1))[:-1]
        pts += line((top_l, d0), (top_r, d0))[:-1] if not right else line((top_l, d0), (top_r, d0))[:-1]
        pts += right if right else line((top_r, d0), (bot_r, d1))[:-1]
        pts += line((bot_r, d1), (bot_l, d1))[:-1]
        pts += left if left else line((bot_l, d1), (top_l, d0))[:-1]
        electrode('E%d' % (j + 1), pts, sp(centres[j], tb.ANCHOR_DEPTH))
    for ref, (cx, cy, rx, ry, rot) in PADS.items():
        c_, s_ = math.cos(math.radians(rot)), math.sin(math.radians(rot))
        electrode(ref, [(cx + rx * math.cos(t) * c_ - ry * math.sin(t) * s_, cy + rx * math.cos(t) * s_ + ry * math.sin(t) * c_)
                        for t in [2 * math.pi * k / 48 for k in range(48)]], (cx, cy))

    # ---- everything placed? then pad nets
    missing = [r for r in comps if r not in placed]
    if missing:
        raise SystemExit('not placed: ' + ' '.join(sorted(missing)))
    count = 0
    for name, nodes in nets.items():
        for ref, pin in nodes:
            hit = [p for p in placed[ref].Pads() if p.GetNumber() == pin]
            if not hit:
                raise SystemExit('%s has no pad %s (net %s)' % (ref, pin, name))
            for p in hit:
                p.SetNet(netinfo[name])
                count += 1

    # ---- is every part on the board? (courtyard corners against the outline; edge parts excepted)
    off = []
    for ref, fp in placed.items():
        if ref in ('J1', 'SW1', 'U4') or comps[ref]['value'] == 'SK6812SIDE-A':     # U4's courtyard is its antenna keep-out
            continue
        p = fp.GetPosition()
        l, t, r, b = courtyard(fp)
        cx_, cy_ = pcbnew.ToMM(p.x), pcbnew.ToMM(p.y)
        for qx, qy in ((cx_ + l, cy_ + t), (cx_ + r, cy_ + t), (cx_ + l, cy_ + b), (cx_ + r, cy_ + b)):
            if not mo.inside(MIRROR - qx, qy - YOFF):
                off.append(ref)
                break
    if off:
        print('PARTLY OFF THE BOARD:', ' '.join(sorted(set(off))))

    # ---- battery area and labels
    x0, y0, x1, y1 = BATTERY
    r = pcbnew.PCB_SHAPE(board)
    r.SetShape(pcbnew.SHAPE_T_RECT)
    r.SetStart(vec(*B(x1, y0)))
    r.SetEnd(vec(*B(x0, y1)))
    r.SetLayer(pcbnew.F_SilkS)
    r.SetWidth(mm(0.15))
    board.Add(r)
    bcx, bcy = (x0 + x1) / 2, (y0 + y1) / 2
    for text, (x, y), layer, mirrored in [('BATTERY: keep clear', (bcx, bcy - 3), pcbnew.F_SilkS, False),
                                          ('DinoLight v0.1 DRAFT 2026-11-22', (bcx, bcy + 4), pcbnew.F_SilkS, False)]:
        # the show face's silkscreen is drawn by tools/silkscreen.py, after routing
        t = pcbnew.PCB_TEXT(board)
        t.SetText(text)
        t.SetPosition(vec(*B(x, y)))
        t.SetLayer(layer)
        t.SetTextSize(pcbnew.VECTOR2I(mm(1.2), mm(1.2)))
        t.SetTextThickness(mm(0.18))
        t.SetMirrored(mirrored)
        board.Add(t)

    pcbnew.SaveBoard(OUT, board)
    print('wrote %s: %d footprints, %d nets, %d pads on nets' % (os.path.basename(OUT), len(placed), len(nets), count))


if __name__ == '__main__':
    import shutil
    backup = OUT + '.bak'
    if os.path.exists(OUT):
        shutil.copy2(OUT, backup)                # a failed build must not leave an empty board behind
    try:
        main()
    except BaseException:
        if os.path.exists(backup):
            shutil.copy2(backup, OUT)
            print('build failed: previous board restored')
        raise
