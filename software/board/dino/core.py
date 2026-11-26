"""Dino: everything a behaviour can read and control. The reference for behaviour writers is
software/API.md; keep the two in step.

The host fills a Reading from the hardware each frame and passes it to Dino._frame(), which turns raw
readings into the things behaviours ask for (which way is up, shaken, falling, height, heading...).
Nothing here touches hardware."""
import math

from . import colour
from .leds import Leds
from .touch import Pad, Slider

PAD_NAMES = ("snout", "tail", "front_flipper", "rear_flipper")
DEFAULT_BRIGHTNESS = 0.3
BEEP_HZ = 4000                  # the buzzer's own pitch (MLT-5020, 4 kHz): its loudest
SEA_LEVEL = 1013.25

# Thresholds for the movement events. Tuned on the simulator only: revisit on the real board.
FALL_BELOW_G = 0.35             # total acceleration under this ...
FALL_AFTER = 0.06               # ... for this long, is free fall
SHAKE_FULL = 1.5                # change of acceleration per frame, in g, that counts as shaking flat out
SHAKE_ON, SHAKE_OFF = 0.5, 0.25
TAP_JERK = 0.8
MOVING_JERK, MOVING_SPIN = 0.05, 8.0


class Vec:
    """Three numbers with names: .x .y .z"""

    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.x, self.y, self.z = x, y, z

    def _set(self, v):
        self.x, self.y, self.z = v

    def __repr__(self):
        return "(%.2f, %.2f, %.2f)" % (self.x, self.y, self.z)


class My:
    """An empty object for a behaviour's own variables: dino.my.score = 0"""


class Reading:
    """What the hardware reports each frame, already in the dinosaur's own directions and units.
    x points out of the nose, y out of the back (the LED edge), z out of the picture side."""

    def __init__(self):
        self.pads = {name: False for name in PAD_NAMES}
        self.slider_touched = False
        self.slider_pos = 0.5               # 0 head to 1 tail
        self.accel = (0.0, 1.0, 0.0)        # g; the direction pointing at the sky reads +1 (here: standing)
        self.spin = (0.0, 0.0, 0.0)         # degrees per second
        self.mag = (20.0, -43.0, 0.0)       # microtesla
        self.temperature = 20.0             # degrees C
        self.humidity = 50.0                # percent
        self.pressure = SEA_LEVEL           # hPa
        self.lux = 200.0
        self.battery = 1.0                  # 0 to 1
        self.plugged_in = False
        self.tapped = None                  # True / False from a hardware tap detector; None = work it out here


def height_between(p0, p):
    """Metres climbed going from pressure p0 to pressure p (hPa): the international barometric formula."""
    return 44330.0 * ((p0 / SEA_LEVEL) ** 0.1903 - (p / SEA_LEVEL) ** 0.1903)


