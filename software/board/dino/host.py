"""The host: the program that is always running. It owns the main loop, loads behaviours, runs the
menu (hold the snout and slide along the back), catches a behaviour's errors, limits the LED current
and saves what behaviours ask to keep.

It talks to the hardware through a small object, `hw`, so that the same code runs on the board
(hw_board.Board), in the tests and in the browser simulator (sim/hw_fake.FakeHardware):

    hw.now()               seconds, from a clock that only goes forwards
    hw.read(reading)       fill in a core.Reading
    hw.show(pixels, eye)   pixels: list of (r, g, b) whole numbers 0 to 255; eye: one such
    hw.tone(hz)            start a note;  hw.quiet()  stop it
    hw.sleep(seconds)      wait

Behaviours are files called NN_name.py in the behaviours folder: NN is 01 to 18, the number printed
beside the LED that stands for it."""
import json
import os

from .core import Dino, Reading
from . import colour

try:
    import traceback
except ImportError:                 # small CircuitPython builds have none
    traceback = None

SLOTS = 18
FPS = 30
# LED current. NOTES.md, "For firmware": cap the total at about 0.3 A; 19 LEDs at full white would be
# about 0.7 A, which is 12.3 mA for each of a LED's three colours.
MAX_AMPS = 0.3
AMPS_PER_COLOUR = 0.7 / 19 / 3
SAVE_EVERY = 5.0                    # seconds between checks of dino.saved (flash wears out: do not hurry)
MENU_DIM = 0.12


class Slot:
    def __init__(self, number):
        self.number = number        # 1 to 18, as printed on the board
        self.file = None            # file name in the behaviours folder
        self.source = None
        self.name = None
        self.colour = "white"
        self.space = None           # the behaviour's own names: init, update, NAME ...
        self.error = None           # text of what went wrong, if anything did
        self.line = None            # line of the file the error points at


def _error_text(e, filename):
    """(text, line number in the behaviour's file or None) for an exception."""
    text = "%s: %s" % (type(e).__name__, e)
    line = getattr(e, "lineno", None) if isinstance(e, SyntaxError) else None
    if traceback is not None:
        try:
            full = traceback.format_exception(type(e), e, e.__traceback__)
            full = full if isinstance(full, str) else "".join(full)
            marker = 'File "%s", line ' % filename
            at = full.rfind(marker)
            if at >= 0 and line is None:
                digits = ""
                for ch in full[at + len(marker):]:
                    if not ch.isdigit():
                        break
                    digits += ch
                line = int(digits) if digits else None
        except Exception:           # never let the error reporter be the thing that fails
            pass
    if line is not None:
        text = "line %d: %s" % (line, text)
    return text, line


