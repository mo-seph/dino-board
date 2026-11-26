"""Colour mixer: the front flipper adds red, the rear flipper adds green and the tail adds blue.
Hold more than one to mix them. The first three lights show what is going in; the rest show the mix."""
NAME = "Colour mixer"
COLOUR = "pink"


def init(dino):
    dino.my.red = dino.my.green = dino.my.blue = 0.0     # 0 to 1


def towards(value, on, step):
    """Move value a step towards 1 if on, towards 0 if not."""
    return min(value + step, 1) if on else max(value - step, 0)


def update(dino):
    my = dino.my
    step = dino.dt * 3                           # a third of a second to fade in or out
    my.red = towards(my.red, dino.front_flipper.touched, step)
    my.green = towards(my.green, dino.rear_flipper.touched, step)
    my.blue = towards(my.blue, dino.tail.touched, step)
    mixed = (255 * my.red, 255 * my.green, 255 * my.blue)
    dino.leds.fill(mixed)
    dino.leds[0] = (255 * my.red, 0, 0)
    dino.leds[1] = (0, 255 * my.green, 0)
    dino.leds[2] = (0, 0, 255 * my.blue)
    dino.leds[3] = "off"
    dino.eye = mixed
