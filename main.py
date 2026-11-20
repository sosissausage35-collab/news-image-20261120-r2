#!/usr/bin/env python3
"""news-image-20261120, round 2 -- "The day, hour by hour".

One image that sums up Friday 20 November 2026 as a vertical timeline:
ten stories placed at the hour they were first reported, plus four more
in an "also today" band, on a dark navy page. Every story on it happened,
or was first reported, on 20 November 2026; nothing from an earlier day
is on the page.

Pure Python standard library. No network, no clock, no randomness:
two runs write byte-identical PNGs (1024x1024, well under 1 MiB).

Run it:  python3 main.py            (writes entry.png next to main.py)
          python3 main.py out.png   (writes to the given path)
          MAKEFUN_OUTPUT_DIR=out python3 main.py   (writes out/entry.png)
"""

import os
import struct
import sys
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- font
# A 5x7 bitmap font drawn for this poster. Each glyph is seven rows of
# five bits, most significant bit on the left, stored as seven ints.
FONT = {
    "A": (0x0E, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    "B": (0x1E, 0x11, 0x11, 0x1E, 0x11, 0x11, 0x1E),
    "C": (0x0E, 0x11, 0x10, 0x10, 0x10, 0x11, 0x0E),
    "D": (0x1E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x1E),
    "E": (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x1F),
    "F": (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x10),
    "G": (0x0E, 0x11, 0x10, 0x17, 0x11, 0x11, 0x0F),
    "H": (0x11, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    "I": (0x0E, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0E),
    "J": (0x07, 0x02, 0x02, 0x02, 0x02, 0x12, 0x0C),
    "K": (0x11, 0x12, 0x14, 0x18, 0x14, 0x12, 0x11),
    "L": (0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x1F),
    "M": (0x11, 0x1B, 0x15, 0x15, 0x11, 0x11, 0x11),
    "N": (0x11, 0x19, 0x15, 0x13, 0x11, 0x11, 0x11),
    "O": (0x0E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    "P": (0x1E, 0x11, 0x11, 0x1E, 0x10, 0x10, 0x10),
    "Q": (0x0E, 0x11, 0x11, 0x11, 0x15, 0x12, 0x0D),
    "R": (0x1E, 0x11, 0x11, 0x1E, 0x14, 0x12, 0x11),
    "S": (0x0F, 0x10, 0x10, 0x0E, 0x01, 0x01, 0x1E),
    "T": (0x1F, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04),
    "U": (0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    "V": (0x11, 0x11, 0x11, 0x11, 0x11, 0x0A, 0x04),
    "W": (0x11, 0x11, 0x11, 0x15, 0x15, 0x15, 0x0A),
    "X": (0x11, 0x11, 0x0A, 0x04, 0x0A, 0x11, 0x11),
    "Y": (0x11, 0x11, 0x0A, 0x04, 0x04, 0x04, 0x04),
    "Z": (0x1F, 0x01, 0x02, 0x04, 0x08, 0x10, 0x1F),
    "0": (0x0E, 0x11, 0x13, 0x15, 0x19, 0x11, 0x0E),
    "1": (0x04, 0x0C, 0x04, 0x04, 0x04, 0x04, 0x0E),
    "2": (0x0E, 0x11, 0x01, 0x02, 0x04, 0x08, 0x1F),
    "3": (0x1F, 0x02, 0x04, 0x02, 0x01, 0x11, 0x0E),
    "4": (0x02, 0x06, 0x0A, 0x12, 0x1F, 0x02, 0x02),
    "5": (0x1F, 0x10, 0x1E, 0x01, 0x01, 0x11, 0x0E),
    "6": (0x06, 0x08, 0x10, 0x1E, 0x11, 0x11, 0x0E),
    "7": (0x1F, 0x01, 0x02, 0x04, 0x08, 0x08, 0x08),
    "8": (0x0E, 0x11, 0x11, 0x0E, 0x11, 0x11, 0x0E),
    "9": (0x0E, 0x11, 0x11, 0x0F, 0x01, 0x02, 0x0C),
}

# ---------------------------------------------------------------- canvas
class Canvas:
    """A plain RGB canvas with a few drawing primitives."""

    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bg * (w * h))

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = c

    def rect(self, x, y, w, h, c):
        for yy in range(y, y + h):
            if 0 <= yy < self.h:
                x0 = max(x, 0)
                x1 = min(x + w, self.w)
                if x1 > x0:
                    i = (yy * self.w + x0) * 3
                    self.px[i:i + (x1 - x0) * 3] = c * (x1 - x0)

    def hline(self, x0, x1, y, c):
        self.rect(x0, y, x1 - x0, 1, c)

    def vline(self, x, y0, y1, c):
        self.rect(x, y0, 1, y1 - y0, c)

    def disc(self, cx, cy, r, c):
        """Filled circle."""
        for dy in range(-r, r + 1):
            dx = int((r * r - dy * dy) ** 0.5)
            self.rect(cx - dx, cy + dy, 2 * dx + 1, 1, c)

    def ring(self, cx, cy, r, c):
        """One-pixel circle outline."""
        for deg in range(360):
            import math
            x = cx + int(round(r * math.cos(math.radians(deg))))
            y = cy + int(round(r * math.sin(math.radians(deg))))
            self.set(x, y, c)

    def glyph(self, x, y, ch, s, c):
        rows = FONT.get(ch)
        if rows is None:
            return
        for ry, bits in enumerate(rows):
            for col in range(5):
                if bits & (1 << (4 - col)):
                    self.rect(x + col * s, y + ry * s, s, s, c)

    def text_w(self, s, scale):
        return len(s) * 6 * scale - scale if s else 0

    def text(self, x, y, s, c, scale):
        for ch in s:
            self.glyph(x, y, ch, scale, c)
            x += 6 * scale

    def text_center(self, cx, y, s, c, scale):
        self.text(cx - self.text_w(s, scale) // 2, y, s, c, scale)

    def text_right(self, x, y, s, c, scale):
        self.text(x - self.text_w(s, scale), y, s, c, scale)


# ---------------------------------------------------------------- png
def write_png(path, cv):
    raw = b"".join(
        b"\x00" + bytes(cv.px[y * W * 3:(y + 1) * W * 3]) for y in range(H)
    )

    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        return out + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(raw, 9))
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)

# Lowercase and punctuation, same 5x7 grid.
FONT.update({
    "a": (0x00, 0x00, 0x0E, 0x01, 0x0F, 0x11, 0x0F),
    "b": (0x10, 0x10, 0x1E, 0x11, 0x11, 0x11, 0x1E),
    "c": (0x00, 0x00, 0x0E, 0x10, 0x10, 0x11, 0x0E),
    "d": (0x01, 0x01, 0x0F, 0x11, 0x11, 0x11, 0x0F),
    "e": (0x00, 0x00, 0x0E, 0x11, 0x1F, 0x10, 0x0E),
    "f": (0x06, 0x09, 0x08, 0x1E, 0x08, 0x08, 0x08),
    "g": (0x00, 0x00, 0x0F, 0x11, 0x11, 0x0F, 0x0E),
    "h": (0x10, 0x10, 0x1E, 0x11, 0x11, 0x11, 0x11),
    "i": (0x04, 0x00, 0x0C, 0x04, 0x04, 0x04, 0x0E),
    "j": (0x02, 0x00, 0x06, 0x02, 0x02, 0x12, 0x0C),
    "k": (0x10, 0x10, 0x12, 0x14, 0x18, 0x14, 0x12),
    "l": (0x0C, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0E),
    "m": (0x00, 0x00, 0x1A, 0x15, 0x15, 0x15, 0x15),
    "n": (0x00, 0x00, 0x1E, 0x11, 0x11, 0x11, 0x11),
    "o": (0x00, 0x00, 0x0E, 0x11, 0x11, 0x11, 0x0E),
    "p": (0x00, 0x00, 0x1E, 0x11, 0x11, 0x1E, 0x10),
    "q": (0x00, 0x00, 0x0F, 0x11, 0x11, 0x0F, 0x01),
    "r": (0x00, 0x00, 0x16, 0x19, 0x10, 0x10, 0x10),
    "s": (0x00, 0x00, 0x0F, 0x10, 0x0E, 0x01, 0x1E),
    "t": (0x08, 0x08, 0x1E, 0x08, 0x08, 0x08, 0x06),
    "u": (0x00, 0x00, 0x11, 0x11, 0x11, 0x13, 0x0D),
    "v": (0x00, 0x00, 0x11, 0x11, 0x11, 0x0A, 0x04),
    "w": (0x00, 0x00, 0x11, 0x11, 0x15, 0x15, 0x0A),
    "x": (0x00, 0x00, 0x11, 0x0A, 0x04, 0x0A, 0x11),
    "y": (0x00, 0x00, 0x11, 0x11, 0x0F, 0x01, 0x0E),
    "z": (0x00, 0x00, 0x1F, 0x02, 0x04, 0x08, 0x1F),
    " ": (0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00),
    ".": (0x00, 0x00, 0x00, 0x00, 0x00, 0x0C, 0x0C),
    ",": (0x00, 0x00, 0x00, 0x00, 0x0C, 0x04, 0x08),
    ":": (0x00, 0x0C, 0x0C, 0x00, 0x0C, 0x0C, 0x00),
    ";": (0x00, 0x0C, 0x0C, 0x00, 0x0C, 0x04, 0x08),
    "!": (0x04, 0x04, 0x04, 0x04, 0x04, 0x00, 0x04),
    "?": (0x0E, 0x11, 0x01, 0x02, 0x04, 0x00, 0x04),
    "'": (0x04, 0x04, 0x08, 0x00, 0x00, 0x00, 0x00),
    '"': (0x0A, 0x0A, 0x00, 0x00, 0x00, 0x00, 0x00),
    "-": (0x00, 0x00, 0x00, 0x0E, 0x00, 0x00, 0x00),
    "(": (0x02, 0x04, 0x08, 0x08, 0x08, 0x04, 0x02),
    ")": (0x08, 0x04, 0x02, 0x02, 0x02, 0x04, 0x08),
    "/": (0x01, 0x02, 0x02, 0x04, 0x08, 0x08, 0x10),
    "&": (0x0C, 0x12, 0x14, 0x08, 0x15, 0x12, 0x0D),
    "%": (0x19, 0x1A, 0x02, 0x04, 0x08, 0x0B, 0x13),
    "$": (0x04, 0x0F, 0x14, 0x0E, 0x05, 0x1E, 0x04),
    "#": (0x0A, 0x0A, 0x1F, 0x0A, 0x1F, 0x0A, 0x0A),
    "@": (0x0E, 0x11, 0x17, 0x15, 0x16, 0x10, 0x0E),
    "+": (0x00, 0x04, 0x04, 0x1F, 0x04, 0x04, 0x00),
    "*": (0x00, 0x15, 0x0E, 0x15, 0x00, 0x00, 0x00),
    "=": (0x00, 0x00, 0x1F, 0x00, 0x1F, 0x00, 0x00),
    "<": (0x02, 0x04, 0x08, 0x10, 0x08, 0x04, 0x02),
    ">": (0x08, 0x04, 0x02, 0x01, 0x02, 0x04, 0x08),
    "_": (0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x1F),
})

# ---------------------------------------------------------------- palette
NAVY = bytes((12, 22, 38))        # page background
NAVY2 = bytes((17, 32, 54))       # header band
RAIL = bytes((46, 74, 107))       # timeline rail
SEPARATOR = bytes((27, 48, 73))   # row separators
WHITE = bytes((255, 255, 255))
GOLD = bytes((232, 184, 75))
DETAIL = bytes((199, 211, 224))   # detail text
MUTED = bytes((139, 160, 184))    # footer text
BAND_BG = bytes((16, 30, 50))     # also-today band
BAND_EDGE = bytes((58, 90, 128))  # also-today border

# Category colours.
CAT = {
    "WAR": bytes((248, 113, 113)),
    "ENERGY": bytes((251, 191, 36)),
    "SPACE": bytes((167, 139, 250)),
    "WEATHER": bytes((45, 212, 191)),
    "TALKS": bytes((96, 165, 250)),
    "FLYING": bytes((147, 197, 253)),
    "TECH": bytes((52, 211, 153)),
    "MARKETS": bytes((74, 222, 128)),
    "CULTURE": bytes((244, 114, 182)),
}

# ---------------------------------------------------------------- stories
# (time, category, headline, detail) -- every one happened, or was first
# reported, on Friday 20 November 2026. Times are UTC, as first reported.
TIMELINE = [
    ("01:23", "CULTURE", "GTA 6 OUTSELLS THE ODYSSEY",
     "sales already pass The Odyssey's $1.80bn global run"),
    ("01:27", "ENERGY", "TANKER ON FIRE OFF HORMUZ",
     "tanker catches fire after hitting a mine east of Hormuz"),
    ("01:30", "SPACE", "HAYABUSA2 GROUNDED",
     "engine trouble ends Japan's asteroid landing plan"),
    ("01:43", "WEATHER", "CYCLONE AKVAN: 300,000 EVACUATED",
     "three lakh evacuated in Odisha; 423 rescue teams out"),
    ("01:43", "TALKS", "EUROPE READY FOR RUSSIA TALKS",
     "leaders say Europe is ready to talk on ending the war"),
    ("03:47", "WAR", "HOUTHIS HIT RIYADH",
     "drones and missiles hit four Saudi targets; a tower damaged"),
    ("04:07", "WAR", "KYIV HIT BY FOUR MISSILES",
     "four ballistic missiles strike the capital in the early hours"),
    ("04:22", "FLYING", "DRONES SHUT GENOA AIRPORT",
     "unidentified drones halt all flights for four hours overnight"),
    ("TODAY", "TECH", "ANTHROPIC'S STOCK DEBUT",
     "the first purely AI company lists on the stock market"),
    ("TODAY", "MARKETS", "KOREA'S EXPORTS TOP $1 TRILLION",
     "annual exports pass $1 trillion for the first time"),
]

ALSO = [
    "White House cyber chief ousted after a wave of US tech outages",
    "Taiwan unveils five measures to steady stocks; short-selling limits begin",
    "Migrant boat sinks off Senegal; dozens missing",
    "Fiona the hippo dies at Cincinnati Zoo after swallowing a hat",
]

# ---------------------------------------------------------------- drawing
RAIL_X = 170
TEXT_X = 196
ROW_Y0 = 136
ROW_H = 68


def draw():
    cv = Canvas(W, H, NAVY)

    # Header band: the date, large, and what the page is.
    cv.rect(0, 0, W, 116, NAVY2)
    cv.hline(24, 1000, 8, GOLD)
    cv.text_center(W // 2, 24, "FRIDAY 20 NOVEMBER 2026", WHITE, 6)
    cv.text_center(W // 2, 78, "THE WORLD IN ONE DAY, AS IT HAPPENED",
                   GOLD, 3)
    cv.hline(24, 1000, 108, GOLD)

    # Timeline rail.
    first_y = ROW_Y0 + 12
    last_y = ROW_Y0 + (len(TIMELINE) - 1) * ROW_H + 12
    cv.rect(RAIL_X - 1, first_y, 3, last_y - first_y, RAIL)

    for i, (when, cat, head, detail) in enumerate(TIMELINE):
        y = ROW_Y0 + i * ROW_H
        colour = CAT[cat]
        # Time and category, right-aligned in the left column.
        cv.text_right(148, y + 2, when, WHITE, 3)
        cv.text_right(148, y + 30, cat, colour, 2)
        # Node on the rail.
        cv.disc(RAIL_X, y + 12, 9, colour)
        cv.ring(RAIL_X, y + 12, 11, WHITE)
        # Headline and one line of detail.
        cv.text(TEXT_X, y + 2, head, WHITE, 3)
        cv.text(TEXT_X, y + 30, detail, DETAIL, 2)
        # Separator between rows.
        if i < len(TIMELINE) - 1:
            cv.hline(TEXT_X, 1000, y + 58, SEPARATOR)

    # Also-today band: four more verified stories from the same day.
    bx0, by0, bx1, by1 = 24, 832, 1000, 958
    cv.rect(bx0, by0, bx1 - bx0, by1 - by0, BAND_BG)
    cv.hline(bx0, bx1, by0, BAND_EDGE)
    cv.hline(bx0, bx1, by1 - 1, BAND_EDGE)
    cv.vline(bx0, by0, by1, BAND_EDGE)
    cv.vline(bx1 - 1, by0, by1, BAND_EDGE)
    cv.text(40, 846, "ALSO ON FRIDAY 20 NOVEMBER", GOLD, 2)
    for j, line in enumerate(ALSO):
        ly = 872 + j * 20
        cv.rect(40, ly + 4, 6, 6, GOLD)
        cv.text(56, ly, line, DETAIL, 2)

    # Footer: the rule the whole page follows.
    cv.text_center(
        W // 2, 976,
        "EVERY EVENT HAPPENED OR WAS FIRST REPORTED ON FRIDAY 20 NOVEMBER 2026",
        MUTED, 2)
    return cv


def main(argv):
    if len(argv) > 1:
        path = argv[1]
    elif os.environ.get("MAKEFUN_OUTPUT_DIR"):
        path = os.path.join(os.environ["MAKEFUN_OUTPUT_DIR"], "entry.png")
    else:
        path = "entry.png"
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    write_png(path, draw())
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
