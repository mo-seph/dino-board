"""Colours. A colour may be written as a name ("red"), a hex string ("#ff8800") or three numbers
(255, 136, 0). Inside the library a colour is always a tuple of three floats, 0 to 255."""

NAMES = {
    "off": (0, 0, 0), "black": (0, 0, 0),
    "red": (255, 0, 0), "orange": (255, 110, 0), "yellow": (255, 210, 0), "green": (0, 255, 0),
    "cyan": (0, 255, 255), "blue": (0, 0, 255), "purple": (150, 0, 255), "pink": (255, 60, 150),
    "white": (255, 255, 255),
}
_ORDER = ("red", "orange", "yellow", "green", "cyan", "blue", "purple", "pink", "white", "off")


def _clip(v):
    return 0.0 if v < 0 else 255.0 if v > 255 else float(v)


def parse(c):
    """Any of the three ways of writing a colour -> (r, g, b) floats."""
    if isinstance(c, str):
        key = c.strip().lower()
        if key in NAMES:
            return tuple(float(v) for v in NAMES[key])
        if key.startswith("#") and len(key) == 7:
            try:
                return tuple(float(int(key[i:i + 2], 16)) for i in (1, 3, 5))
            except ValueError:
                pass
        raise ValueError('"%s" is not a colour. Use one of: %s; or "#rrggbb"; or three numbers'
                         % (c, ", ".join(_ORDER)))
    try:
        r, g, b = c
    except (TypeError, ValueError):
        raise ValueError("%r is not a colour. Use a name, \"#rrggbb\" or three numbers 0 to 255" % (c,))
    return (_clip(r), _clip(g), _clip(b))


def mix(a, b, amount):
    """Blend two colours: amount 0 gives a, 1 gives b."""
    a, b = parse(a), parse(b)
    t = 0.0 if amount < 0 else 1.0 if amount > 1 else amount
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t)


def hsv(hue, sat=1.0, val=1.0):
    """A rainbow colour: hue 0 to 1 goes red, yellow, green, cyan, blue, purple, back to red."""
    h = (hue % 1.0) * 6.0
    i = int(h)
    f = h - i
    sat = min(max(sat, 0.0), 1.0)
    v = min(max(val, 0.0), 1.0) * 255.0
    p, q, t = v * (1 - sat), v * (1 - sat * f), v * (1 - sat * (1 - f))
    return ((v, t, p), (q, v, p), (p, v, t), (p, q, v), (t, p, v), (v, p, q))[i % 6]
