# The `dino` API: rough draft

Draft of 2026-11-25. Nothing here is built yet. This is the proposal that the host program, the
simulator and [PROMPT.md](PROMPT.md) will all be written against, so change it here first.

## The idea

A behaviour is one small Python file. It never touches the hardware: it is handed one object, `dino`,
and reads and writes that. The host program owns everything else: the main loop, the sensors, the LED
current limit, the battery, sleep, the menu and the web page.

```python
"""Marble: tip the dinosaur and a marble of light rolls along its back."""
NAME = "Marble"
COLOUR = "orange"            # the colour of this behaviour's LED in the menu

def init(dino):              # called once, when the behaviour is chosen
    dino.my.pos = 0.5
    dino.my.speed = 0.0

def update(dino):            # called about 30 times a second
    my = dino.my
    my.speed += dino.accel.x * 2.0 * dino.dt
    my.pos += my.speed * dino.dt
    if my.pos < 0 or my.pos > 1:
        if abs(my.speed) > 0.3:      # click for a real knock, not while it rests at an end
            dino.beep(0.02)
        my.pos = min(max(my.pos, 0), 1)
        my.speed = -my.speed * 0.6
    dino.leds.fade(0.7)
    dino.leds.dot(my.pos, "orange")
```

- `update` must return quickly: no `while` loops that wait, no `time.sleep`. Use `dino.time`,
  `dino.dt` and `dino.every()` to make things happen over time.
- The LEDs keep their colours from one call to the next. The host sends them to the board after each
  `update`.
- If a behaviour raises an error, the host stops it, blinks its LED red and keeps the message for the
  web page.
- Holding the snout and sliding along the back is the menu gesture. It belongs to the host.

## Time and memory

| | |
|---|---|
| `dino.time` | Seconds since this behaviour started |
| `dino.dt` | Seconds since the last `update` (about 0.03) |
| `dino.every(seconds)` | True on one call every so many seconds |
| `dino.wave(seconds)` | A number that swings smoothly 0 → 1 → 0 once in that time |
| `dino.my` | An empty object for the behaviour's own variables: `dino.my.score = 0`. Emptied at each start |
| `dino.saved` | A small dictionary that survives switching off: `dino.saved["best"] = 0.21`. One per behaviour. Numbers and short strings only |

## Lights

18 LEDs along the back, shining off the top edge, and one eye.

| | |
|---|---|
| `dino.leds[i] = colour` | One LED. `i` is 0 at the head to 17 at the tail: the number printed on the board, minus 1 |
| `dino.leds.fill(colour)` | All of them |
| `dino.leds.clear()` | All off |
| `dino.leds.dot(pos, colour, width=1)` | A soft spot of light at `pos`, 0 (head) to 1 (tail), `width` LEDs wide, added to what is there |
| `dino.leds.bar(amount, colour, back="off")` | A bar from the head, `amount` 0 to 1 of the length; the rest gets `back` |
| `dino.leds.fade(keep=0.8)` | Dim everything to `keep` of its brightness: call every frame for trails |
| `dino.leds.gradient(a, b)` | Blend from colour `a` at the head to `b` at the tail |
| `dino.eye = colour` | The eye |
| `dino.brightness = 0.3` | Overall brightness, 0 to 1. The host limits the total current whatever this says |

**Positions match the touch slider:** `dino.leds.dot(dino.slider.pos, "white")` puts light under the finger.

**Colours** can be written three ways: a name (`"red"`, `"orange"`, `"yellow"`, `"green"`, `"cyan"`,
`"blue"`, `"purple"`, `"pink"`, `"white"`, `"off"`), a hex string (`"#ff8800"`), or three numbers
(`(255, 136, 0)`).

| | |
|---|---|
| `dino.hsv(hue, sat=1, val=1)` | A colour from the rainbow: `hue` 0 to 1 goes red, yellow, green, blue, purple, red |
| `dino.mix(a, b, amount)` | Blend: `amount` 0 gives `a`, 1 gives `b` |

## Touch

Four pads and a slider, all on the picture side.

| | |
|---|---|
| `dino.snout`, `dino.tail`, `dino.front_flipper`, `dino.rear_flipper` | The pads |
| `dino.slider` | The strip along the back, under the LEDs |

