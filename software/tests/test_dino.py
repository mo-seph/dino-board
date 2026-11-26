"""Tests for the dino library, the host and the behaviours, on a desktop with a pretend board.

    python3 software/tests/run_tests.py

Plain functions and asserts, so they need nothing installed (pytest also runs them)."""
import json
import math
import os
import random
import re
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SOFTWARE = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(SOFTWARE, "board"))
sys.path.insert(0, os.path.join(SOFTWARE, "sim"))

from dino import colour                                   # noqa: E402
from dino.core import Dino, Reading, height_between       # noqa: E402
from dino.host import Host, MAX_AMPS, AMPS_PER_COLOUR     # noqa: E402
from dino.leds import Leds                                # noqa: E402
from dino.touch import Pad, Slider                        # noqa: E402
from hw_fake import FakeHardware                          # noqa: E402

BEHAVIOURS = os.path.join(SOFTWARE, "board", "behaviours")
DT = 1.0 / 30


def raises(kind, fn, *args):
    try:
        fn(*args)
    except kind as e:
        return str(e)
    raise AssertionError("expected %s" % kind.__name__)


def near(a, b, tol=1e-6):
    return abs(a - b) <= tol


# ---- colour ------------------------------------------------------------------------------------------
def test_colour_three_ways():
    assert colour.parse("red") == (255, 0, 0)
    assert colour.parse(" Red ") == (255, 0, 0)
    assert colour.parse("#ff8800") == (255, 136, 0)
    assert colour.parse((1, 2, 3)) == (1, 2, 3)
    assert colour.parse([300, -5, 20.5]) == (255, 0, 20.5)        # out-of-range numbers are clipped
    assert colour.parse("off") == colour.parse("black") == (0, 0, 0)


def test_colour_errors_say_what_to_do():
    assert "not a colour" in raises(ValueError, colour.parse, "gold")
    assert "red" in raises(ValueError, colour.parse, "gold")
    raises(ValueError, colour.parse, 7)
    raises(ValueError, colour.parse, (1, 2))
    raises(ValueError, colour.parse, "#12")


def test_mix_and_hsv():
    assert colour.mix("off", "white", 0.5) == (127.5, 127.5, 127.5)
    assert colour.mix("red", "blue", -1) == (255, 0, 0)            # amount is clipped
    assert colour.mix("red", "blue", 2) == (0, 0, 255)
    assert colour.hsv(0) == (255, 0, 0)
    assert all(near(a, b) for a, b in zip(colour.hsv(1 / 3), (0, 255, 0)))
    assert all(near(a, b) for a, b in zip(colour.hsv(2 / 3), (0, 0, 255)))
    assert colour.hsv(1.0) == colour.hsv(0.0)                      # it wraps
    assert colour.hsv(0.2, 0, 1) == (255, 255, 255)


# ---- LEDs --------------------------------------------------------------------------------------------
def test_leds_index():
    leds = Leds()
    assert len(leds) == 18
    leds[0] = "red"
    leds[-1] = "blue"
    leds[8.0] = "green"                                            # a whole number written as a float
    assert leds[0] == (255, 0, 0) and leds[17] == (0, 0, 255) and leds[8] == (0, 255, 0)
    assert "0 to 17" in raises(IndexError, leds.__setitem__, 18, "red")
    raises(TypeError, leds.__setitem__, "3", "red")


def test_leds_dot():
    leds = Leds()
    leds.dot(0.0, "white")
    assert leds[0] == (255, 255, 255) and leds[1] == (0, 0, 0)
    leds.clear()
    leds.dot(0.5, "white")                                         # between LEDs 8 and 9
    assert leds[8] == leds[9] == (127, 127, 127) and leds[7] == (0, 0, 0)
    leds.clear()
    leds.dot(1.0, "red", 3)
    assert leds[17] == (255, 0, 0) and leds[16] == (170, 0, 0) and leds[14] == (0, 0, 0)
    leds.fill("blue")
    leds.dot(0.0, "red")                                           # adds: it never darkens
    assert leds[0] == (255, 0, 255)
    leds.dot(5.0, "red")                                           # off the end: clipped, no error
    leds.dot(-1, "red")


