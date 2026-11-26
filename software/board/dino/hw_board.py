"""The real board, for CircuitPython on the ESP32-S3-MINI-1-N4R2.

NOT YET RUN ON HARDWARE (written 2026-11-26, before the boards arrived). Pins, addresses and the
firmware rules come from NOTES.md ("For firmware"); library names and signatures were read from the
libraries' source on 2026-11-26. Each thing that can only be settled on the bench is marked CHECK.

Libraries needed in /lib: adafruit_bus_device, adafruit_register, adafruit_mpr121, adafruit_lsm6ds,
adafruit_sht4x, adafruit_ltr329_ltr303, adafruit_bmp5xx, adafruit_qmc5883p.

A sensor that is missing or fails to start is skipped with a message on the serial console: the board
still runs, and that reading keeps its stand-in value."""
import time

import analogio
import busio
import digitalio
import microcontroller
import neopixel_write
import pwmio

from .core import PAD_NAMES

P = microcontroller.pin
PIN_TOUCH_IRQ, PIN_BUZZER, PIN_VBAT, PIN_SPINE = P.GPIO1, P.GPIO4, P.GPIO10, P.GPIO11
PIN_INT1, PIN_INT2, PIN_CHG, PIN_VBUS, PIN_LED_EN = P.GPIO15, P.GPIO16, P.GPIO17, P.GPIO18, P.GPIO21
PIN_SDA, PIN_SCL, PIN_EYE = P.GPIO41, P.GPIO42, P.GPIO48

ADDR_TOUCH = 0x5C               # MPR121, ADDR tied to SDA
ADDR_PRESSURE = 0x46            # BMP580, SDO to ground
# MPR121 electrodes: 0 to 7 are the back, head to tail; then the four pads
ELECTRODE = {"snout": 8, "tail": 9, "rear_flipper": 10, "front_flipper": 11}
SPINE = 8
TOUCH_NOISE = 4                 # counts below the baseline that are ignored when finding the finger. CHECK

LED_ORDER = (1, 0, 2)           # SK6812: green, red, blue. CHECK: if red and green are swapped, use (0, 1, 2)

# Directions. The dinosaur's x points out of the nose, y out of the back, z out of the picture side.
# Both chips sit on the parts side at rotation 0 with pin 1 top-left (board file, 2026-11-26).
# LSM6DS3TR-C: its +X is towards the nose, +Y towards the back, +Z out of the parts side.
ACCEL_SIGN = (1, 1, -1)         # CHECK: nose up must give accel.x near +1; picture side up, accel.z near +1
SPIN_SIGN = (1, 1, 1)           # CHECK: spin.z positive when turned clockwise, looking at the picture
# QMC5883P: its +X is towards the tail, +Y towards the belly, +Z out of the parts side (datasheet; a
# register can flip signs).
MAG_SIGN = (-1, -1, -1)         # CHECK against a real compass: lying picture side up, heading 0 = nose north
MAG_TO_UT = 100.0               # the library's .magnetic is in gauss, whatever its docstring says. CHECK

VBAT_EMPTY, VBAT_FULL = 3.5, 4.15       # volts: the notes say sleep at about 3.5
G = 9.80665


def _unstick_i2c():
    """Nine clocks on SCL: after a brown-out the module restarts but a sensor may be mid-byte (NOTES.md)."""
    scl = digitalio.DigitalInOut(PIN_SCL)
    scl.switch_to_output(value=True, drive_mode=digitalio.DriveMode.OPEN_DRAIN)
    for _ in range(9):
        scl.value = False
        time.sleep(0.00001)
        scl.value = True
        time.sleep(0.00001)
    scl.deinit()


def _input(pin):
    io = digitalio.DigitalInOut(pin)
    io.switch_to_input(pull=None)       # claimed with no pull: an unclaimed pin gets a 45k pull-up
    return io


