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
