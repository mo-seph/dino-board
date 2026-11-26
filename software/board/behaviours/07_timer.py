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