def test_leds_bar_fade_gradient():
    leds = Leds()
    leds.bar(0.5, "green")
    assert leds[8] == (0, 255, 0) and leds[9] == (0, 0, 0)
    leds.bar(0.25, "white", "red")                                 # 4.5 LEDs
    assert leds[3] == (255, 255, 255) and leds[4] == (255, 127, 127) and leds[5] == (255, 0, 0)
    leds.bar(0, "white")
    assert all(leds[i] == (0, 0, 0) for i in range(18))
    leds.bar(7, "white")                                           # clipped
    assert all(leds[i] == (255, 255, 255) for i in range(18))
    leds.fade(0.5)
    assert leds[0] == (127, 127, 127)
    leds.gradient("red", "blue")
    assert leds[0] == (255, 0, 0) and leds[17] == (0, 0, 255)


# ---- touch -------------------------------------------------------------------------------------------
def test_pad_edges():
    pad = Pad()
    pad._update(True, DT)
    assert pad.touched and pad.pressed and not pad.released and pad.held == 0
    pad._update(True, DT)
    assert pad.touched and not pad.pressed and near(pad.held, DT)
    pad._update(False, DT)
    assert not pad.touched and pad.released and pad.held == 0
    pad._update(False, DT)
    assert not pad.released


def test_slider():
    s = Slider()
    s._update(True, 0.0, DT)
    assert s.pos == 0 and s.led == 0 and s.speed == 0
    for i in range(1, 31):
        s._update(True, i / 30, DT)                                # head to tail in one second
    assert s.pos == 1 and s.led == 17 and near(s.speed, 1.0, 0.01)
    s._update(False, 0.3, DT)
    assert s.pos == 1 and s.speed == 0                             # keeps where the finger was
    s._update(True, 9, DT)
    assert s.pos == 1                                              # clipped


# ---- the dino object -----------------------------------------------------------------------------------
def fresh():
    return Dino(), Reading()


def test_time_helpers():
    d, r = fresh()
    ticks = 0
    for _ in range(315):                                           # ten and a half seconds
        d._frame(r, DT)
        ticks += d.every(1)
    assert ticks == 10
    assert near(d.time, 10.5, 1e-6)
    d.time = 1.0
    assert near(d.wave(2), 1.0)
    d.time = 2.0
    assert near(d.wave(2), 0.0)


def test_which_way_up():
    d, r = fresh()
    for accel, name in (((1, 0, 0), "nose"), ((-1, 0, 0), "tail"), ((0, 1, 0), "spine"), ((0, -1, 0), "belly"),
                        ((0, 0, 1), "face"), ((0, 0, -1), "underside"), ((0.2, 0.2, 0.1), "underside")):
        r.accel = accel
        d._frame(r, DT)
        assert d.up == name, (accel, d.up)                         # the last one: too little to tell, so no change
    assert d.accel.x == 0.2


def test_free_fall_and_airtime():
    d, r = fresh()
    d._frame(r, DT)
    r.accel = (0.0, 0.05, 0.0)
    seen = 0
    for _ in range(12):                                            # 0.4 s in the air
        d._frame(r, DT)
        seen += d.falling
    assert seen >= 10
    r.accel = (0, 1, 0)
    d._frame(r, DT)
    assert not d.falling and near(d.airtime, 0.4, 0.001)
    r.accel = (0, 0.1, 0)                                          # one short dip is not a fall
    d._frame(r, DT)
    assert not d.falling


