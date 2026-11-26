"""Weather tail: the back shows the temperature, from 10 degrees (short and blue) to 30 (long and red).
Touch a flipper for humidity. The eye is green when the air pressure has risen in the last hour
(fine weather on the way) and red when it has fallen."""
NAME = "Weather tail"
COLOUR = "red"
COLD, WARM = 10, 30              # degrees C at the two ends of the row
HOUR = 3600
CHANGE = 0.5                     # hPa in an hour that counts as rising or falling


def init(dino):
    dino.my.then = None          # the pressure an hour ago
    dino.my.trend = 0.0          # how much it has changed since


def update(dino):
    my = dino.my
    if my.then is None:
        my.then = dino.pressure
    if dino.every(HOUR):
        my.trend = dino.pressure - my.then
        my.then = dino.pressure
    if dino.front_flipper.touched or dino.rear_flipper.touched:
        dino.leds.bar(dino.humidity / 100, "cyan")
    else:
        warmth = min(max((dino.temperature - COLD) / (WARM - COLD), 0), 1)
        dino.leds.bar(warmth, dino.mix("blue", "red", warmth))
    if my.trend > CHANGE:
        dino.eye = "green"
    elif my.trend < -CHANGE:
        dino.eye = "red"
    else:
        dino.eye = (40, 40, 40)
