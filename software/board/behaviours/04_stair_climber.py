"""Stair climber: touch the snout at the bottom, then carry the dinosaur up. One more light for every
25 cm you climb. The eye turns blue if you go below where you started."""
NAME = "Stair climber"
COLOUR = "cyan"
STEP = 0.25                      # metres for each light


def init(dino):
    dino.my.smooth = 0.0


def update(dino):
    my = dino.my
    if dino.snout.pressed:                       # "here" is the bottom
        dino.zero_height()
        my.smooth = 0.0
        dino.beep(0.05)
    my.smooth += (dino.height - my.smooth) * min(dino.dt * 2, 1)     # steady the reading
    dino.leds.bar(min(max(my.smooth, 0) / (STEP * 18), 1), "cyan")
    dino.eye = "blue" if my.smooth < -STEP else "off"