def test_shake_tap_still():
    d, r = fresh()
    for _ in range(60):
        d._frame(r, DT)
    assert d.shake < 0.01 and near(d.still, 2.0, 0.05) and not d.tapped
    r.accel = (0, 2.2, 0)                                          # one knock
    d._frame(r, DT)
    assert d.tapped and not d.shaken and d.still == 0
    r.accel = (0, 1, 0)
    d._frame(r, DT)
    assert not d.tapped                                            # not twice for one knock
    events = 0
    for i in range(30):                                            # a second of hard shaking
        r.accel = (1.5 if i % 2 else -1.5, 1, 0)
        d._frame(r, DT)
        events += d.shaken
    assert events == 1 and d.shake > 0.9
    r.accel = (0, 1, 0)
    for _ in range(60):
        d._frame(r, DT)
    assert d.shake < 0.05


def test_hardware_tap_detector_wins():
    d, r = fresh()
    r.tapped = True
    d._frame(r, DT)
    assert d.tapped
    r.tapped = False
    r.accel = (0, 3, 0)
    d._frame(r, DT)
    assert not d.tapped


def test_height_from_pressure():
    assert near(height_between(1013.25, 1013.25 - 1.2), 10.0, 0.2)   # about 12 Pa to the metre
    d, r = fresh()
    d._frame(r, DT)
    assert d.height == 0
    r.pressure -= 0.3
    d._frame(r, DT)
    assert near(d.height, 2.5, 0.1)
    d.zero_height()
    assert d.height == 0
    r.pressure += 0.12
    d._frame(r, DT)
    assert near(d.height, -1.0, 0.05)


def test_light_heading_magnet():
    d, r = fresh()
    r.lux = 0
    d._frame(r, DT)
    assert d.light == 0
    r.lux = 100000
    d._frame(r, DT)
    assert d.light == 1
    r.lux = 300
    d._frame(r, DT)
    assert 0.5 < d.light < 0.6
    # lying picture side up, seen from above: the nose points left on the page and the back is up the page,
    # so the back is a quarter turn clockwise from the nose
    for heading in (0, 90, 180, 270, 45):
        h = math.radians(heading)
        r.mag = (20 * math.cos(h), 20 * math.cos(h + math.pi / 2), -40)   # field along the nose, along the back, down
        d._frame(r, DT)
        assert near(d.heading, heading, 1e-6) or near(d.heading, heading + 360, 1e-6), (heading, d.heading)
    assert near(d.magnet, math.sqrt(20 * 20 + 40 * 40))


def test_eye_brightness_sound():
    d, r = fresh()
    d.eye = "#102030"
    assert d.eye == (16, 32, 48)
    d.brightness = 7
    assert d.brightness == 1
    d.beep()
    assert d._take_sound() == ("tone", 4000, 0.1) and d._take_sound() is None
    d.tone(5, 1)
    assert d._take_sound()[1] == 50                                # pitches are kept to what a buzzer can do
    d.quiet()
    assert d._take_sound() == ("quiet",)


# ---- the host ----------------------------------------------------------------------------------------
class Rig:
    """A host on a pretend board, with its own folders."""

    def __init__(self, copy_behaviours=True):
        self.dir = tempfile.mkdtemp()
        self.behaviours = os.path.join(self.dir, "behaviours")
        if copy_behaviours:
            shutil.copytree(BEHAVIOURS, self.behaviours)
        else:
            os.mkdir(self.behaviours)
        self.new_host()

    def new_host(self):
        """As if the board had been switched off and on."""
        self.hw = FakeHardware()
        self.host = Host(self.hw, self.behaviours, os.path.join(self.dir, "saved"))
        self.i = self.hw.inputs
        return self.host

    def frames(self, n=1):
        for _ in range(n):
            self.hw.tick(DT)
            self.host.step()

    def seconds(self, s):
        self.frames(int(round(s * 30)))

    def tap(self, pad):
        self.i.pads[pad] = True
        self.frames(2)
        self.i.pads[pad] = False
        self.frames(2)

    def choose(self, number):
        """The menu gesture: hold the snout, slide along the back to LED `number`, let go."""
        self.i.pads["snout"] = True
        self.frames(2)
        self.i.slider_touched, self.i.slider_pos = True, 0.5
        self.frames(2)
        assert self.host.menu
        self.i.slider_pos = (number - 1) / 17
        self.frames(2)
        self.i.slider_touched = False
        self.frames(1)
        self.i.pads["snout"] = False
        self.frames(1)

    def lit(self):
        return sum(1 for p in self.hw.pixels if max(p) > 0)

    def close(self):
        shutil.rmtree(self.dir)


