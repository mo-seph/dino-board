"""Magnet hunt: someone hides a magnet. Sweep the dinosaur about: the lights grow, turn red and tick
faster as it gets near. Touch the snout, away from any magnet, to set "nothing here"."""
import math

NAME = "Magnet hunt"
COLOUR = "purple"


def init(dino):
    dino.my.rest = None          # the field with no magnet about: the Earth's own
    dino.my.near = 0.0           # 0 = nothing, 1 = right on top of it


def update(dino):
    my = dino.my
    if my.rest is None or dino.snout.pressed:
        my.rest = dino.magnet
    extra = abs(dino.magnet - my.rest)                               # microtesla more than the Earth's
    near = min(math.log(1 + extra / 5) / math.log(401), 1)           # 5 is faint, 2000 is touching
    my.near += (near - my.near) * min(dino.dt * 8, 1)
    dino.leds.bar(my.near, dino.mix("blue", "red", my.near))
    dino.eye = "white" if my.near > 0.9 else "off"
    if my.near > 0.1 and dino.every(0.6 - 0.5 * my.near):
        dino.tone(2000 + 2000 * my.near, 0.02)
