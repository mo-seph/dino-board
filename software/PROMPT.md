# Writing a behaviour for the Mosasauraboard

Please write one "behaviour" for the Mosasauraboard: a single Python file. The idea for it is at the end
of this page. Everything you need to know about the board is here; please use only what this page
describes.

## The board

The Mosasauraboard is a circuit board shaped like a mosasaurus, about 23 cm long, head on the left. It
has 18 coloured LEDs in a row along its back, one more LED for its eye, a small buzzer, touch pads, and
sensors for movement, compass direction, temperature, humidity, air pressure and light. It has no
screen, microphone or speaker, and it does not know the time of day.

People who use it are often not programmers, and many are children. A good behaviour does one thing,
and what it does is obvious within a few seconds of picking the board up.

## How a behaviour is written

A host program runs on the board. It owns the main loop and all the hardware. It calls two functions
in your file and passes them one object, `dino`:

```python
"""One line saying what the behaviour does and how to use it."""
NAME = "Short name"
COLOUR = "orange"        # the colour of this behaviour's LED in the menu

def init(dino):          # called once, when the behaviour is chosen
    ...

def update(dino):        # called about 30 times a second
    ...
```

The rules, and why they exist:

- **`update` must return straight away.** No `time.sleep`, and no loop that waits for something. The
  host cannot read the sensors, refresh the LEDs or switch behaviour until `update` returns. To make
  things happen over time, keep a variable and compare it with `dino.time`, as the examples do.
- **Use `dino.dt` for anything that moves or counts.** The 30 calls a second are not exact.
- **Keep your variables on `dino.my`** (`dino.my.score = 0`), set up in `init`. Module-level variables
  survive from one run to the next and cause surprises.
- **Use only `dino`.** Do not import `board`, `time`, `neopixel`, `machine` or any hardware library:
  the host already owns the hardware. `math` and `random` are fine.
- **`.pressed` is true for one call only**, when a finger arrives. Use it for "do this once". Use
  `.touched` for "while a finger is there".
- **The LEDs keep their colours between calls.** Clear or redraw them if you want them to change.
- **Do not start a beep on every call:** each new sound cuts off the last one. Start a sound when
  something happens.
- **Holding the snout while sliding along the back is taken:** it opens the menu. The snout alone and
  the slider alone are yours.
- Keep it short: most behaviours need 20 to 60 lines.

## What `dino` gives you

Time and memory:

```
dino.time              seconds since the behaviour started
dino.dt                seconds since the last update (about 0.03)
dino.every(seconds)    True on one update every so many seconds
dino.wave(seconds)     a number that swings smoothly 0 -> 1 -> 0 once in that time
dino.my                an empty object for your own variables; emptied each time the behaviour starts
dino.saved             a small dict that survives switching off (numbers and short strings):
                       dino.saved.get("best", 0), dino.saved["best"] = 3
```

Lights:

```
dino.leds[i] = colour                 one LED; i is 0 at the head to 17 at the tail
dino.leds.fill(colour)                all 18
dino.leds.clear()                     all off
dino.leds.dot(pos, colour, width=1)   a soft spot at pos, 0.0 (head) to 1.0 (tail), added to what is there
dino.leds.bar(amount, colour, back="off")   a bar from the head covering amount (0.0 to 1.0) of the row
dino.leds.fade(keep=0.8)              dim everything to that fraction; call each update for trails
dino.leds.gradient(a, b)              blend from colour a at the head to b at the tail
dino.eye = colour                     the eye
dino.brightness = 0.3                 overall brightness, 0.0 to 1.0
```

The board has the numbers 1 to 18 printed beside the LEDs. `dino.leds[0]` is the one printed "1".

A colour is a name ("red", "orange", "yellow", "green", "cyan", "blue", "purple", "pink", "white",
"off"), a hex string ("#ff8800") or three numbers (255, 136, 0).

```
dino.hsv(hue, sat=1, val=1)    a rainbow colour; hue 0.0 to 1.0 goes red, yellow, green, blue, purple, red
dino.mix(a, b, amount)         blend two colours: amount 0.0 gives a, 1.0 gives b
```

Touch:

```
dino.snout   dino.tail   dino.front_flipper   dino.rear_flipper     four touch pads
dino.slider                                                         a touch strip along the back, under the LEDs

each of them has:
  .touched     True while a finger is on it
  .pressed     True for one update, when the finger arrives
  .released    True for one update, when it leaves
  .held        seconds the finger has been there (0 when not touched)

the slider also has:
  .pos         where the finger is, 0.0 (head) to 1.0 (tail); keeps its last value when the finger lifts
  .led         the index of the LED above the finger, 0 to 17
  .speed       finger speed in lengths per second, positive towards the tail
```

Slider positions and LED positions use the same scale, so `dino.leds.dot(dino.slider.pos, "white")`
puts a light under the finger.

Movement:

```
dino.accel.x  .y  .z   acceleration in g. x points out of the nose, y out of the back (the LED edge),
                       z out of the picture side. Held still, the direction pointing at the sky reads +1,
                       so nose pointing down gives accel.x = -1
dino.up                the part pointing at the sky: "spine", "belly", "nose", "tail",
                       "face" (lying picture side up) or "underside"
dino.spin.x  .y  .z    turning speed in degrees per second; z is spinning flat on a table
dino.shake             how hard it is being shaken, 0.0 to 1.0
dino.shaken            True for one update when a shake starts
dino.tapped            True for one update when it is tapped or knocked
dino.still             seconds since it last moved
dino.falling           True while in free fall (dropped, or held by someone in mid-jump)
dino.airtime           seconds the last free fall lasted
```