Every one of them has:

| | |
|---|---|
| `.touched` | True all the time a finger is on it |
| `.pressed` | True for one `update` only, when the finger arrives |
| `.released` | True for one `update` only, when it leaves |
| `.held` | Seconds the finger has been there; 0 when not touched |

The slider also has:

| | |
|---|---|
| `.pos` | Where the finger is, 0 (head) to 1 (tail). Keeps its last value after the finger lifts |
| `.led` | The LED above the finger, 0 to 17 |
| `.speed` | How fast the finger is moving, in lengths per second: positive towards the tail |

## Movement

| | |
|---|---|
| `dino.accel.x`, `.y`, `.z` | Which way is up, and how hard it is being pushed, in g. `x` points out of the nose, `y` out of the back (the LED edge), `z` out of the picture side. Held still, the direction pointing at the sky reads +1 |
| `dino.up` | The part pointing at the sky: `"spine"`, `"belly"`, `"nose"`, `"tail"`, `"face"` (lying picture side up) or `"underside"` |
| `dino.spin.x`, `.y`, `.z` | Turning speed in degrees per second. `z` is spinning flat on a table |
| `dino.shake` | How hard it is being shaken, 0 to 1 |
| `dino.shaken` | True for one `update` when a shake starts |
| `dino.tapped` | True for one `update` when it is tapped or knocked |
| `dino.still` | Seconds since it last moved |
| `dino.falling` | True while it is in free fall (dropped, thrown, or held by someone in mid-jump) |
| `dino.airtime` | How long the last free fall lasted, in seconds |

## The world around it

| | |
|---|---|
| `dino.temperature` | Degrees C, measured at the tip of the tail |
| `dino.humidity` | Percent, also at the tail tip |
| `dino.pressure` | Air pressure in hPa (about 1013 at sea level) |
| `dino.height` | Metres above where it was when the behaviour started, worked out from the pressure |
| `dino.zero_height()` | Call it to make "here" zero |
| `dino.light` | 0 (dark) to 1 (bright daylight), measured at the nose |
| `dino.lux` | The same in lux |
| `dino.heading` | Compass direction the nose points, 0 to 360 degrees, 0 = north. Needs the board held flat |
| `dino.magnet` | Strength of the magnetic field in microtesla. The Earth alone is 25 to 65; a magnet nearby is far more |

## Sound

One small buzzer: beeps, not music.

| | |
|---|---|
| `dino.beep(seconds=0.1)` | A beep at the buzzer's loudest pitch |
| `dino.tone(hz, seconds=0.2)` | A beep at another pitch (quieter) |
| `dino.quiet()` | Stop any sound |

Sounds do not wait: the call returns at once and the host stops the sound when its time is up. A new
sound replaces the one playing.

## Power

| | |
|---|---|
| `dino.battery` | 0 (empty) to 1 (full) |
| `dino.plugged_in` | True when USB power is there |

## Later: phone, page and other boards

Not in the first version. Named here so behaviours can be written with them in mind.

| | |
|---|---|
| `dino.show(label, value)` | Put a live reading on the board's web page: `dino.show("Height", dino.height)` |
| `dino.inbox` | Messages sent from the page to this behaviour |
| `dino.herd.send(name, value)` | Send a small message to the other boards in the same herd |
| `dino.herd.messages` | Messages that arrived from them since the last `update` |

## Open questions

- **Frame rate.** 30 a second is a guess until it runs on the board; reading six sensors and 19 LEDs
  each frame may be slower. Timing in a behaviour is only as fine as one frame.
- **LED numbers.** Code counts 0 to 17 and the board is printed 1 to 18. The alternative is to count
  from 1 in code too, which is friendlier to people and odd to every model and programmer.
- **Compass with the LEDs lit.** LED current makes its own magnetic field. The host may have to read
  the compass in dim moments, or `dino.heading` will wander when the lights are bright.
- **`dino.height`.** The sensor's maker claims resolution of a few centimetres; what it does in a
  draughty room is not known.
- **`dino.tapped` and `dino.falling`.** Both come from the motion sensor's own detectors; thresholds
  will need tuning on the real board.
- **Buzzer.** Its loudness away from its own pitch (4 kHz) is not known.
