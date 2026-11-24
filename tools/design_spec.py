#!/usr/bin/env python3
"""DinoLight: WHAT is on the board. Parts (value, footprint, JLCPCB number) and nets, declared once.
The schematic (tools/schematic.py) draws exactly this; the board is built from the same lists.

Pin numbers come from the datasheets in datasheets/ (see NOTES.md, "Ground truth")."""
import copy
import os
import sys

SKILL = os.path.expanduser('~/.claude/skills/pcb-for-assembly/scripts')
sys.path.insert(0, SKILL)
import schdraw
from schdraw import kid, kids, q, unq

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SYMLIB = os.path.join(ROOT, 'lib', 'DinoLight.kicad_sym')

N_LED = 18                      # spine LEDs D1..D18, D1 at the head (D19, D20 and their capacitors C29, C30 were
                                # taken off on 2026-11-23; the eye keeps the names D21 and C31). Must match outline/make_outline.py
# touch channels, in MPR121 electrode order ELE0..ELE11: (net stem, what it is). ELEn is U7 pin 8 + n.
TOUCH = [('SPINE%d' % (i + 1), 'spine %d' % (i + 1)) for i in range(8)]
# in controller channel order (ELE8..11). The three long lines leave the controller nested, tail outermost,
# so the channel order is not the pad order: ELECTRODE says which pad each one is.
TOUCH += [('SNOUT', 'snout'), ('TAIL', 'tail'), ('FLIP_R', 'rear flipper'), ('FLIP_F', 'front flipper')]
ELECTRODE = {'SNOUT': 'E9', 'FLIP_F': 'E10', 'FLIP_R': 'E11', 'TAIL': 'E12'}
TESTPOINTS = ['GND', '+3V3', '+BATT', 'VBUS', 'VLED', 'UART_TX', 'UART_RX', 'IO3', 'SDA', 'SCL', 'SPINE_OUT',
              'EN', 'LED_EN', 'LDO_EN', 'CHG_STAT', 'EYE_DIN', 'TOUCH_IRQ']


# ------------------------------------------------------------------ project symbols
def _copy_symbol(src_lib, src, new, numbers=None, names=None, add_pin=None, value=None):
    """Copy a stock symbol into the project library under a new name. numbers: {pin name: new number};
    names: {old pin name: new name}; add_pin: (number, name, x_mm, y_mm, angle) cloned from the first pin."""
    text = open(SYMLIB, encoding='utf-8').read() if os.path.exists(SYMLIB) else ''
    if '(symbol "%s"' % new in text:
        return
    stock = schdraw._lib_text(os.path.join(schdraw.STOCK, src_lib + '.kicad_sym'))
    tree = schdraw._symbol_block(stock, src, src_lib)
    if kid(tree, 'extends'):
        raise SystemExit(f'{src} is a derived symbol; copy its parent instead')

    def rename(node):
        return [rename(c) if isinstance(c, list)
                else (q(unq(c).replace(src, new)) if isinstance(c, schdraw.Q) and unq(c).startswith(src) else c)
                for c in node]
    tree = rename(tree)
    for p in kids(tree, 'property'):
        if unq(p[1]) == 'Value' and value:
            p[2] = q(value)
        if unq(p[1]) in ('Footprint', 'Datasheet', 'ki_fp_filters'):
            p[2] = q('')
    units = kids(tree, 'symbol')
    first = None
    for unit in units:
        for p in kids(unit, 'pin'):
            first = first or (unit, p)
            name = unq(kid(p, 'name')[1])
            if numbers and name in numbers:
                kid(p, 'number')[1] = q(numbers[name])
            if names and name in names:
                kid(p, 'name')[1] = q(names[name])
    if add_pin:
        unit, p = first
        new_pin = copy.deepcopy(p)
        number, name, x, y, angle = add_pin
        new_pin[1] = 'passive'
        kid(new_pin, 'at')[1:] = [schdraw.num(x), schdraw.num(y), str(angle)]
        kid(new_pin, 'name')[1] = q(name)
        kid(new_pin, 'number')[1] = q(number)
        unit.append(new_pin)
    block = schdraw.dump(tree, 1)
    if text:
        text = text.rstrip()
        text = text[:text.rindex(')')].rstrip() + '\n\t' + block + '\n)\n'
    else:
        text = ('(kicad_symbol_lib\n\t(version 20241209)\n\t(generator "schdraw")\n'
                '\t(generator_version "9.0")\n\t' + block + '\n)\n')
    os.makedirs(os.path.dirname(SYMLIB), exist_ok=True)
    with open(SYMLIB, 'w', encoding='utf-8') as f:
        f.write(text)
    schdraw._LIB_CACHE.pop(SYMLIB, None)


