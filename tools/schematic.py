#!/usr/bin/env python3
"""DinoLight schematic: WHERE things are drawn. The parts and nets are in design_spec.py.

    python3 tools/schematic.py            check the drawing and write the .kicad_sch files
    python3 tools/schematic.py verify     ... then KiCad ERC and netlist comparison
    python3 tools/schematic.py export     ... then output/schematic.pdf and a PNG per page

Set KICAD_DOCUMENTS_HOME to <project>/kicad-user first. Coordinates are grid units of 1.27 mm.
If the schematic has been edited by hand in KiCad, do not run this again without asking: it overwrites."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import design_spec as spec
import schdraw
from schdraw import ACROSS, LEFT, RIGHT

d = schdraw.Design('dinolight', folder=spec.ROOT, title='DinoLight', rev='0.1', paper='A3',
                   libs={'DinoLight': 'lib/DinoLight.kicad_sym'})
spec.declare(d)

P = d.sheet('Power')
M = d.sheet('MCU')
L = d.sheet('LEDs')
S = d.sheet('Sensors')

# =====================================================================================
# Page 1: power
# =====================================================================================
P.subsheet(M, 244, 117, 44, 7)
P.subsheet(L, 244, 133, 44, 7)
P.subsheet(S, 244, 149, 44, 7)

# ---- USB-C in --------------------------------------------------------------------
P.frame(12, 14, 108, 104, 'USB-C in')
j1 = P.part('J1', 30, 58, ref=(-8, -15.5, 'l'), val=(-3, -15.5, 'l'))
vb = j1.p('A4')
P.wire(vb, (48, vb[1]))
P.power('VBUS', 48, vb[1])
P.connect(j1, 'A5', length=6)
P.connect(j1, 'B5', length=6)
P.connect(j1, 'A8')
P.connect(j1, 'B8')
P.power('GND', *j1.p('A1'))
P.power('GND', *j1.p('SH'))
P.wire(j1.p('SH'), (18, 76))
P.power('PWR_FLAG', 18, 76, direction='down')
P.wire(j1.p('A7'), (46, 56), (46, 58))                    # the two D- contacts joined
P.wire(j1.p('B7'), (46, 58))
P.wire(j1.p('A6'), (50, 60), (50, 62))                    # the two D+ contacts joined
P.wire(j1.p('B6'), (50, 62))
u1 = P.part('U1', 72, 58, ref=(4, 4, 'l'), val=(4, 6, 'l'))
P.wire((46, 58), u1.p(1))
P.wire((50, 60), u1.p(3))
P.name_wire('USB_DM', (60, 58), 'up')
P.name_wire('USB_DP', (60, 60), 'down')
P.wire(u1.p(6), (84, 58))
P.glabel('USB_DM', 84, 58)
P.wire(u1.p(4), (84, 60))
P.glabel('USB_DP', 84, 60)
P.connect(u1, 5)
P.connect(u1, 2)
r1 = P.part('R1', 58, 88)
r2 = P.part('R2', 70, 88)
P.connect_all(r1)
P.connect_all(r2)
P.note(14, 97, 'R1, R2: 5.1k on each CC line asks the host for 5 V.',
       'D+ and D- go straight to the module, which has USB built in. U1 clamps static.')

# ---- charger -----------------------------------------------------------------------
P.frame(112, 14, 200, 104, 'LiPo charger, 213 mA')
u2 = P.part('U2', 150, 56, ref=(2, -5.5, 'l'), val=(2, -7.5, 'l'))
P.wire(u2.p(4), (150, 42), (126, 42))
P.power('VBUS', 134, 42)
P.power('PWR_FLAG', 126, 42)
c1 = P.part('C1', 134, 48, **LEFT)
P.wire((134, 42), c1.p(1))
P.power('GND', *c1.p(2))
P.power('GND', *u2.p(2))
P.wire(u2.p(3), (192, 54))
P.power('+BATT', 192, 54)
c2 = P.part('C2', 184, 58)
P.wire((184, 54), c2.p(1))
P.power('GND', *c2.p(2))
r3 = P.part('R3', 136, 64)
P.wire(u2.p(5), (136, 58), r3.p(1))
P.power('GND', *r3.p(2))
P.name_wire('CHG_PROG', (139, 58), 'up')
r10 = P.part('R10', 170, 70, rot=90, **ACROSS)
P.wire(u2.p(1), (164, 58), (164, 70), r10.p(1))
P.name_wire('CHG_STAT_5V', (164, 62), 'right')
r19 = P.part('R19', 180, 76)
P.wire(r10.p(2), (180, 70), (188, 70))
P.wire((180, 70), r19.p(1))
P.power('GND', *r19.p(2))
P.glabel('CHG_STAT', 188, 70)
P.part('TP15', 184, 70, ref=(1.5, -2.6, 'l'), val=None)
P.note(114, 86, 'R3 sets the charge current: 1000 V / 4.7k = 213 mA.',
       'STAT is a three-state output that swings to VBUS (5 V) when charging',
       'is complete, so R10 / R19 scale it by 2/3 for the 3.3 V input.',
       'CHG_STAT: high = charge complete; low = charging, or no USB.')

# ---- battery input -----------------------------------------------------------------
P.frame(204, 14, 318, 104, 'Battery in: polarity, fuse, reverse protection')
j2 = P.part('J2', 220, 56, mirror='y', ref=(-2, -3, 'r'), val=(-2, -5, 'r'))
f1 = P.part('F1', 234, 56, rot=90, **ACROSS)
sj1 = P.part('SJ1', 248, 48, mirror='y', ref=(0, -3, 'c'), val=None)
sj2 = P.part('SJ2', 248, 68, mirror='x', ref=(0, 3.5, 'c'), val=None)
P.wire(j2.p(1), f1.p(1))
P.name_wire('BAT_P1', (227, 56), 'up')
P.wire(f1.p(2), (248, 56), sj1.p(2))
P.name_wire('BAT_P1F', (240, 56), 'up')
P.wire(j2.p(2), (226, 58), (226, 62), (248, 62), sj2.p(2))
P.name_wire('BAT_P2', (236, 62), 'down')
P.connect(sj1, 3)
P.connect(sj2, 1)
P.connect(j2, 'MP')
q1 = P.part('Q1', 276, 50, rot=90, ref=(4, 3, 'l'), val=(4, 5, 'l'))
P.wire(sj1.p(1), q1.p(3))
P.wire(sj2.p(3), (258, 68), (258, 48))
P.name_wire('BAT_RAW', (264, 48), 'up')
P.wire(q1.p(2), (298, 48))
P.power('+BATT', 298, 48)
P.power('GND', *q1.p(1))
P.note(206, 80, 'SJ1, SJ2 choose the battery polarity. As built (pads 1-2 bridged) J2 pin 1 is +.',
       'For a cell wired the other way: UNPLUG THE CELL, cut both bridges, then solder pads 2-3 on both.',
       'F1 (1.1 A resettable) is in series with the connector pin, so any jumper mistake is fused.',
       'Q1 blocks a reversed cell: its gate is at ground, so it only conducts when the battery side',
       'is positive. With USB plugged in as well, a reversed cell is slowly drained, not damaged.',
       'The LiPo is not fitted by the assembler: it must be a protected cell. Check polarity with a',
       'meter (+BATT test point against GND) before the first USB plug.')

# ---- on/off and 3.3 V ----------------------------------------------------------------
P.frame(12, 110, 150, 215, 'On / off and 3.3 V')
u3 = P.part('U3', 96, 150, ref=(-6, -5.5, 'l'), val=(2, 6, 'l'))
P.wire(u3.p(1), (66, 148))
P.power('+BATT', 66, 148)
c3 = P.part('C3', 74, 152, **LEFT)
P.wire((74, 148), c3.p(1))
P.power('GND', *c3.p(2))
P.wire(u3.p(5), (124, 148))
P.power('+3V3', 124, 148)
c4 = P.part('C4', 114, 152)
P.wire((114, 148), c4.p(1))
P.power('GND', *c4.p(2))
P.power('GND', *u3.p(2))
P.connect(u3, 4)
sw1 = P.part('SW1', 50, 166, mirror='y', ref=(0, -5, 'c'), val=(0, -7, 'c'))
P.wire(sw1.p(2), (82, 166), (82, 152), u3.p(3))
P.wire(sw1.p(1), (38, 164))
P.power('+BATT', 38, 164)
P.connect(sw1, 3)
P.connect(sw1, 'SH')
r5 = P.part('R5', 82, 172)
P.wire((82, 166), r5.p(1))
P.power('GND', *r5.p(2))
r4 = P.part('R4', 66, 184, rot=90, **ACROSS)
d23 = P.part('D23', 52, 184, rot=180, **ACROSS)
P.wire((44, 184), d23.p(2))
P.power('VBUS', 44, 184)
P.wire(d23.p(1), r4.p(1))
P.name_wire('EN_USB', (59, 184), 'down')
P.wire(r4.p(2), (72, 184), (72, 166))
P.name_wire('LDO_EN', (62, 166), 'up')
P.part('TP14', 75, 166, ref=(1.5, -2.6, 'l'), val=None)
P.hint('SW1: 2-1 joined = on; 2-3 = off (3 is open)', 16, 178)
P.note(14, 196, 'SW1 on: LDO_EN = battery, regulator runs. SW1 carries no load current.',
       'USB plugged in: D23, R4 / R5 put about 2.2 V on LDO_EN whatever SW1 says, so it can',
       'show charging and be programmed. Otherwise off: U3 shut down (0.01 uA typ),',
       'LED rail off. D23 stops the battery feeding back onto VBUS through R4.',
       'U3 is an XC6220B331: 0.2 ohm pass transistor (60 mV dropout at 300 mA), 8 uA quiescent.')

# ---- monitoring ------------------------------------------------------------------------
P.frame(154, 110, 232, 215, 'Battery voltage and USB detect')
r6 = P.part('R6', 170, 138)
P.power('+BATT', *r6.p(1))
r7 = P.part('R7', 170, 150)
P.wire(r6.p(2), r7.p(1))
P.power('GND', *r7.p(2))
c7 = P.part('C7', 184, 148)
P.wire((170, 144), (198, 144))
P.wire((184, 144), c7.p(1))
P.power('GND', *c7.p(2))
P.glabel('VBAT_SENSE', 198, 144)
r8 = P.part('R8', 170, 174)
P.power('VBUS', *r8.p(1))
r9 = P.part('R9', 170, 186)
P.wire(r8.p(2), r9.p(1))
P.power('GND', *r9.p(2))
P.wire((170, 180), (198, 180))
P.glabel('VBUS_DET', 198, 180)
P.note(156, 200, 'VBAT_SENSE = battery / 2, on an ADC1 pin (2 uA standing).',
       'VBUS_DET = VBUS x 2/3: 3.3 V while USB is plugged in.',
       'Firmware should sleep at about 3.5 V.')

# ---- test points and holes -----------------------------------------------------------------
P.frame(236, 110, 318, 196, 'Pages, test points, holes')
for i, net in enumerate(spec.TESTPOINTS[:5]):
    x, y = 246 + i * 14, 180
    P.part('TP%d' % (i + 1), x, y, ref=(-1.5, -2.6, 'r'), val=None)
    if net == 'GND':
        P.power('GND', x, y)
    else:
        P.wire((x, y), (x, y + 3), (x + 4, y + 3))
        P.power(net, x + 4, y + 3)
for i in (1, 2):
    P.part('H%d' % i, 304, 114 + i * 12, ref=(0, -2.6, 'c'), val=(0, 2.6, 'c'))
P.note(240, 165, 'Page 2: module, touch, Qwiic.', 'Page 3: LED rail, eye, spine chain.', 'Page 4: sensors and buzzer.')

# =====================================================================================
# Page 2: module, touch, accelerometer
# =====================================================================================
M.frame(12, 14, 112, 120, 'Touch electrodes (bare front face, under solder mask)')
for i, (stem, what) in enumerate(spec.TOUCH):
    y = 30 + 7 * i
    M.glabel('T_' + stem, 34, y, rot=180)
    rr = M.part('R%d' % (20 + i), 44, y, rot=90, ref=(0, -2.3, 'c'), val=None)
    M.wire((34, y), rr.p(1))
    M.wire(rr.p(2), (66, y))
    M.part(spec.ELECTRODE.get(stem, 'E%d' % (i + 1)), 58, y, ref=(1.5, -2.6, 'l'), val=None)
    M.glabel('PAD_' + stem, 66, y)
    M.hint('%s, ELE%d' % (what, i), 86, y)
M.note(14, 113, 'R20 to R31 are 470R: static protection in series with each electrode.')

M.frame(12, 124, 112, 174, 'Touch controller MPR121 (I2C 0x5C)')
u7 = M.part('U7', 62, 150, ref=(-8, -15.5, 'l'), val=(2, 15.5, 'l'))
M.connect_all(u7, length=2)
M.connect_all(M.part('C37', 94, 146))
M.connect_all(M.part('TP17', 104, 152, ref=(1.5, -2.6, 'l'), val=None))
M.connect_all(M.part('R34', 20, 138, ref=(-2.4, 0, 'r'), val=None))
M.connect_all(M.part('R33', 28, 150, ref=(-2.4, 0, 'r'), val=None))
M.connect_all(M.part('C38', 36, 150, ref=(-2.4, 0, 'r'), val=None))
M.note(14, 162, 'R34 100k pulls up IRQ (open collector).', 'R33 75k 1 % sets the charge current.',
       'C38 100 nF on the internal regulator.', 'ADDR tied to SDA: address 0x5C.',
       'IRQ on GPIO1 can wake the module.')

M.frame(116, 14, 204, 120, 'ESP32-S3 module')
u4 = M.part('U4', 160, 68, ref=(-10, -23.5, 'l'), val=(2.5, -23.5, 'l'))
gnd = [str(p) for p in (2, 42, 43) + tuple(range(46, 66))]
M.connect_all(u4, skip=gnd, length=3)
M.note(118, 100, 'GPIO0 (BOOT) has an internal pull-up. GPIO3, 45, 46 are strapping',
       'pins left open: their defaults give a normal boot with USB.',
       'GPIO19 / 20 are the USB pair. Touch is read by U7, not the module.',
       'IO21 high = LED rail on. IO11 = spine data, IO48 = eye data.',
       'Unlabelled pins are spare and not brought out.')

M.frame(208, 14, 318, 76, 'Reset, boot, decoupling')
r16 = M.part('R16', 244, 30)
M.power('+3V3', *r16.p(1))
c32 = M.part('C32', 244, 46)
M.wire(r16.p(2), c32.p(1))
M.power('GND', *c32.p(2))
M.wire((244, 38), (234, 38))
M.glabel('EN', 234, 38, rot=180)
M.part('TP12', 241, 38, ref=(-1.5, -2.6, 'r'), val=None)
sw2 = M.part('SW2', 260, 38, ref=(0, -4, 'c'), val=(0, 2.5, 'c'))
M.wire((244, 38), sw2.p(1))
M.wire(sw2.p(2), (270, 38))
M.power('GND', 270, 38)
u6 = M.part('U6', 216, 52, ref=(-3, -5, 'r'), val=(0, 10, 'c'))
M.power('+3V3', *u6.p(3))
M.power('GND', *u6.p(1))
r32 = M.part('R32', 231, 52, rot=90, **ACROSS)
M.wire(u6.p(2), r32.p(1))
M.name_wire('RST_OD', (226, 52), 'down')
M.wire(r32.p(2), (238, 52), (238, 38))
M.connect_all(M.part('C36', 224, 32))
sw3 = M.part('SW3', 260, 62, ref=(0, -4, 'c'), val=(0, 2.5, 'c'))
M.glabel('BOOT', 240, 62, rot=180)
M.wire((240, 62), sw3.p(1))
M.wire(sw3.p(2), (270, 62))
M.power('GND', 270, 62)
c5 = M.part('C5', 290, 34)
c6 = M.part('C6', 302, 34)
M.connect_all(c5)
M.connect_all(c6)
M.hint('at the module 3V3 pin', 286, 44)
M.note(276, 50, 'Hold BOOT, tap RESET: ROM loader', 'on USB. Only needed if the', 'firmware is badly broken.')
M.note(210, 67, 'U6 (TLV803S, open drain) holds EN low while 3V3 is under 2.93 V, so a flat cell can take the',
       "charger's 21 mA trickle instead of the module eating it. U6 also gives the 200 ms start-up delay.",
       'R16 is 100k to keep the held-off drain low; R32 limits the current when U6 discharges C32.')

M.frame(208, 80, 318, 150, 'I2C pull-ups and Qwiic')
r17 = M.part('R17', 228, 100)
r18 = M.part('R18', 244, 100)
M.connect_all(r17)
M.connect_all(r18)
j3 = M.part('J3', 290, 108, ref=(3, 1, 'l'), val=(3, 3, 'l'))
M.connect_all(j3)
M.note(210, 124, 'One I2C bus, nose to tail: touch 0x5C, motion 0x6A, compass 0x2C,',
       'temperature / humidity 0x44, light 0x29, pressure 0x46 (page 4), plus Qwiic.',
       'R17, R18 are 2.2k for the length of the bus. Use 100 kHz unless measured.',
       'Qwiic: 1 GND, 2 3V3, 3 SDA, 4 SCL.')

M.frame(116, 124, 204, 150, 'Test points')
for i, net in enumerate(spec.TESTPOINTS[5:10]):
    tp = M.part('TP%d' % (6 + i), 130 + 15 * i, 132, ref=(1.5, -2.6, 'l'), val=None)
    M.connect_all(tp)

M.frame(12, 178, 112, 215, 'For firmware')
M.note(14, 184,
       'Touch          MPR121 at 0x5C: ELE0-7 spine 1-8 (head to tail), ELE8 snout,',
       '               9 tail, 10 rear flipper, 11 front flipper. TOUCH_IRQ on GPIO1',
       'VBAT_SENSE     GPIO10, battery / 2',
       'ACC_INT1, 2    GPIO15, GPIO16',
       'CHG_STAT       GPIO17, high = charge complete',
       'VBUS_DET       GPIO18, high = USB present',
       'LED_EN         GPIO21, high = LED rail on',
       'SDA, SCL       GPIO41, GPIO42 (accelerometer 0x19, Qwiic)',
       'SPINE_DATA     GPIO11, %d LEDs, first at the head' % spec.N_LED,
       'BUZZ           GPIO4, high = buzzer on (4 kHz square wave)',
       'EYE_DATA       GPIO48, 1 LED',
       'UART           GPIO43 TX, GPIO44 RX on test points',
       'Turn the LED rail off before sleeping: each LED draws 0.6 mA when dark.',
       'Limit brightness: the LED maker allows 70 % with all three colours lit.')

# =====================================================================================
# Page 3: LEDs
# =====================================================================================
L.frame(12, 14, 150, 100, 'LED rail switch')
q2 = L.part('Q2', 90, 52, mirror='x', ref=(4, -1, 'l'), val=(4, 1, 'l'))
L.power('+BATT', 92, 40)
L.wire((80, 40), (92, 40), q2.p(2))
r11 = L.part('R11', 80, 46)
L.wire((80, 40), r11.p(1))
L.wire(r11.p(2), (80, 52))
c10 = L.part('C10', 80, 58)
L.wire((80, 52), c10.p(1))
L.wire(c10.p(2), (80, 62), (92, 62))
L.wire(q2.p(1), (66, 52))
r13 = L.part('R13', 54, 58)
L.wire((66, 52), (54, 52), r13.p(1))
L.name_wire('LED_GATE', (60, 52), 'up')
q3 = L.part('Q3', 52, 68, ref=(5, 1.5, 'l'), val=(5, 3.5, 'l'))
L.wire(r13.p(2), q3.p(3))
L.name_wire('LED_PULL', (54, 62), 'right')
L.power('GND', *q3.p(2))
L.glabel('LED_EN', 26, 68, rot=180)
L.wire((26, 68), q3.p(1))
L.part('TP13', 32, 68, ref=(1.5, -2.6, 'l'), val=None)
r12 = L.part('R12', 38, 74, **LEFT)
L.wire((38, 68), r12.p(1))
L.power('GND', *r12.p(2))
L.wire(q2.p(3), (92, 62), (120, 62))
L.power('VLED', 120, 62)
L.power('PWR_FLAG', 112, 62)
c8 = L.part('C8', 104, 66)
L.wire((104, 62), c8.p(1))
L.power('GND', *c8.p(2))
L.note(14, 84, 'LED_EN high turns the LED rail on. It is off by default (R12) and must be off in sleep:',
       '19 LEDs idle at 0.6 mA each. C10 (gate to drain) and R13 make the rail rise over about 1.5 ms,',
       'so switching the LEDs on does not dip the battery and reset the module.',
       'The LEDs run from the battery, never from USB 5 V: their input threshold is 0.65 x VLED,',
       'which 3.3 V logic meets at 4.2 V but not at 5 V.')

L.frame(154, 14, 318, 100, 'Data in, and the eye')
L.glabel('SPINE_DATA', 172, 30, rot=180)
r14 = L.part('R14', 184, 30, rot=90, **ACROSS)
L.wire((172, 30), r14.p(1))
L.wire(r14.p(2), (198, 30))
L.glabel('SPINE_DIN', 198, 30)
L.glabel('EYE_DATA', 172, 58, rot=180)
r15 = L.part('R15', 184, 58, rot=90, **ACROSS)
L.wire((172, 58), r15.p(1))
d21 = L.part('D21', 212, 58, ref=(1, -5.2, 'l'), val=(5, 5.5, 'l'))
L.wire(r15.p(2), d21.p(1))
L.name_wire('EYE_DIN', (196, 58), 'up')
L.part('TP16', 202, 58, ref=(1.5, -2.6, 'l'), val=None)
L.connect(d21, 2)
L.connect(d21, 4)
L.connect(d21, 3)
for ref, x in (('C31', 250), ('C9', 298)):
    L.connect_all(L.part(ref, x, 58))
L.hint('C9: at the tail end of the rail', 290, 68)
L.note(156, 80, 'The eye is one ordinary top-emitting LED (SK6812MINI-012) on the parts side, shining away from the',
       'board through a hole in the printed case. Pins 1 DIN, 2 VDD, 3 DOUT, 4 GND. R14, R15 damp the data edges.')

L.frame(12, 104, 318, 197, 'Spine: %d side-emitting LEDs, D1 at the head, each with 100 nF beside it' % spec.N_LED)
X0, PITCH, ROWS = 36, 28, (132, 178)
leds = []
for k in range(spec.N_LED):
    row, col = divmod(k, 10)
    x, y = X0 + PITCH * col, ROWS[row]
    dd = L.part('D%d' % (k + 1), x, y, ref=(1, -5.2, 'l'), val=None)
    L.connect(dd, 2)
    L.connect(dd, 4)
    L.connect_all(L.part('C%d' % (11 + k), x + 14, y - 10, ref=(2.4, 0, 'l'), val=None))
    leds.append(dd)
L.glabel('SPINE_DIN', 26, ROWS[0], rot=180)
L.wire((26, ROWS[0]), leds[0].p(1))
for k in range(spec.N_LED - 1):
    a, b = leds[k], leds[k + 1]
    if k == 9:                                            # end of the first row: wrap round to the second
        L.wire(a.p(3), (304, ROWS[0]), (304, 154), (20, 154), (20, ROWS[1]), b.p(1))
    else:
        L.wire(a.p(3), b.p(1))
    px = a.p(3)
    L.name_wire('SPINE_%d' % (k + 1), (px[0] + 6, px[1]), 'down', length=1)
end = leds[-1].p(3)
L.wire(end, (306, end[1]))
L.part('TP11', 306, end[1], ref=(1.5, -2.6, 'l'), val=None)
L.name_wire('SPINE_OUT', (end[0] + 6, end[1]), 'down', length=1)
L.note(14, 191, 'All SK6812SIDE-A (C5378721): pin 1 DIN, 2 VDD, 3 DOUT, 4 GND. Data runs head to tail.',
       'SPINE_OUT is the end of the chain, on a test point.')

# =====================================================================================
# Page 4: sensors and buzzer
# =====================================================================================
S.frame(12, 14, 112, 100, 'Motion: accelerometer + gyroscope LSM6DS3TR-C (I2C 0x6A)')
u5 = S.part('U5', 58, 58, ref=(-8, -15, 'l'), val=(2, 15, 'l'))
S.connect_all(u5, length=2)
S.connect_all(S.part('C33', 88, 32))
S.connect_all(S.part('C34', 102, 32))
S.note(14, 84, 'SA0 low gives 0x6A; SDx, SCx grounded (no slave sensors); CS high selects I2C.',
       'Pins 10, 11 are soldered but must stay unconnected.',
       'INT1, INT2 are push-pull, active high: INT1 can wake the module (pick-up, tap, tilt).',
       'C33 on VDD, C34 on VDDIO, each beside its pin.')

S.frame(116, 14, 214, 100, 'Compass: magnetometer QMC5883P (I2C 0x2C), on the tail')
u8 = S.part('U8', 162, 54, ref=(-6, -9, 'l'), val=(2, 9, 'l'))
S.connect_all(u8, length=2)
S.connect_all(S.part('C39', 190, 34))
S.connect_all(S.part('C40', 204, 34))
S.note(118, 80, 'Pads 3-8 and 12-15 are NC and left open. No interrupt pin on this part.',
       'C40 (4.7 uF, low ESR, 0603) on C1 is mandatory. C39 decouples VDD.',
       'No copper under or near it on either face; keep steel and magnets away.',
       'Draws 22 uA even when suspended. Needs a figure-of-eight calibration.')

S.frame(218, 14, 318, 100, 'Barometer BMP580 (I2C 0x46)')
u11 = S.part('U11', 264, 56, ref=(-6, -11, 'l'), val=(2, 13, 'l'))
S.connect_all(u11, length=2)
S.connect_all(S.part('C43', 296, 32))
S.connect_all(S.part('C44', 310, 32))
S.note(220, 84, 'CSB high at power-up or I2C is locked out; SDO low gives 0x46;',
       'INT unused, grounded (leave it disabled in firmware).',
       'C43 on VDD, C44 on VDDIO. Vent in the lid must stay open: no wash.')

S.frame(12, 104, 112, 190, 'Temperature and humidity SHT40 (I2C 0x44), tail tip')
u9 = S.part('U9', 58, 140, ref=(-6, -8, 'l'), val=(6, 8, 'l'))
S.connect_all(u9, length=2)
S.connect_all(S.part('C41', 96, 120))
S.note(14, 170, 'On the tip of the tail, which sticks out of the case. No copper under it',
       'and no ground pour round it, so it follows the air and not the board.',
       'It does not stretch the clock: wait 10 ms after asking for a reading.')

S.frame(116, 104, 214, 190, 'Light sensor LTR-303ALS (I2C 0x29), nose')
u10 = S.part('U10', 162, 140, ref=(-6, -8, 'l'), val=(2, 8, 'l'))
S.connect_all(u10, length=2)
S.connect_all(S.part('C42', 200, 120))
S.note(118, 170, 'On the parts side at the nose: the case needs a hole over it.',
       'INT not used. Wait 100 ms after power-up before the first command.')

S.frame(218, 104, 318, 190, 'Buzzer (IO4)')
S.connect_all(S.part('R35', 228, 124))
S.connect_all(S.part('R37', 244, 124))
S.connect_all(S.part('BZ1', 258, 126, ref=(0, -6, 'c'), val=(0, 6, 'c')))
S.connect_all(S.part('D24', 282, 126, rot=90))
S.connect_all(S.part('Q4', 300, 150, ref=(4, -2, 'l'), val=(4, 2, 'l')), length=2)
S.connect_all(S.part('R36', 280, 156))
S.note(220, 170, '3V3 - R35 || R37 - buzzer - Q4 - ground; D24 across the buzzer takes the coil kick.',
       'Passive buzzer, about 12 ohms: drive IO4 with a 4 kHz square wave.',
       'R36 (4.7k) holds Q4 off against the 45k pull-up CircuitPython puts on unclaimed pins.',
       'R35 || R37 (50 ohms) limit the current to 53 mA if the pin is ever left high:',
       '71 mW in each. Take one off for a quieter buzzer; do not fit less than 100R each.')

if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else 'write'
    d.build()
    ok = True
    if mode in ('verify', 'export'):
        ok = d.verify()
    if mode == 'export':
        d.export('output')
    sys.exit(0 if ok else 1)
