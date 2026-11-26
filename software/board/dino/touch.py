"""Touch pads and the slider, as behaviours see them."""


class Pad:
    def __init__(self):
        self.touched = False     # True while a finger is on it
        self.pressed = False     # True for one update, when the finger arrives
        self.released = False    # True for one update, when it leaves
        self.held = 0.0          # seconds the finger has been there

    def _update(self, touched, dt):
        touched = bool(touched)
        self.pressed = touched and not self.touched
        self.released = self.touched and not touched
        self.held = self.held + dt if (touched and self.touched) else 0.0
        self.touched = touched


class Slider(Pad):
    def __init__(self, n_leds=18):
        Pad.__init__(self)
        self._n = n_leds
        self.pos = 0.5           # 0.0 at the head to 1.0 at the tail; keeps its last value
        self.led = int(round(0.5 * (n_leds - 1)))
        self.speed = 0.0         # lengths per second, positive towards the tail

    def _update(self, touched, pos, dt):
        was = self.touched
        Pad._update(self, touched, dt)
        if self.touched:
            pos = 0.0 if pos < 0 else 1.0 if pos > 1 else pos
            if was and dt > 0:
                self.speed += ((pos - self.pos) / dt - self.speed) * 0.5     # a little smoothing
            else:
                self.speed = 0.0
            self.pos = pos
            self.led = int(round(pos * (self._n - 1)))
        else:
            self.speed = 0.0