class Dino:
    def __init__(self, n_leds=18):
        self.leds = Leds(n_leds)
        self.snout, self.tail = Pad(), Pad()
        self.front_flipper, self.rear_flipper = Pad(), Pad()
        self.slider = Slider(n_leds)
        self.accel, self.spin = Vec(0.0, 1.0, 0.0), Vec()
        self.saved = {}
        self._last_accel = None
        self._reset()

    # ---- used by the host --------------------------------------------------------------------------
    def _reset(self):
        """Fresh start for a behaviour. Touch and movement carry on; time, memory and lights start again."""
        self.time, self.dt = 0.0, 1.0 / 30
        self.my = My()
        self.leds.clear()
        self._eye = (0.0, 0.0, 0.0)
        self._brightness = DEFAULT_BRIGHTNESS
        self._sound = None                  # ("tone", hz, seconds) or ("quiet",) waiting for the host
        self.up = "spine"
        self.shake, self.shaken, self.tapped = 0.0, False, False
        self._shaking = False
        self.still = 0.0
        self.falling, self.airtime = False, 0.0
        self._low_g, self._since_tap = 0.0, 1.0
        self.temperature, self.humidity, self.pressure = 20.0, 50.0, SEA_LEVEL
        self.lux, self.light = 200.0, 0.5
        self.heading, self.magnet = 0.0, 45.0
        self.battery, self.plugged_in = 1.0, False
        self._zero_pressure = None
        self.height = 0.0

    def _frame(self, r, dt):
        """Take one Reading and move time on by dt seconds."""
        self.dt = dt
        self.time += dt
        for name in PAD_NAMES:
            getattr(self, name)._update(r.pads.get(name, False), dt)
        self.slider._update(r.slider_touched, r.slider_pos, dt)
        self._movement(r, dt)
        self.temperature, self.humidity, self.pressure = r.temperature, r.humidity, r.pressure
        if self._zero_pressure is None:
            self._zero_pressure = r.pressure
        self.height = height_between(self._zero_pressure, r.pressure)
        self.lux = r.lux if r.lux > 0 else 0.0
        self.light = min(math.log(1.0 + self.lux) / math.log(30001.0), 1.0)   # 0 dark, 1 at 30,000 lux
        mx, my, mz = r.mag
        self.magnet = math.sqrt(mx * mx + my * my + mz * mz)
        self.heading = math.degrees(math.atan2(-my, mx)) % 360.0              # lying flat, picture side up
        self.battery, self.plugged_in = r.battery, r.plugged_in

    def _movement(self, r, dt):
        ax, ay, az = r.accel
        self.accel._set(r.accel)
        self.spin._set(r.spin)
        big = max(abs(ax), abs(ay), abs(az))
        if big > 0.5:                                    # otherwise keep the last answer
            if big == abs(ax):
                self.up = "nose" if ax > 0 else "tail"
            elif big == abs(ay):
                self.up = "spine" if ay > 0 else "belly"
            else:
                self.up = "face" if az > 0 else "underside"
        # free fall: next to no acceleration at all, for long enough to be sure
        if math.sqrt(ax * ax + ay * ay + az * az) < FALL_BELOW_G:
            self._low_g += dt
            if self._low_g >= FALL_AFTER:
                self.falling = True
        else:
            if self.falling:
                self.airtime = self._low_g
            self.falling, self._low_g = False, 0.0
        # shaking and tapping: how much the acceleration changed since the last frame
        last = self._last_accel or r.accel
        self._last_accel = r.accel
        jerk = math.sqrt((ax - last[0]) ** 2 + (ay - last[1]) ** 2 + (az - last[2]) ** 2)
        was_calm = self.shake < 0.3
        self.shake += (min(jerk / SHAKE_FULL, 1.0) - self.shake) * (1.0 - math.exp(-dt / 0.15))
        self.shaken = False
        if not self._shaking and self.shake > SHAKE_ON:
            self._shaking = self.shaken = True
        elif self._shaking and self.shake < SHAKE_OFF:
            self._shaking = False
        self._since_tap += dt
        if r.tapped is None:
            self.tapped = jerk > TAP_JERK and was_calm and self._since_tap > 0.25
        else:
            self.tapped = bool(r.tapped)
        if self.tapped:
            self._since_tap = 0.0
        turning = math.sqrt(r.spin[0] ** 2 + r.spin[1] ** 2 + r.spin[2] ** 2)
        self.still = 0.0 if (jerk > MOVING_JERK or turning > MOVING_SPIN) else self.still + dt

    def _take_sound(self):
        s, self._sound = self._sound, None
        return s

    # ---- for behaviours ----------------------------------------------------------------------------
    @property
    def eye(self):
        r, g, b = self._eye
        return (int(r), int(g), int(b))

    @eye.setter
    def eye(self, c):
        self._eye = colour.parse(c)

    @property
    def brightness(self):
        return self._brightness

    @brightness.setter
    def brightness(self, v):
        self._brightness = 0.0 if v < 0 else 1.0 if v > 1 else float(v)

    def every(self, seconds):
        """True on one update every so many seconds."""
        if seconds <= 0:
            return True
        return int(self.time / seconds) != int((self.time - self.dt) / seconds)

    def wave(self, seconds):
        """A number that swings smoothly 0 -> 1 -> 0 once in that many seconds."""
        if seconds <= 0:
            return 0.0
        return (1.0 - math.cos(2.0 * math.pi * self.time / seconds)) / 2.0

    def hsv(self, hue, sat=1.0, val=1.0):
        return colour.hsv(hue, sat, val)

    def mix(self, a, b, amount):
        return colour.mix(a, b, amount)

    def beep(self, seconds=0.1):
        """A beep at the buzzer's loudest pitch."""
        self._sound = ("tone", BEEP_HZ, seconds)

    def tone(self, hz, seconds=0.2):
        """A beep at another pitch. Returns at once; the host stops it when its time is up."""
        self._sound = ("tone", min(max(float(hz), 50.0), 12000.0), seconds)

    def quiet(self):
        self._sound = ("quiet",)

    def zero_height(self):
        """Make dino.height zero here."""
        self._zero_pressure = self.pressure
        self.height = 0.0
