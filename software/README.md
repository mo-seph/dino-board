# Software for the Mosasauraboard

Started 2026-11-26, before the boards arrived. Everything that does not need the real hardware is
written and tested; the one file that talks to the hardware is a draft that has never run.

## What is here

| Where | What |
|---|---|
| `API.md` | What a behaviour can read and control: the `dino` object. Change it here first |
| `IDEAS.md` | What the board can do, for people thinking up behaviours |
| `PROMPT.md` | The page to give an AI model, with an idea, to get a behaviour written |
| `BROKERS.md` | Notes on message services for boards in different places |
| `board/` | Everything that goes on the board's drive |
| `board/dino/` | The library: `colour`, `leds`, `touch`, `core` (the `dino` object), `host` (main loop, menu, errors), `hw_board` (the real hardware) |
| `board/behaviours/` | One file for each light: `NN_name.py`, NN = the number printed beside the LED |
| `board/code.py`, `board/boot.py` | CircuitPython's start-up files |
| `sim/hw_fake.py` | A pretend board, used by the tests and the web simulator |
| `tests/` | `python3 software/tests/run_tests.py` |
| `../web/` | The website: a landing page, the simulator, and the write-with-an-AI page |

## How it fits together

A behaviour is a file with `init(dino)` and `update(dino)`. The **host** calls `update` about 30 times a
second and does everything else: reads the hardware, runs the menu (hold the snout, slide along the
back), catches a behaviour's errors and blinks its light red, limits the LED current to 0.3 A, stops
sounds when their time is up, and saves what behaviours put in `dino.saved`.

The host reaches the hardware through five calls (`now`, `read`, `show`, `tone` / `quiet`, `sleep`).
`hw_board.Board` answers them on the real board and `hw_fake.FakeHardware` in the tests and the
simulator, so the same library and the same behaviours run in all three places. Keep `board/dino/`
(apart from `hw_board.py`) to plain Python that CircuitPython has: no `typing`, `dataclasses` or
`colorsys`.

## Testing

```bash
python3 software/tests/run_tests.py
```

45 tests, nothing to install. They cover the library, the host (menu, errors with line numbers, the
current limit, saving, a read-only drive), each of the eight behaviours doing its job, twenty minutes of
random handling for each, every code example in `PROMPT.md` and `API.md`, and the Python that the
simulator page runs.

## The simulator

It needs a web server, because the page fetches the Python files:

```bash
python3 -m http.server 8765
```

Run that in the repository's top folder and open `http://localhost:8765/web/sim/`. The page loads
Pyodide (Python in the browser) from the jsDelivr network, so it needs the internet the first time.

**Not yet seen in a real browser** (2026-11-26). The page's script was run under Node against a
stand-in page and a stand-in Python, and its Python side is tested; the look of it, the touch handling
and the use of a tablet's own movement sensor have not been tried. The movement sensor part is marked
experimental on the page: browsers disagree about signs.

## Putting it on a board

Not done yet. When the boards arrive, after the checks in `NOTES.md`, "When the boards arrive":

1. Install CircuitPython. The module is an ESP32-S3-MINI-1-N4R2 (4 MB flash, 2 MB PSRAM). The build to
   try first is `generic_esp32s3_supermini`: its status LED is GPIO48, which is the eye, and it claims
   no LED power pin. Avoid the Adafruit Feather ESP32-S3 4 MB / 2 MB build: it drives GPIO21 as its
   LED power pin, and GPIO21 here is the LED rail's switch. (Read from the builds' board files on
   2026-11-26; no build has been tried on this board.)
2. Copy into `/lib` on the drive: `adafruit_bus_device`, `adafruit_register`, `adafruit_mpr121`,
   `adafruit_lsm6ds`, `adafruit_sht4x`, `adafruit_ltr329_ltr303`, `adafruit_bmp5xx`, `adafruit_qmc5883p`.
3. Copy the contents of `software/board/` to the drive.
4. Work through every line marked `CHECK` in `board/dino/hw_board.py`: LED colour order, the signs of
   the three movement directions, the compass against a real one, the slider's ends, the light
   sensor's scale, sleep on a flat battery.
5. Only then delete `KEEP_USB_DRIVE` from the drive. With it gone the drive is hidden unless the snout
   is held at switch-on, and the board can save scores and (later) take behaviours over Wi-Fi.

## Not written yet

- The board's own web page (join Wi-Fi, see the 18 slots, paste a behaviour, read an error).
- Messages between boards (`dino.herd`) and to a phone (`dino.show`, `dino.inbox`). See `BROKERS.md`.
- Sleep: after a while untouched, and waking on movement.
- The motion sensor's own tap and free-fall detectors (the library does not expose them; for now both
  are worked out in `core.py` from the frame-by-frame readings, which is coarser).
