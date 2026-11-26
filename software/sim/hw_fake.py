"""A pretend board, for the tests and the browser simulator. Set the inputs as plain attributes
(or all at once with set_inputs); read back what the host showed in .pixels, .eye and .hz."""
import json
import time

from dino.core import Reading, PAD_NAMES


class FakeHardware:
    def __init__(self, real_time=False):
        self.real_time = real_time      # False: the clock moves only when tick() or sleep() is called
        self.clock = 0.0
        self.inputs = Reading()         # change these to change what the board "feels"
        self.pixels = [(0, 0, 0)] * 18
        self.eye = (0, 0, 0)
        self.hz = 0                     # the note sounding now; 0 = silence
        self.notes = []                 # every note started: (clock, hz)
        self.frames = 0

    # ---- what the host calls ----
    def now(self):
        return time.monotonic() if self.real_time else self.clock

    def sleep(self, seconds):
        if self.real_time:
            time.sleep(seconds)
        else:
            self.clock += seconds

    def read(self, reading):
        i = self.inputs
        for name in PAD_NAMES:
            reading.pads[name] = i.pads[name]
        reading.slider_touched, reading.slider_pos = i.slider_touched, i.slider_pos
        reading.accel, reading.spin, reading.mag = i.accel, i.spin, i.mag
        reading.temperature, reading.humidity, reading.pressure, reading.lux = i.temperature, i.humidity, i.pressure, i.lux
        reading.battery, reading.plugged_in, reading.tapped = i.battery, i.plugged_in, i.tapped

    def show(self, pixels, eye):
        self.pixels, self.eye = pixels, eye
        self.frames += 1

    def tone(self, hz):
        self.hz = hz
        self.notes.append((self.now(), hz))

    def quiet(self):
        self.hz = 0

    # ---- for whoever is driving ----
    def tick(self, seconds=1.0 / 30):
        self.clock += seconds

    def set_inputs(self, text):
        """Inputs as JSON, the way the simulator page sends them:
        {"pads": {"snout": true}, "slider_touched": false, "slider_pos": 0.4, "accel": [0, 1, 0], ...}"""
        data = json.loads(text)
        i = self.inputs
        for name, value in data.get("pads", {}).items():
            if name in i.pads:
                i.pads[name] = bool(value)
        for key in ("accel", "spin", "mag"):
            if key in data:
                setattr(i, key, tuple(float(v) for v in data[key]))
        for key in ("slider_pos", "temperature", "humidity", "pressure", "lux", "battery"):
            if key in data:
                setattr(i, key, float(data[key]))
        for key in ("slider_touched", "plugged_in"):
            if key in data:
                setattr(i, key, bool(data[key]))
        if "tapped" in data:
            i.tapped = data["tapped"]

    def output(self):
        """What the board is showing, as JSON for the page."""
        return json.dumps({"pixels": self.pixels, "eye": self.eye, "hz": self.hz})
