"""The row of LEDs along the back. Index 0 is at the head; positions run 0.0 (head) to 1.0 (tail)."""
from .colour import parse, mix

OFF = (0.0, 0.0, 0.0)


class Leds:
    def __init__(self, n=18):
        self._n = n
        self._p = [OFF] * n

    def __len__(self):
        return self._n

    def _index(self, i):
        if isinstance(i, float):
            i = int(round(i))
        if not isinstance(i, int):
            raise TypeError("an LED is chosen by a whole number, 0 to %d" % (self._n - 1))
        if i < 0:
            i += self._n
        if not 0 <= i < self._n:
            raise IndexError("there is no LED %d: they are numbered 0 to %d" % (i, self._n - 1))
        return i

    def __getitem__(self, i):
        r, g, b = self._p[self._index(i)]
        return (int(r), int(g), int(b))

    def __setitem__(self, i, colour):
        self._p[self._index(i)] = parse(colour)

    def fill(self, colour):
        self._p = [parse(colour)] * self._n

    def clear(self):
        self._p = [OFF] * self._n

    def dot(self, pos, colour, width=1):
        """A soft spot of light at pos (0 to 1), about `width` LEDs wide, added to what is there."""
        c = parse(colour)
        pos = 0.0 if pos < 0 else 1.0 if pos > 1 else pos
        centre = pos * (self._n - 1)
        reach = width if width > 0.5 else 0.5
        lo, hi = int(centre - reach), int(centre + reach) + 1
        for i in range(max(lo, 0), min(hi, self._n - 1) + 1):
            k = 1.0 - abs(i - centre) / reach
            if k > 0:
                old = self._p[i]
                self._p[i] = (max(old[0], c[0] * k), max(old[1], c[1] * k), max(old[2], c[2] * k))

    def bar(self, amount, colour, back="off"):
        """A bar from the head covering `amount` (0 to 1) of the row; the rest gets `back`."""
        c, back = parse(colour), parse(back)
        lit = (0.0 if amount < 0 else 1.0 if amount > 1 else amount) * self._n
        self._p = [c if lit >= i + 1 else back if lit <= i else mix(back, c, lit - i) for i in range(self._n)]

    def fade(self, keep=0.8):
        """Dim everything to `keep` of its brightness."""
        k = 0.0 if keep < 0 else 1.0 if keep > 1 else keep
        self._p = [(r * k, g * k, b * k) for r, g, b in self._p]

    def gradient(self, a, b):
        """Blend from colour a at the head to colour b at the tail."""
        a, b = parse(a), parse(b)
        self._p = [mix(a, b, i / (self._n - 1)) for i in range(self._n)]