def with_rig(fn):
    def test():
        rig = Rig()
        try:
            fn(rig)
        finally:
            rig.close()
    test.__name__ = fn.__name__
    return test


@with_rig
def test_host_loads_all_behaviours(rig):
    rig.host.start()
    loaded = [s for s in rig.host.slots if s.space is not None]
    assert [s.number for s in loaded] == [1, 2, 3, 4, 5, 6, 7, 8]
    assert [s.error for s in loaded] == [None] * 8
    assert loaded[0].name == "Marble" and loaded[0].colour == "orange"
    assert rig.host.current.number == 1 and rig.host.running


@with_rig
def test_menu_gesture_chooses(rig):
    rig.host.start()
    rig.i.pads["snout"] = True
    rig.frames(3)
    assert not rig.host.menu                                       # the snout alone is the behaviour's
    rig.i.slider_touched, rig.i.slider_pos = True, 6 / 17
    rig.frames(3)
    assert rig.host.menu and rig.host.cursor == 6
    assert rig.hw.pixels[6] != (0, 0, 0) and max(rig.hw.pixels[6]) > 4 * max(rig.hw.pixels[0])   # cursor is brightest
    assert rig.hw.pixels[12] == (0, 0, 0)                          # empty slots are dark
    rig.i.slider_touched = False
    rig.frames(1)
    assert not rig.host.menu and rig.host.current.number == 7      # LED 7: the timer
    rig.i.pads["snout"] = False
    rig.frames(5)
    rig.choose(2)
    assert rig.host.current.number == 2


@with_rig
def test_menu_on_an_empty_slot_changes_nothing(rig):
    rig.host.start()
    rig.frames(10)
    time_before = rig.host.dino.time
    rig.choose(15)
    assert rig.host.current.number == 1 and rig.host.running
    assert rig.host.dino.time > time_before                        # not restarted
    assert rig.host.dino.brightness == 0.3


@with_rig
def test_error_in_update_is_caught_and_shown(rig):
    rig.host.start()
    bad = 'NAME = "Bad"\n\ndef update(dino):\n    dino.leds.fill("red")\n    dino.leds[20] = "red"\n'
    assert rig.host.load_source(9, bad, "09_bad.py")
    rig.host.select(9)
    rig.frames(1)
    slot = rig.host.slots[8]
    assert not rig.host.running and slot.line == 5
    assert "no LED 20" in slot.error and slot.error.startswith("line 5: IndexError")
    rig.seconds(0.1)
    assert rig.hw.pixels[8][0] > 0 and rig.lit() == 1 and rig.hw.eye[0] > 0     # its LED blinks red
    rig.seconds(0.5)
    assert rig.lit() == 0
    rig.choose(1)                                                  # and the menu still works
    assert rig.host.running and rig.host.current.number == 1


@with_rig
def test_errors_on_loading(rig):
    assert not rig.host.load_source(9, "def update(dino)\n    pass\n", "09_typo.py")
    assert rig.host.slots[8].error.startswith("line 1: SyntaxError")
    assert not rig.host.load_source(10, "x = 1\n", "10_empty.py")
    assert "update(dino)" in rig.host.slots[9].error
    assert not rig.host.load_source(11, 'COLOUR = "gold"\ndef update(dino):\n    pass\n', "11_colour.py")
    assert "not a colour" in rig.host.slots[10].error
    assert not rig.host.load_source(12, 'import board\ndef update(dino):\n    pass\n', "12_import.py")
    assert "line 1" in rig.host.slots[11].error
    rig.host.select(9)
    rig.frames(3)                                                  # an unloadable slot can be chosen: it shows its error
    assert not rig.host.running


