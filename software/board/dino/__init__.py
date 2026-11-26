"""The Mosasauraboard's own library. Behaviours never import this: the host hands them a `dino` object.

    colour.py   colour names, hsv, mix
    leds.py     the row of LEDs: fill, dot, bar, fade
    touch.py    pads and the slider: touched, pressed, released, held
    core.py     Dino: everything a behaviour can read and control (see software/API.md)
    host.py     the main loop: loads behaviours, runs the menu, catches errors, limits LED current
    hw_board.py the real hardware (CircuitPython only)

Everything except hw_board.py is plain Python that runs the same on the board, on a desktop (the tests)
and in a browser (the simulator), so keep it to what CircuitPython has: no typing, dataclasses or colorsys.
"""
VERSION = "0.1"