class Board:
    def __init__(self):
        # outputs first, in their safe states
        self.led_en = digitalio.DigitalInOut(PIN_LED_EN)
        self.led_en.switch_to_output(value=False)
        self.spine = digitalio.DigitalInOut(PIN_SPINE)
        self.spine.switch_to_output(value=False)
        self.eye_pin = digitalio.DigitalInOut(PIN_EYE)
        self.eye_pin.switch_to_output(value=False)
        self.buzzer = pwmio.PWMOut(PIN_BUZZER, frequency=4000, duty_cycle=0, variable_frequency=True)
        # inputs: every pin claimed (NOTES.md: the motion sensor's interrupt pins waste 73 uA each otherwise)
        self.touch_irq, self.int1, self.int2 = _input(PIN_TOUCH_IRQ), _input(PIN_INT1), _input(PIN_INT2)
        self.chg, self.vbus = _input(PIN_CHG), _input(PIN_VBUS)
        self.vbat = analogio.AnalogIn(PIN_VBAT)

        _unstick_i2c()
        self.i2c = busio.I2C(PIN_SCL, PIN_SDA, frequency=100000)
        self.touch = self.touch_raw = self.motion = self.compass = None
        self.climate = self.light = self.baro = None
        self._start("touch", self._start_touch)
        self._start("motion", self._start_motion)
        self._start("compass", self._start_compass)
        self._start("temperature", self._start_climate)
        self._start("light", self._start_light)
        self._start("pressure", self._start_baro)

        self._leds_on = False
        self._buf = bytearray(18 * 3)
        self._eye_buf = bytearray(3)
        self._turn = 0
        self._filtered, self._baseline = bytearray(SPINE * 2), bytearray(SPINE)
        self._slider_pos = 0.5
        self._pressure = None

    def _start(self, name, fn):
        try:
            fn()
        except Exception as e:          # a sensor that is not there must not stop the dinosaur
            print("no %s sensor: %s: %s" % (name, type(e).__name__, e))

    def _start_touch(self):
        import adafruit_mpr121
        from adafruit_bus_device.i2c_device import I2CDevice
        self.touch = adafruit_mpr121.MPR121(self.i2c, address=ADDR_TOUCH)     # the constructor soft-resets it
        self.touch_raw = I2CDevice(self.i2c, ADDR_TOUCH)                      # for reading eight electrodes at once

    def _start_motion(self):
        from adafruit_lsm6ds import AccelRange, GyroRange, Rate
        from adafruit_lsm6ds.lsm6ds3trc import LSM6DS3TRC
        self.motion = LSM6DS3TRC(self.i2c)                                    # 0x6A, the library's default
        self.motion.accelerometer_range = AccelRange.RANGE_8G
        self.motion.gyro_range = GyroRange.RANGE_1000_DPS
        self.motion.accelerometer_data_rate = self.motion.gyro_data_rate = Rate.RATE_104_HZ

    def _start_compass(self):
        import adafruit_qmc5883p
        self.compass = adafruit_qmc5883p.QMC5883P(self.i2c)                   # 0x2C

    def _start_climate(self):
        import adafruit_sht4x
        self.climate = adafruit_sht4x.SHT4x(self.i2c)                         # 0x44
        self.climate.mode = adafruit_sht4x.Mode.NOHEAT_LOWPRECISION           # quickest; never the heater (NOTES.md)

    def _start_light(self):
        from adafruit_ltr329_ltr303 import LTR303
        time.sleep(0.1)                                                       # 100 ms after power-up (NOTES.md)
        self.light = LTR303(self.i2c)                                         # 0x29
        self.light.als_gain = 1
        self.light.integration_time = 100
        self.light.measurement_rate = 200

    def _start_baro(self):
        import adafruit_bmp5xx
        self.baro = adafruit_bmp5xx.BMP5XX.over_i2c(self.i2c, address=ADDR_PRESSURE)

    # ---- what the host calls ---------------------------------------------------------------------------
    def now(self):
        return time.monotonic()

    def sleep(self, seconds):
        time.sleep(seconds)

    def read(self, r):
        self._read_touch(r)
        if self.motion is not None:
            try:
                a, g = self.motion.acceleration, self.motion.gyro             # m/s2 and radians per second
                r.accel = tuple(a[i] / G * ACCEL_SIGN[i] for i in range(3))
                r.spin = tuple(g[i] * 57.29578 * SPIN_SIGN[i] for i in range(3))
            except OSError:
                pass
        # the slow sensors take turns, one a frame, so no frame waits for all of them
        self._turn = (self._turn + 1) % 30
        try:
            if self._turn % 3 == 0 and self.compass is not None:              # ten times a second
                m = self.compass.magnetic
                r.mag = tuple(m[i] * MAG_TO_UT * MAG_SIGN[i] for i in range(3))
            elif self._turn % 6 == 1 and self.baro is not None:               # five times a second
                p = self.baro.pressure                                        # hPa
                self._pressure = p if self._pressure is None else self._pressure + (p - self._pressure) * 0.3
                r.pressure = self._pressure
            elif self._turn == 2 and self.climate is not None:                # once a second
                r.temperature, r.humidity = self.climate.measurements
            elif self._turn % 6 == 5 and self.light is not None:
                r.lux = self._lux()
            elif self._turn == 4:
                volts = self.vbat.value / 65535 * self.vbat.reference_voltage * 2      # the pin sees half the battery
                r.battery = min(max((volts - VBAT_EMPTY) / (VBAT_FULL - VBAT_EMPTY), 0.0), 1.0)
                r.plugged_in = self.vbus.value
        except (OSError, ValueError, RuntimeError):
            pass                                                              # a bad reading: keep the last one

    def _read_touch(self, r):
        if self.touch is None:
            return
        try:
            mask = self.touch.touched()
        except OSError:
            return
        for name in PAD_NAMES:
            r.pads[name] = bool(mask & (1 << ELECTRODE[name]))
        r.slider_touched = bool(mask & 0xFF)
        if r.slider_touched:
            try:
                with self.touch_raw as dev:
                    dev.write_then_readinto(b"\x04", self._filtered)          # filtered data, electrodes 0 to 7
                    dev.write_then_readinto(b"\x1e", self._baseline)          # baselines, top 8 of 10 bits
            except OSError:
                return
            total = moment = 0
            for i in range(SPINE):
                filtered = self._filtered[2 * i] | (self._filtered[2 * i + 1] << 8)
                delta = (self._baseline[i] << 2) - filtered - TOUCH_NOISE     # a finger lowers the reading
                if delta > 0:
                    total += delta
                    moment += delta * i
            if total > 0:
                self._slider_pos = moment / total / (SPINE - 1)               # CHECK: ends reachable? evenly spread?
        r.slider_pos = self._slider_pos

    def _lux(self):
        """Lux from the LTR-303's two channels, by the formula in its maker's application note (FROM MEMORY:
        CHECK against the note, and against a lux meter through the case window)."""
        both, ir = self.light.light_channels
        if both + ir == 0:
            return 0.0
        ratio = ir / (both + ir)
        scale = self.light.als_gain * self.light.integration_time / 100.0
        if ratio < 0.45:
            return (1.7743 * both + 1.1059 * ir) / scale
        if ratio < 0.64:
            return (4.2785 * both - 1.9548 * ir) / scale
        if ratio < 0.85:
            return (0.5926 * both + 0.1185 * ir) / scale
        return 0.0

    def show(self, pixels, eye):
        dark = not any(eye) and not any(any(p) for p in pixels)
        if dark and not self._leds_on:
            return
        if not self._leds_on:
            self.led_en.value = True
            time.sleep(0.005)                           # the rail takes about 2 ms to rise (NOTES.md)
            self._leds_on = True
        a, b, c = LED_ORDER
        buf = self._buf
        for i, p in enumerate(pixels):
            buf[3 * i], buf[3 * i + 1], buf[3 * i + 2] = p[a], p[b], p[c]
        self._eye_buf[0], self._eye_buf[1], self._eye_buf[2] = eye[a], eye[b], eye[c]
        neopixel_write.neopixel_write(self.spine, buf)
        neopixel_write.neopixel_write(self.eye_pin, self._eye_buf)
        if dark:                                        # all off: blanked above, now drop the rail
            self.spine.value = False                    # data low first, or the dead rail is fed through the pin
            self.eye_pin.value = False
            self.led_en.value = False
            self._leds_on = False

    def tone(self, hz):
        self.buzzer.frequency = int(hz)
        self.buzzer.duty_cycle = 32768

    def quiet(self):
        self.buzzer.duty_cycle = 0                      # the pin rests low: never leave it high (NOTES.md)

    # ---- power -----------------------------------------------------------------------------------------
    def battery_volts(self):
        return self.vbat.value / 65535 * self.vbat.reference_voltage * 2

    def sleep_until_plugged_in(self):
        """Lights out and deep sleep until USB power arrives. For a flat battery. CHECK on the bench."""
        import alarm
        self.quiet()
        self.show([(0, 0, 0)] * 18, (0, 0, 0))
        self.vbus.deinit()
        wake = alarm.pin.PinAlarm(pin=PIN_VBUS, value=True, pull=False)
        alarm.exit_and_deep_sleep_until_alarms(wake)