@with_rig
def test_error_in_init(rig):
    rig.host.load_source(9, "def init(dino):\n    dino.my.x = 1 / 0\n\ndef update(dino):\n    pass\n", "09_init.py")
    rig.host.select(9)
    rig.frames(2)
    assert not rig.host.running and rig.host.slots[8].error.startswith("line 2: ZeroDivisionError")


@with_rig
def test_no_init_is_fine_and_reload_restarts(rig):
    rig.host.load_source(9, 'def update(dino):\n    dino.leds.fill("green")\n', "09_green.py")
    rig.host.select(9)
    rig.frames(2)
    assert rig.host.running and rig.hw.pixels[0][1] > 0 and rig.host.slots[8].name == "green"
    rig.host.load_source(9, 'def update(dino):\n    dino.leds.fill("blue")\n')     # a new version, as from the web page
    rig.frames(2)
    assert rig.host.running and rig.hw.pixels[0] == (0, 0, int(255 * 0.3))
    assert rig.host.slots[8].file == "09_green.py"


@with_rig
def test_led_current_is_limited(rig):
    rig.host.load_source(9, 'def update(dino):\n    dino.brightness = 1\n    dino.leds.fill("white")\n    dino.eye = "white"\n')
    rig.host.select(9)
    rig.frames(2)
    amps = (sum(sum(p) for p in rig.hw.pixels) + sum(rig.hw.eye)) / 255 * AMPS_PER_COLOUR
    assert 0.9 * MAX_AMPS < amps <= MAX_AMPS, amps
    rig.host.load_source(9, 'def update(dino):\n    dino.brightness = 1\n    dino.leds[0] = "white"\n')
    rig.frames(2)
    assert rig.hw.pixels[0] == (255, 255, 255)                     # one LED alone may be full


@with_rig
def test_sounds_stop_by_themselves(rig):
    rig.host.load_source(9, "def update(dino):\n    if dino.snout.pressed:\n        dino.tone(880, 0.2)\n")
    rig.host.select(9)
    rig.frames(2)
    rig.i.pads["snout"] = True
    rig.frames(1)
    assert rig.hw.hz == 880
    rig.seconds(0.15)
    assert rig.hw.hz == 880
    rig.seconds(0.1)
    assert rig.hw.hz == 0


@with_rig
def test_saved_survives_switching_and_power(rig):
    src = ('def init(dino):\n    dino.saved["runs"] = dino.saved.get("runs", 0) + 1\n\n'
           'def update(dino):\n    dino.leds.bar(dino.saved["runs"] / 18, "white")\n')
    rig.host.load_source(9, src, "09_count.py")
    rig.host.select(9)
    rig.frames(2)
    rig.host.select(1)
    rig.host.select(9)
    assert rig.host.dino.saved == {"runs": 2}
    host = rig.new_host()                                          # off and on again
    host.load_source(9, src, "09_count.py")
    host.start()
    assert host.current.number == 9                                # it remembers what was running
    assert host.dino.saved == {"runs": 3}
    assert rig.host.storage_ok


@with_rig
def test_read_only_storage_does_not_stop_anything(rig):
    rig.host.saved_dir = "/nowhere/that/exists/saved"
    rig.host.start()
    rig.choose(2)
    rig.seconds(1)
    assert rig.host.running and not rig.host.storage_ok


@with_rig
def test_nothing_to_run(rig):
    empty = Rig(copy_behaviours=False)
    try:
        empty.host.start()
        empty.seconds(1)
        assert empty.host.current is None and empty.lit() == 0 and max(empty.hw.eye) > 0     # the eye breathes
        assert empty.host.status()["current"] is None
    finally:
        empty.close()


