"""Jump height: hold the dinosaur and jump. The lights show how high you went, 2.5 cm for each light.
The red light is your best. Hold the snout for two seconds to forget the best."""
NAME = "Jump height"
COLOUR = "yellow"
G = 9.81                         # metres per second per second
FULL = 0.45                      # metres shown by the whole row of lights


def init(dino):
    dino.my.height = 0.0
    dino.my.best = dino.saved.get("best", 0.0)
    dino.my.was_falling = False


def update(dino):
    my = dino.my
    if my.was_falling and not dino.falling:      # just landed
        t = min(dino.airtime, 1.0)
        my.height = G * t * t / 8                # half the time going up, half coming down
        if my.height > my.best:
            my.best = my.height
            dino.saved["best"] = my.best
            dino.beep(0.3)
        else:
            dino.beep(0.05)
    my.was_falling = dino.falling
    if dino.snout.held > 2 and my.best > 0:
        my.best = my.height = 0.0
        dino.saved["best"] = 0.0
        dino.tone(500, 0.2)
    dino.eye = "white" if dino.falling else "off"
    dino.leds.bar(min(my.height / FULL, 1), "yellow")
    if my.best > 0:
        dino.leds.dot(min(my.best / FULL, 1), "red")
