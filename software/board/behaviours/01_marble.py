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