@with_rig
def test_status_is_plain_data(rig):
    rig.host.start()
    text = json.dumps(rig.host.status())
    assert '"name": "Marble"' in text and '"current": 1' in text


# ---- the behaviours ------------------------------------------------------------------------------------
@with_rig
def test_marble_rolls_downhill(rig):
    rig.host.start()
    rig.i.accel = (-0.7, 0.7, 0)                                   # nose down
    rig.seconds(4)
    brightest = max(range(18), key=lambda i: sum(rig.hw.pixels[i]))
    assert brightest <= 1 and rig.hw.notes                         # at the head, and it clicked on the way
    notes = len(rig.hw.notes)
    rig.seconds(5)
    assert len(rig.hw.notes) == notes                              # resting there, it is quiet
    rig.i.accel = (0.7, 0.7, 0)
    rig.seconds(4)
    assert max(range(18), key=lambda i: sum(rig.hw.pixels[i])) >= 16


@with_rig
def test_reaction_timer(rig):
    rig.host.start()
    rig.host.select(2)
    rig.frames(2)
    assert rig.hw.eye[0] > 0 and rig.hw.eye[1] == 0                # red: wait
    go_at = rig.host.dino.my.go_at
    assert 2 <= go_at <= 5.1
    while rig.host.dino.time - go_at < 0.25:                       # a quarter of a second after "go"
        rig.frames(1)
    assert rig.hw.eye[1] > 0 and rig.hw.eye[0] == 0                # green: go
    rig.i.pads["snout"] = True
    rig.frames(1)
    best = rig.host.dino.saved["best"]
    assert 0.25 <= best < 0.33
    assert 9 <= rig.lit() <= 12                                    # about half the row for a quarter of a second


@with_rig
def test_timer_counts_down_and_rings(rig):
    rig.host.start()
    rig.host.select(7)
    rig.i.slider_touched, rig.i.slider_pos = True, 0.0             # one minute
    rig.frames(3)
    rig.i.slider_touched = False
    rig.frames(2)
    assert rig.lit() == 1
    rig.tap("snout")
    assert rig.lit() == 18
    rig.seconds(30)
    assert 9 <= rig.lit() <= 10
    notes = len(rig.hw.notes)
    rig.seconds(32)
    assert len(rig.hw.notes) > notes + 2                           # ringing
    rig.tap("snout")
    notes = len(rig.hw.notes)
    rig.seconds(2)
    assert len(rig.hw.notes) == notes and rig.lit() == 1           # stopped, back to choosing


@with_rig
def test_jump_height(rig):
    rig.host.start()
    rig.host.select(3)
    rig.seconds(0.5)
    rig.i.accel = (0, 0.02, 0)
    rig.seconds(0.4)                                               # 0.4 s in the air: 9.81 * 0.16 / 8 = 0.196 m
    rig.i.accel = (0, 1, 0)
    rig.frames(2)
    assert near(rig.host.dino.my.height, 0.196, 0.035)
    assert 7 <= rig.lit() <= 9                                     # 2.5 cm a light
    assert near(rig.host.dino.saved["best"], rig.host.dino.my.height)


@with_rig
def test_stair_climber(rig):
    rig.host.start()
    rig.host.select(4)
    rig.seconds(1)
    rig.tap("snout")
    rig.i.pressure -= 0.24                                         # two metres up
    rig.seconds(4)
    assert 7 <= rig.lit() <= 9                                     # 25 cm a light


@with_rig
def test_magnet_hunt(rig):
    rig.host.start()
    rig.host.select(5)
    rig.seconds(1)
    assert rig.lit() == 0
    rig.i.mag = (20, -43, 600)                                     # a magnet close by
    rig.seconds(1)
    assert rig.lit() >= 12 and rig.hw.notes