The world around it:

```
dino.temperature       degrees C, at the tip of the tail
dino.humidity          percent
dino.pressure          air pressure in hPa
dino.height            metres above where it was when the behaviour started (from the pressure)
dino.zero_height()     make "here" zero
dino.light             0.0 (dark) to 1.0 (bright daylight), at the nose
dino.lux               the same in lux
dino.heading           compass direction of the nose in degrees, 0 = north; the board must be flat
dino.magnet            magnetic field strength in microtesla: 25 to 65 from the Earth alone
```

Sound and power:

```
dino.beep(seconds=0.1)         a beep at the buzzer's loudest pitch
dino.tone(hz, seconds=0.2)     a beep at another pitch (quieter); it cannot play chords or speech
dino.quiet()                   stop any sound
dino.battery                   0.0 (empty) to 1.0 (full)
dino.plugged_in                True when USB power is there
```

Sounds do not wait: the call returns at once and the sound stops by itself.

## Examples

Physics with `dino.dt`:

```python
"""Marble: tip the dinosaur and a marble of light rolls along its back."""
NAME = "Marble"
COLOUR = "orange"


def init(dino):
    dino.my.pos = 0.5            # 0 = head, 1 = tail
    dino.my.speed = 0.0


def update(dino):
    my = dino.my
    my.speed += dino.accel.x * 2.0 * dino.dt     # nose down rolls it towards the head
    my.speed *= 0.995                            # a little friction
    my.pos += my.speed * dino.dt
    if my.pos < 0 or my.pos > 1:                 # bounce off the ends
        if abs(my.speed) > 0.3:                  # click for a real knock, not while it rests there
            dino.beep(0.02)
        my.pos = min(max(my.pos, 0), 1)
        my.speed = -my.speed * 0.6
    dino.leds.fade(0.7)                          # leave a short trail
    dino.leds.dot(my.pos, "orange")
```

Steps that follow one another, without waiting:

```python
"""Reaction timer: when the eye turns green, touch the snout as fast as you can."""
import random

NAME = "Reaction timer"
COLOUR = "green"
FULL = 0.5                       # seconds shown by the whole row of lights


def get_ready(dino):
    dino.my.state = "wait"
    dino.my.go_at = dino.time + random.uniform(2, 5)
    dino.eye = "red"
    dino.leds.clear()


def init(dino):
    get_ready(dino)


def update(dino):
    my = dino.my
    if my.state == "wait":
        if dino.snout.pressed:                   # too early: start again
            dino.tone(300, 0.3)
            get_ready(dino)
        elif dino.time >= my.go_at:
            my.state = "go"
            dino.eye = "green"
            dino.beep()
    elif my.state == "go":
        if dino.snout.pressed:
            took = dino.time - my.go_at
            best = dino.saved.get("best", FULL)
            if took < best:
                best = took
                dino.saved["best"] = took
            dino.leds.bar(min(took / FULL, 1), "yellow")
            dino.leds.dot(best / FULL, "white")  # the best so far
            dino.eye = "off"
            my.state = "show"
            my.until = dino.time + 4
    elif dino.time >= my.until:                  # "show": leave the result up, then go again
        get_ready(dino)
```

The slider, a countdown and a repeating beep:

```python
"""Timer: slide along the back to pick 1 to 18 minutes, then touch the snout to start."""
NAME = "Timer"
COLOUR = "blue"


def init(dino):
    dino.my.minutes = 3
    dino.my.left = 0.0           # seconds left; 0 means not running
    dino.my.alarm = 0.0          # seconds of alarm still to go


def update(dino):
    my = dino.my
    if my.alarm > 0:                             # time is up: flash and beep
        my.alarm -= dino.dt
        dino.leds.fill("red" if dino.wave(0.5) > 0.5 else "off")
        if dino.every(0.5):
            dino.beep(0.2)
        if dino.snout.pressed:
            my.alarm = 0
    elif my.left > 0:                            # counting down
        my.left -= dino.dt
        dino.leds.bar(my.left / (my.minutes * 60), "blue")
        if my.left <= 0:
            my.alarm = 10
        elif dino.snout.pressed:                 # touch again to cancel
            my.left = 0
    else:                                        # choosing
        if dino.slider.touched:
            my.minutes = dino.slider.led + 1
        dino.leds.bar(my.minutes / 18, "green")
        if dino.snout.pressed:
            my.left = my.minutes * 60
            dino.beep()
```

Reading a sensor:

```python
"""Thermometer: the back shows the temperature, 10 to 30 degrees. Touch a flipper for humidity."""
NAME = "Thermometer"
COLOUR = "red"


def init(dino):
    pass


def update(dino):
    if dino.front_flipper.touched or dino.rear_flipper.touched:
        dino.leds.bar(dino.humidity / 100, "cyan")
    else:
        warmth = min(max((dino.temperature - 10) / 20, 0), 1)     # 0 at 10 C, 1 at 30 C
        dino.leds.bar(warmth, dino.mix("blue", "red", warmth))
```

## What to send back

1. The complete file in one Python code block.
2. Two or three sentences for the person who will use it: what to do, and what they will see.

If the idea needs something the board cannot do (hear, speak, show text, know the time of day), say so
and build the nearest thing it can do. If the idea leaves a choice open, make the choice and say what
you chose.

## The idea

(Write the idea here: what you do to the board, what it does back, and what it is for.)