class Host:
    def __init__(self, hw, behaviours_dir="behaviours", saved_dir="saved"):
        self.hw = hw
        self.behaviours_dir, self.saved_dir = behaviours_dir, saved_dir
        self.dino = Dino(SLOTS)
        self.reading = Reading()
        self.slots = [Slot(i + 1) for i in range(SLOTS)]
        self.current = None         # the Slot that is running, or None
        self.running = False        # False while its error is being shown
        self.menu = False
        self.cursor = 0
        self.storage_ok = True
        self._last = None
        self._tone_until = None
        self._saved_text = "{}"
        self._save_check = 0.0
        self._clock = 0.0
        self._before_menu = 0.3

    # ---- behaviours ----------------------------------------------------------------------------------
    def scan(self):
        """Read every NN_name.py in the behaviours folder."""
        try:
            names = sorted(os.listdir(self.behaviours_dir))
        except OSError:
            names = []
        for name in names:
            if not name.endswith(".py") or len(name) < 4 or not name[:2].isdigit():
                continue
            number = int(name[:2])
            if not 1 <= number <= SLOTS:
                continue
            try:
                with open(self.behaviours_dir + "/" + name) as f:
                    source = f.read()
            except OSError:
                continue
            self.load_source(number, source, name)

    def load_source(self, number, source, filename=None):
        """Put this Python text in slot `number` (1 to 18). True if it loaded without error."""
        slot = self.slots[number - 1]
        slot.file = filename or slot.file or "%02d_behaviour.py" % number
        slot.source, slot.error, slot.line, slot.space = source, None, None, None
        slot.name, slot.colour = slot.file[3:-3].replace("_", " "), "white"
        space = {"__name__": "behaviour_%02d" % number}
        try:
            exec(compile(source, slot.file, "exec"), space)
            if not callable(space.get("update")):
                raise ValueError("a behaviour needs a function called update(dino)")
            if "COLOUR" in space:
                colour.parse(space["COLOUR"])
                slot.colour = space["COLOUR"]
            if "NAME" in space:
                slot.name = str(space["NAME"])
            slot.space = space
        except Exception as e:
            slot.error, slot.line = _error_text(e, slot.file)
        if self.current is slot:                     # it was running: start the new version
            self.select(number)
        return slot.error is None

    def clear_slot(self, number):
        slot = self.slots[number - 1]
        if self.current is slot:
            self._save()
            self.current, self.running = None, False
        self.slots[number - 1] = Slot(number)

    def select(self, number):
        """Start the behaviour in slot `number` (1 to 18)."""
        self._save()
        slot = self.slots[number - 1]
        self.current, self.menu = slot, False
        self.dino._reset()
        self.dino.saved = self._load_saved(slot)
        self._saved_text = json.dumps(self.dino.saved)
        self.running = slot.space is not None
        self._remember(number)
        if self.running and callable(slot.space.get("init")):
            self._call(slot, "init")
            self._save()                             # what init changed is kept even if the power goes now

    def _call(self, slot, what):
        try:
            slot.space[what](self.dino)
        except Exception as e:
            slot.error, slot.line = _error_text(e, slot.file)
            self.running = False
            self.dino._take_sound()
            self.hw.quiet()
            self._tone_until = None

    # ---- things kept on the board ----------------------------------------------------------------------
    def _path(self, slot):
        return "%s/%s.json" % (self.saved_dir, (slot.file or "slot%02d" % slot.number)[:-3])

    def _load_saved(self, slot):
        try:
            with open(self._path(slot)) as f:
                data = json.load(f)
            return data if isinstance(data, dict) else {}
        except (OSError, ValueError):
            return {}

    def _write(self, path, text):
        if not self.storage_ok:
            return
        try:
            try:
                os.mkdir(self.saved_dir)
            except OSError:
                pass                                 # it is there already
            with open(path, "w") as f:
                f.write(text)
        except OSError:
            self.storage_ok = False                  # a read-only drive (a computer has it): stop trying

    def _save(self):
        if self.current is None:
            return
        try:
            text = json.dumps(self.dino.saved)
        except (TypeError, ValueError):
            return                                   # something in there cannot be saved: leave the old file
        if text != self._saved_text:
            self._saved_text = text
            self._write(self._path(self.current), text)

    def _remember(self, number):
        self._write(self.saved_dir + "/_host.json", json.dumps({"slot": number}))

    def remembered(self):
        """The slot that was running last time, or None."""
        try:
            with open(self.saved_dir + "/_host.json") as f:
                number = json.load(f).get("slot")
            return number if isinstance(number, int) and 1 <= number <= SLOTS else None
        except (OSError, ValueError, AttributeError):
            return None

    # ---- one frame -------------------------------------------------------------------------------------
    def step(self):
        now = self.hw.now()
        dt = 1.0 / FPS if self._last is None else now - self._last
        dt = 0.001 if dt < 0.001 else 0.1 if dt > 0.1 else dt
        self._last = now
        self._clock += dt
        self.hw.read(self.reading)
        d = self.dino
        d._frame(self.reading, dt)

        if self._tone_until is not None and self._clock >= self._tone_until:
            self.hw.quiet()
            self._tone_until = None

        if not self.menu and d.snout.touched and d.slider.touched:
            self.menu = True
            self.cursor = d.slider.led
            self._before_menu = d.brightness
            self._beep(0.01)
        if self.menu:
            self._menu_frame()
        elif self.current is not None and self.running:
            self._call(self.current, "update")
            self._sound(d._take_sound())
            if self._clock - self._save_check > SAVE_EVERY:
                self._save_check = self._clock
                self._save()
        if not self.menu and not self.running:
            self._idle_frame()
        self._show()

    def _menu_frame(self):
        d = self.dino
        if d.slider.touched:
            if d.slider.led != self.cursor:
                self.cursor = d.slider.led
                self._beep(0.005)
            for i, slot in enumerate(self.slots):
                d.leds[i] = colour.mix("off", slot.colour, MENU_DIM) if slot.space is not None else "off"
            here = self.slots[self.cursor]
            d.leds[self.cursor] = here.colour if here.space is not None else colour.mix("off", "white", MENU_DIM)
            d.eye = here.colour if here.space is not None else "off"
            d.brightness = 0.5
        else:                                        # the finger left the back: that is the choice
            chosen = self.slots[self.cursor]
            if chosen.space is not None or chosen.error is not None:
                self.select(chosen.number)
                self._beep(0.03)
            else:                                    # an empty slot: carry on with what was running
                self.menu = False
                d.leds.clear()
                d.eye = "off"
                d.brightness = self._before_menu

    def _idle_frame(self):
        """Nothing is running: show why. A slot with an error blinks red; otherwise the eye breathes."""
        d = self.dino
        d.leds.clear()
        d.brightness = 0.3
        if self.current is not None and self.current.error is not None:
            on = int(self._clock * 2) % 2 == 0
            d.leds[self.current.number - 1] = "red" if on else "off"
            d.eye = "red" if on else "off"
        else:
            d.eye = colour.mix("off", "white", 0.1 + 0.3 * d.wave(4))

    def _beep(self, seconds):
        self._sound(("tone", 4000, seconds))

    def _sound(self, s):
        if s is None:
            return
        if s[0] == "quiet" or s[2] <= 0:
            self.hw.quiet()
            self._tone_until = None
        else:
            self.hw.tone(s[1])
            self._tone_until = self._clock + s[2]

    def _show(self):
        d = self.dino
        k = d.brightness
        total = sum(r + g + b for r, g, b in d.leds._p) + sum(d._eye)
        amps = total * k / 255.0 * AMPS_PER_COLOUR
        if amps > MAX_AMPS:
            k *= MAX_AMPS / amps
        self.hw.show([(int(r * k), int(g * k), int(b * k)) for r, g, b in d.leds._p],
                     tuple(int(v * k) for v in d._eye))

    # ---- running for ever ------------------------------------------------------------------------------
    def start(self):
        """Load the behaviours and start the one that ran last, or the first there is."""
        self.scan()
        number = self.remembered()
        if number is None or self.slots[number - 1].space is None:
            loaded = [s.number for s in self.slots if s.space is not None]
            number = loaded[0] if loaded else None
        if number is not None:
            self.select(number)

    def run(self):
        self.start()
        while True:
            began = self.hw.now()
            self.step()
            spare = 1.0 / FPS - (self.hw.now() - began)
            if spare > 0:
                self.hw.sleep(spare)

    def status(self):
        """A plain summary for a web page."""
        return {
            "current": self.current.number if self.current is not None else None,
            "running": self.running,
            "menu": self.menu,
            "storage_ok": self.storage_ok,
            "slots": [{"number": s.number, "file": s.file, "name": s.name, "colour": s.colour,
                       "loaded": s.space is not None, "error": s.error, "line": s.line} for s in self.slots],
        }