@with_rig
def test_colour_mixer(rig):
    rig.host.start()
    rig.host.select(6)
    rig.i.pads["front_flipper"] = rig.i.pads["tail"] = True        # red and blue
    rig.seconds(1)
    r, g, b = rig.hw.pixels[10]
    assert r > 0 and b > 0 and g == 0 and r == b
    assert rig.hw.pixels[0][0] > 0 and rig.hw.pixels[1] == (0, 0, 0) and rig.hw.pixels[2][2] > 0


@with_rig
def test_weather_tail(rig):
    rig.host.start()
    rig.host.select(8)
    rig.i.temperature = 20
    rig.frames(3)
    assert rig.lit() == 9
    rig.i.pads["rear_flipper"], rig.i.humidity = True, 100
    rig.frames(3)
    assert rig.lit() == 18


@with_rig
def test_every_behaviour_survives_random_handling(rig):
    """Twenty minutes of a pretend child with every behaviour: no errors, no nonsense colours, not too many beeps."""
    rig.host.start()
    random.seed(1)
    for slot in [s for s in rig.host.slots if s.space is not None]:
        rig.host.select(slot.number)
        notes = len(rig.hw.notes)
        for frame in range(36000):
            i = rig.i
            for pad in ("tail", "front_flipper", "rear_flipper"):
                if random.random() < 0.02:
                    i.pads[pad] = not i.pads[pad]
            if random.random() < 0.02:                             # never the snout and the slider together:
                i.pads["snout"] = not i.pads["snout"] and not i.slider_touched     # that is the menu
            if random.random() < 0.02:
                i.slider_touched = not i.slider_touched and not i.pads["snout"]
            i.slider_pos = min(max(i.slider_pos + random.uniform(-0.05, 0.05), 0), 1)
            t = frame / 30
            i.accel = (math.sin(t / 3), math.cos(t / 3), 0.0) if frame % 900 > 12 else (0, 0, 0)
            i.temperature, i.humidity = 20 + 25 * math.sin(t / 50), 50 + 50 * math.sin(t / 70)
            i.pressure = 1013 + 2 * math.sin(t / 90)
            i.mag = (20, -43, 500 * max(math.sin(t / 15), 0))
            rig.hw.tick(random.uniform(0.02, 0.05))
            rig.host.step()
            assert rig.host.running, (slot.name, slot.error)
            assert all(0 <= v <= 255 for p in rig.hw.pixels for v in p)
        assert rig.host.current is slot
        assert len(rig.hw.notes) - notes < 36000 * 0.1, slot.name


# ---- the documents -------------------------------------------------------------------------------------
def code_blocks(name):
    text = open(os.path.join(SOFTWARE, name)).read()
    return [b for b in re.findall(r"```python\n(.*?)```", text, re.S) if "def update" in b and "..." not in b]


def test_prompt_examples_are_the_real_behaviours():
    files = {"Marble": "01_marble.py", "Reaction timer": "02_reaction_timer.py", "Timer": "07_timer.py"}
    seen = set()
    for block in code_blocks("PROMPT.md"):
        name = re.search(r'NAME = "([^"]+)"', block).group(1)
        if name in files:
            assert block == open(os.path.join(BEHAVIOURS, files[name])).read(), name + " differs from PROMPT.md"
            seen.add(name)
    assert seen == set(files)


@with_rig
def test_every_example_in_the_documents_runs(rig):
    for doc in ("PROMPT.md", "API.md"):
        for block in code_blocks(doc):
            assert rig.host.load_source(18, block, "18_example.py"), rig.host.slots[17].error
            rig.host.select(18)
            rig.seconds(20)
            assert rig.host.running, rig.host.slots[17].error


def test_everything_the_prompt_promises_exists():
    """Each dino.<name> in the reference part of PROMPT.md is a real thing on the object."""
    text = open(os.path.join(SOFTWARE, "PROMPT.md")).read()
    reference = text[text.index("## What `dino` gives you"):text.index("## Examples")]
    d, r = fresh()
    d._frame(r, DT)
    names = set(re.findall(r"dino\.([a-z_]+)", reference))
    assert len(names) > 30, len(names)
    for name in sorted(names):
        assert hasattr(d, name), "PROMPT.md promises dino.%s" % name
    for name in set(re.findall(r"dino\.leds\.([a-z_]+)", reference)):
        assert hasattr(d.leds, name), "PROMPT.md promises dino.leds.%s" % name
    for name in ("touched", "pressed", "released", "held", "pos", "led", "speed"):
        assert hasattr(d.slider, name)