def _box_symbol(name, left, right, description):
    """A plain rectangle symbol in the project library. left / right: [(number, name, type)] top to bottom;
    type is a KiCad pin type (power_in, input, bidirectional, passive, output, no_connect...)."""
    text = open(SYMLIB, encoding='utf-8').read() if os.path.exists(SYMLIB) else ''
    if '(symbol "%s"' % name in text:
        return
    rows = max(len(left), len(right))
    top = 2.54 * (rows // 2)
    font = '(effects (font (size 1.27 1.27)))'

    def prop(key, value, y, hide=False):
        return '(property "%s" "%s" (at 0 %s 0) %s%s)' % (key, value, schdraw.num(y), '(hide yes) ' if hide else '', font)

    pins = []
    for side, x, angle in ((left, -10.16, 0), (right, 10.16, 180)):
        for i, (number, pname, ptype) in enumerate(side):
            pins.append('(pin %s line (at %s %s %d) (length 2.54) (name "%s" %s) (number "%s" %s))'
                        % (ptype, schdraw.num(x), schdraw.num(top - 2.54 * i), angle, pname, font, number, font))
    block = ('(symbol "%s" (pin_names (offset 1.016)) (exclude_from_sim no) (in_bom yes) (on_board yes)\n\t\t' % name
             + '\n\t\t'.join([prop('Reference', 'U', top + 5.08), prop('Value', name, -top - 5.08), prop('Footprint', '', 0, True),
                                prop('Datasheet', '', 0, True), prop('Description', description, 0, True)])
             + '\n\t\t(symbol "%s_0_1" (rectangle (start -7.62 %s) (end 7.62 %s) (stroke (width 0.254) (type default)) (fill (type background))))'
             % (name, schdraw.num(top + 2.54), schdraw.num(top - 2.54 * rows))
             + '\n\t\t(symbol "%s_1_1"\n\t\t\t' % name + '\n\t\t\t'.join(pins) + '\n\t\t)\n\t)')
    text = text.rstrip()
    text = text[:text.rindex(')')].rstrip() + '\n\t' + block + '\n)\n'
    with open(SYMLIB, 'w', encoding='utf-8') as f:
        f.write(text)
    schdraw._LIB_CACHE.pop(SYMLIB, None)


def ensure_symbols():
    # side LED: same drawing as the MINI-E, pins renumbered to the SIDE-A datasheet (1 DIN 2 VDD 3 DOUT 4 GND)
    _copy_symbol('LED', 'SK6812MINI', 'SK6812SIDE-A', numbers={'DIN': '1', 'VDD': '2', 'DOUT': '3', 'VSS': '4'},
                 names={'VSS': 'GND'}, value='SK6812SIDE-A')
    # eye LED: the same drawing and the same pin numbers (SK6812MINI-012 datasheet: 1 DIN 2 VDD 3 DOUT 4 GND)
    _copy_symbol('LED', 'SK6812MINI', 'SK6812MINI-012', numbers={'DIN': '1', 'VDD': '2', 'DOUT': '3', 'VSS': '4'},
                 names={'VSS': 'GND'}, value='SK6812MINI-012')
    # slide switch: SPDT plus its metal frame (datasheet circuit: 2 is the common, 4 the frame)
    _copy_symbol('Switch', 'SW_SPDT', 'MSK12C02', add_pin=('SH', 'SH', 0, -5.08, 90), value='MSK12C02')
    schdraw.make_power_symbol(SYMLIB, 'VLED', like='+3V3')
    # magnetometer: pins from QST's datasheet 13-52-19 Rev A (LGA-16; every pad not listed is NC, left open)
    _box_symbol('QMC5883P', [('2', 'VDD', 'power_in'), ('10', 'C1', 'passive'), ('9', 'GND', 'power_in'), ('11', 'GND', 'power_in')],
                [('1', 'SCK', 'input'), ('16', 'SDA', 'bidirectional')], 'QST QMC5883P 3-axis magnetometer, I2C 0x2C')
    # barometer: pins from Bosch BST-BMP580-DS004 (LGA-10)
    _box_symbol('BMP580', [('10', 'VDD', 'power_in'), ('1', 'VDDIO', 'power_in'), ('6', 'CSB', 'input'), ('5', 'SDO', 'input'),
                           ('3', 'VSS', 'power_in'), ('8', 'VSS', 'power_in'), ('9', 'VSS', 'power_in')],
                [('2', 'SCK', 'input'), ('4', 'SDI', 'bidirectional'), ('7', 'INT', 'passive')], 'Bosch BMP580 pressure sensor, I2C 0x46 / 0x47')


# ------------------------------------------------------------------ parts and nets
R0603 = 'Resistor_SMD:R_0603_1608Metric'
R0805, C0603 = 'Resistor_SMD:R_0805_2012Metric', 'Capacitor_SMD:C_0603_1608Metric'
R0402, C0402, C0805 = 'Resistor_SMD:R_0402_1005Metric', 'Capacitor_SMD:C_0402_1005Metric', 'Capacitor_SMD:C_0805_2012Metric'
SOT23 = 'Package_TO_SOT_SMD:SOT-23'
RES = {'2.2k': 'C25879', '1k': 'C11702', '330R': 'C25104', '470R': 'C25117', '4.7k': 'C25900', '5.1k': 'C25905', '10k': 'C25744', '100k': 'C25741',
       '200k': 'C25764', '1M': 'C26083'}
CAP = {'100nF': (C0402, 'C1525'), '10uF': (C0805, 'C15850'), '1uF': (C0402, 'C52923'), '4.7uF': (C0603, 'C19666'),
       '22uF': (C0805, 'C45783')}


def declare(d):
    ensure_symbols()
    d.power_net('VBUS')
    d.power_net('+BATT')
    d.power_net('VLED', 'DinoLight:VLED')

    def r(refs, value):
        for ref in refs.split():
            d.comp(ref, 'Device:R', value, R0402, lcsc=RES[value])

    def c(refs, value):
        for ref in refs.split():
            d.comp(ref, 'Device:C', value, CAP[value][0], lcsc=CAP[value][1])

    # connectors
    d.comp('J1', 'Connector:USB_C_Receptacle_USB2.0_16P', 'USB-C', 'Connector_USB:USB_C_Receptacle_HRO_TYPE-C-31-M-12', lcsc='C165948')
    d.comp('J2', 'Connector_Generic_MountingPin:Conn_01x02_MountingPin', 'LiPo JST-PH',
           'Connector_JST:JST_PH_S2B-PH-SM4-TB_1x02-1MP_P2.00mm_Horizontal', lcsc='C295747')
    d.comp('J3', 'Connector_Generic_MountingPin:Conn_01x04_MountingPin', 'Qwiic',
           'Connector_JST:JST_SH_SM04B-SRSS-TB_1x04-1MP_P1.00mm_Horizontal', lcsc='C160404')
    # ICs
    d.comp('U1', 'Power_Protection:USBLC6-2SC6', 'USBLC6-2SC6', 'Package_TO_SOT_SMD:SOT-23-6', lcsc='C7519')
    d.comp('U2', 'Battery_Management:MCP73831-2-OT', 'MCP73831T-2ACI/OT', 'Package_TO_SOT_SMD:SOT-23-5', lcsc='C424093')
    d.comp('U3', 'Regulator_Linear:XC6220B331MR', 'XC6220B331MR-G', 'Package_TO_SOT_SMD:SOT-23-5', lcsc='C86534')
    d.comp('U4', 'RF_Module:ESP32-S3-MINI-1', 'ESP32-S3-MINI-1-N8', 'RF_Module:ESP32-S2-MINI-1', lcsc='C2913206')
    # touch controller: 12 channels on I2C (0x5C), interrupt can wake the module
    d.comp('U7', 'Sensor_Touch:MPR121QR2', 'MPR121QR2', 'Package_DFN_QFN:UQFN-20_3x3mm_P0.4mm', lcsc='C91322')
    d.comp('R33', 'Device:R', '75k 1%', R0603, lcsc='C23242')      # MPR121 reference current; 0603 is the basic part
    # supervisor: holds the module in reset below 2.93 V so a flat cell can take the charger's trickle
    d.comp('U6', 'Power_Supervisor:TPS3839DBZ', 'TLV803SDBZR', SOT23, lcsc='C132016')
    # motion: accelerometer + gyroscope (I2C 0x6A); with the magnetometer U8 that makes nine axes
    d.comp('U5', 'Sensor_Motion:LSM6DS3', 'LSM6DS3TR-C', 'Package_LGA:LGA-14_3x2.5mm_P0.5mm_LayoutBorder3x4y', lcsc='C967633')
    d.comp('U8', 'DinoLight:QMC5883P', 'QMC5883P', 'Package_LGA:LGA-16_3x3mm_P0.5mm', lcsc='C2847467')         # compass, 0x2C
    d.comp('U9', 'Sensor_Humidity:SHT4x', 'SHT40-AD1B', 'Sensor_Humidity:Sensirion_DFN-4_1.5x1.5mm_P0.8mm_SHT4x_NoCentralPad',
           lcsc='C2909890')                                                                                     # temperature, humidity, 0x44
    d.comp('U10', 'Sensor_Optical:LTR-303ALS-01', 'LTR-303ALS-01', 'OptoDevice:Lite-On_LTR-303ALS-01', lcsc='C364577')   # light, 0x29
    d.comp('U11', 'DinoLight:BMP580', 'BMP580', 'DinoLight:Bosch_LGA-10_2x2mm_P0.5mm_BMP580', lcsc='C22391138')  # pressure, 0x46
    # buzzer: passive, about 12 ohms, driven at 4 kHz through Q4 (logic-level: fully on from a 3.3 V pin).
    # R35 and R37 in parallel (50 ohms) limit the current if firmware ever leaves the pin high: 53 mA,
    # 71 mW in each 125 mW resistor. Take one off by hand for a quieter buzzer.
    d.comp('BZ1', 'Device:Buzzer', 'MLT-5020', 'DinoLight:Buzzer_MLT-5020', lcsc='C94598')
    d.comp('Q4', 'Transistor_FET:AO3400A', 'AO3400A', SOT23, lcsc='C20917')
    d.comp('D24', 'Device:D', '1N4148W', 'Diode_SMD:D_SOD-123', lcsc='C81598')
    for ref in ('R35', 'R37'):
        d.comp(ref, 'Device:R', '100R', R0805, lcsc='C17408')
    d.comp('Q1', 'Transistor_FET:AO3401A', 'AO3401A', SOT23, lcsc='C15127')
    d.comp('Q2', 'Transistor_FET:AO3401A', 'AO3401A', SOT23, lcsc='C15127')
    d.comp('Q3', 'Transistor_FET:2N7002', '2N7002', SOT23, lcsc='C8545')
    # stops the battery feeding back onto VBUS through R4 when SW1 is on
    d.comp('D23', 'Device:D', '1N4148W', 'Diode_SMD:D_SOD-123', lcsc='C81598')
    d.comp('F1', 'Device:Polyfuse', '1.1A', 'Fuse:Fuse_1812_4532Metric', lcsc='C21000')
    d.comp('SW1', 'DinoLight:MSK12C02', 'MSK12C02', 'Button_Switch_SMD:SW_SPDT_Shouhan_MSK12C02', lcsc='C431540')
    d.comp('SW2', 'Switch:SW_Push', 'RESET', 'Button_Switch_SMD:SW_Push_1P1T_XKB_TS-1187A', lcsc='C318884')
    d.comp('SW3', 'Switch:SW_Push', 'BOOT', 'Button_Switch_SMD:SW_Push_1P1T_XKB_TS-1187A', lcsc='C318884')
    for i in range(1, N_LED + 1):
        d.comp('D%d' % i, 'DinoLight:SK6812SIDE-A', 'SK6812SIDE-A', 'DinoLight:LED_SK6812SIDE-A_4.0x1.6mm', lcsc='C5378721')
    # the eye: an ordinary top-emitting LED on the parts side, shining away from the board through a hole in
    # the printed case (the owner, 2026-11-23: "not a reverse light thing"). OPSCO SK6812MINI-012, 3.7 x 3.5 mm.
    # Pins 1 DIN, 2 VDD, 3 DOUT, 4 GND (datasheet Rev B/0, section 5): the same numbers as the side LED.
    d.comp('D21', 'DinoLight:SK6812MINI-012', 'SK6812MINI-012', 'DinoLight:LED_SK6812MINI-012_3.7x3.5mm', lcsc='C2886570')
    # passives
    r('R1 R2', '5.1k')
    # R12, R36: gate pull-downs. 4.7k, not 100k: CircuitPython puts a 45k pull-up on every pin the program has
    # not claimed, and against 100k that half-turns-on the LED rail switch and the buzzer (review 4)
    r('R3 R12 R36', '4.7k')
    r('R17 R18', '2.2k')            # I2C pull-ups: the bus runs nose to tail with seven devices on it
    r('R6 R7', '1M')
    r('R4 R5 R9 R19', '200k')
    r('R8 R10 R11 R16 R34', '100k')
    r('R13', '10k')
    r('R32', '1k')
    r('R14 R15', '330R')
    r(' '.join('R%d' % (20 + i) for i in range(len(TOUCH))), '470R')
    c('C1 C2 C4 C8 C9', '10uF')
    # C3: the XC6220 wants 10 uF of real input capacitance (its table: with 4.7 uF in, 47 uF out).
    # C5: the module datasheet's 22 uF, at the module's supply pin.
    c('C3 C5', '22uF')
    c('C42', '1uF')
    c('C40', '4.7uF')
    c('C6 C7 C10 C32 C33 C34 C36 C37 C38 C39 C41 C43 C44 ' + ' '.join('C%d' % (10 + i) for i in range(1, N_LED + 1)) + ' C31', '100nF')
    # board features with nothing to buy
    for ref in ('SJ1', 'SJ2'):
        d.comp(ref, 'Jumper:SolderJumper_3_Bridged12', 'polarity',
               'Jumper:SolderJumper-3_P1.3mm_Bridged12_RoundedPad1.0x1.5mm', nobom=True)
    for i, (stem, what) in enumerate(TOUCH, 1):
        d.comp(ELECTRODE.get(stem, 'E%d' % i), 'Connector:TestPoint', what, 'DinoLight:TouchAnchor', nobom=True)
    for i, net in enumerate(TESTPOINTS, 1):
        d.comp('TP%d' % i, 'Connector:TestPoint', net, 'TestPoint:TestPoint_Pad_D1.5mm', nobom=True)
    for i in (1, 2):
        d.comp('H%d' % i, 'Mechanical:MountingHole', 'M2.5', 'MountingHole:MountingHole_2.7mm_M2.5', nobom=True)

    n = d.net
    u4_gnd = ['U4.%d' % p for p in (1, 2, 42, 43) + tuple(range(46, 66))]
    n('GND', 'J1.A1', 'J1.A12', 'J1.B1', 'J1.B12', 'J1.SH', 'R1.2', 'R2.2', 'U1.2', 'C1.2', 'U2.2', 'R3.2', 'C2.2', 'R19.2',
      'J2.MP', 'SJ1.3', 'SJ2.1', 'Q1.1', 'C3.2', 'U3.2', 'C4.2', 'SW1.SH', 'R5.2', 'R7.2', 'C7.2', 'R9.2',
      *u4_gnd, 'C5.2', 'C6.2', 'C32.2', 'SW2.2', 'SW3.2', 'U6.1', 'C36.2', 'U7.6', 'C37.2', 'C38.2', 'R33.2', 'U5.1', 'U5.2', 'U5.3', 'U5.6', 'U5.7', 'C33.2', 'C34.2',
      'U8.9', 'U8.11', 'C39.2', 'C40.2', 'U9.4', 'C41.2', 'U10.3', 'C42.2', 'U11.3', 'U11.5', 'U11.7', 'U11.8', 'U11.9', 'C43.2', 'C44.2',
      'Q4.2', 'R36.2',
      'J3.1', 'J3.MP', 'Q3.2', 'R12.2', 'C8.2', 'C9.2', 'D21.4', 'C31.2', 'TP1.1',
      *['D%d.4' % i for i in range(1, N_LED + 1)], *['C%d.2' % (10 + i) for i in range(1, N_LED + 1)])
    n('VBUS', 'J1.A4', 'J1.A9', 'J1.B4', 'J1.B9', 'U1.5', 'C1.1', 'U2.4', 'D23.2', 'R8.1', 'TP4.1')
    n('EN_USB', 'D23.1', 'R4.1')
    n('+BATT', 'Q1.2', 'U2.3', 'C2.1', 'SW1.1', 'U3.1', 'C3.1', 'R6.1', 'Q2.2', 'R11.1', 'TP3.1')
    n('+3V3', 'U3.5', 'C4.1', 'U4.3', 'C5.1', 'C6.1', 'R16.1', 'U5.5', 'U5.8', 'U5.12', 'C33.1', 'C34.1',
      'U8.2', 'C39.1', 'U9.3', 'C41.1', 'U10.1', 'C42.1', 'U11.1', 'U11.6', 'U11.10', 'C43.1', 'C44.1', 'R35.1', 'R37.1',
      'R17.1', 'R18.1', 'J3.2', 'TP2.1', 'U6.3', 'C36.1', 'U7.20', 'C37.1', 'R34.1')
    n('VLED', 'Q2.3', 'C8.1', 'C9.1', 'C10.2', 'D21.2', 'C31.1', 'TP5.1',
      *['D%d.2' % i for i in range(1, N_LED + 1)], *['C%d.1' % (10 + i) for i in range(1, N_LED + 1)])
    # battery input
    n('BAT_P1', 'J2.1', 'F1.1')            # the fuse is in series with the connector pin, ahead of the jumpers
    n('BAT_P1F', 'F1.2', 'SJ1.2')
    n('BAT_P2', 'J2.2', 'SJ2.2')
    n('BAT_RAW', 'SJ1.1', 'SJ2.3', 'Q1.3')
    # USB and charger
    n('CC1', 'J1.A5', 'R1.1')
    n('CC2', 'J1.B5', 'R2.1')
    n('USB_DM', 'J1.A7', 'J1.B7', 'U1.1', 'U1.6', 'U4.23')
    n('USB_DP', 'J1.A6', 'J1.B6', 'U1.3', 'U1.4', 'U4.24')
    n('CHG_PROG', 'U2.5', 'R3.1')
    n('CHG_STAT_5V', 'U2.1', 'R10.1')
    n('CHG_STAT', 'R10.2', 'R19.1', 'U4.21', 'TP15.1')
    # on/off and monitoring
    n('LDO_EN', 'U3.3', 'SW1.2', 'R4.2', 'R5.1', 'TP14.1')
    n('VBAT_SENSE', 'R6.2', 'R7.1', 'C7.1', 'U4.14')
    n('VBUS_DET', 'R8.2', 'R9.1', 'U4.22')
    # module
    n('EN', 'U4.45', 'R16.2', 'C32.1', 'SW2.1', 'R32.2', 'TP12.1')
    n('RST_OD', 'U6.2', 'R32.1')
    n('BOOT', 'U4.4', 'SW3.1')
    n('IO3', 'U4.7', 'TP8.1')
    n('UART_TX', 'U4.39', 'TP6.1')
    n('UART_RX', 'U4.40', 'TP7.1')
    for i, (stem, what) in enumerate(TOUCH):
        n('T_' + stem, 'U7.%d' % (8 + i), 'R%d.1' % (20 + i))
        n('PAD_' + stem, 'R%d.2' % (20 + i), ELECTRODE.get(stem, 'E%d' % (i + 1)) + '.1')
    n('TOUCH_IRQ', 'U7.1', 'R34.2', 'U4.5', 'TP17.1')        # open collector, active low; GPIO1 can wake the module
    n('MPR_VREG', 'U7.5', 'C38.1')
    n('MPR_REXT', 'U7.7', 'R33.1')
    # accelerometer and I2C
    # U7 pin 4 (ADDR) is tied to SDA, the pin beside it: that selects I2C address 0x5C
    n('SDA', 'U4.37', 'U5.14', 'U7.3', 'U7.4', 'R17.2', 'J3.3', 'TP9.1', 'U8.16', 'U9.1', 'U10.6', 'U11.4')
    n('SCL', 'U4.38', 'U5.13', 'U7.2', 'R18.2', 'J3.4', 'TP10.1', 'U8.1', 'U9.2', 'U10.4', 'U11.2')
    n('ACC_INT1', 'U4.19', 'U5.4')                     # push-pull, active high by default
    n('ACC_INT2', 'U4.20', 'U5.9')
    n('MAG_C1', 'U8.10', 'C40.1')                      # the magnetometer's reservoir capacitor (mandatory)
    # buzzer: 3V3 - R35 || R37 - buzzer - Q4 - ground, D24 across the buzzer, R36 holds Q4 off until firmware drives it
    n('BUZ_P', 'R35.2', 'R37.2', 'BZ1.1', 'D24.1')
    n('BUZ_N', 'BZ1.2', 'D24.2', 'Q4.3')
    n('BUZZ', 'U4.8', 'Q4.1', 'R36.1')                 # IO4
    # LEDs
    n('LED_EN', 'U4.25', 'Q3.1', 'R12.1', 'TP13.1')
    n('LED_PULL', 'Q3.3', 'R13.2')
    n('LED_GATE', 'R13.1', 'Q2.1', 'R11.2', 'C10.1')   # C10 gate to drain: sets the rail's rise rate
    n('SPINE_DATA', 'U4.15', 'R14.1')                  # IO11: the pad nearest the first LED
    n('SPINE_DIN', 'R14.2', 'D1.1')
    for i in range(1, N_LED):
        n('SPINE_%d' % i, 'D%d.3' % i, 'D%d.1' % (i + 1))
    n('SPINE_OUT', 'D%d.3' % N_LED, 'TP11.1')
    n('EYE_DATA', 'U4.30', 'R15.1')
    n('EYE_DIN', 'R15.2', 'D21.1', 'TP16.1')
    # deliberately open
    d.nc('J1.A8', 'J1.B8', 'SW1.3', 'D21.3', 'U3.4', 'U10.5',
         *['U4.%d' % p for p in (6, 9, 10, 11, 12, 13, 16, 17, 18, 26, 27, 28, 29, 31, 32, 33, 34, 35, 36, 41, 44)])