# ---- the simulator page ----------------------------------------------------------------------------------
WEB = os.path.join(os.path.dirname(SOFTWARE), "web")


def test_behaviour_index_matches_the_folder():
    listed = json.load(open(os.path.join(BEHAVIOURS, "index.json")))
    assert listed == sorted(f for f in os.listdir(BEHAVIOURS) if f.endswith(".py"))


def test_simulator_page_python_runs_as_the_page_runs_it():
    """The Python that web/sim/index.html hands to Pyodide, run here with the folders the page sets up,
    fed the same JSON the page sends. This cannot test the page's own JavaScript."""
    page = open(os.path.join(WEB, "sim", "index.html")).read()
    for f in re.search(r"const LIB = \[(.*?)\]", page).group(1).replace('"', "").split(", "):
        assert os.path.exists(os.path.join(SOFTWARE, "board", "dino", f)), f
    glue = re.search(r"py\.runPython\(`\n(import sys, json.*?)`\);", page, re.S).group(1)
    tmp = tempfile.mkdtemp()
    try:
        glue = glue.replace('sys.path[:0] = ["/board", "/sim"]', "")
        glue = glue.replace('"/board/behaviours"', repr(BEHAVIOURS)).replace('"/saved"', repr(os.path.join(tmp, "saved")))
        space = {}
        exec(glue, space)
        inputs = re.search(r"const inp = (\{.*?\});", page, re.S).group(1)
        inputs = re.sub(r"([{,]\s*)([a-z_]+):", r'\1"\2":', inputs)                 # JavaScript object -> JSON
        data = json.loads(inputs)
        for frame in range(90):
            data["accel"] = [-0.7, 0.7, 0]
            out = json.loads(space["frame"](frame / 30, json.dumps(data)))
        assert len(out["pixels"]) == 18 and len(out["eye"]) == 3 and "hz" in out
        assert max(out["pixels"][0]) > 0                                         # the marble has rolled to the head
        status = json.loads(json.dumps(space["host"].status()))
        assert status["current"] == 1 and status["slots"][0]["name"] == "Marble"
        assert space["host"].slots[0].source.startswith('"""Marble')
        assert space["host"].slots[17].source is None
    finally:
        shutil.rmtree(tmp)


def test_simulator_shape_matches_the_board():
    shape = json.load(open(os.path.join(WEB, "sim", "shape.json")))
    assert len(shape["leds"]) == 18 and len(shape["spine"]) == 8
    assert sorted(shape["pads"]) == ["front_flipper", "rear_flipper", "snout", "tail"]
    xs = [p[0] for p in shape["leds"]]
    assert xs == sorted(xs) and xs[0] < 60                                       # LED 1 is at the head (the left)
    assert shape["pads"]["snout"][0][0][0] < 40 and shape["pads"]["tail"][0][0][0] > 180


def test_website_pages_point_at_real_things():
    prompt_page = open(os.path.join(WEB, "prompt.html")).read()
    mark = re.search(r'const MARK = "(.*?)";', prompt_page).group(1)
    assert open(os.path.join(SOFTWARE, "PROMPT.md")).read().count(mark) == 1      # where the idea goes
    for page in ("index.html", "prompt.html", os.path.join("sim", "index.html")):
        text = open(os.path.join(WEB, page)).read()
        for link in re.findall(r'href="([^"#:]+)"', text):                       # links within the site
            target = os.path.normpath(os.path.join(WEB, os.path.dirname(page), link))
            assert os.path.exists(target), "%s links to %s" % (page, link)
