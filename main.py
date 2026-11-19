#!/usr/bin/env python3
"""World news image: Thursday 19 November 2026.

Draws a one-page newspaper front page in pure stdlib Python and writes
$MAKEFUN_OUTPUT_DIR/entry.png (default /output). Deterministic: no clock,
no randomness, fixed colours and layout, so two runs are byte-identical.

Stories (all happened or first reported on 19 November 2026):
  1. Trump, Xi and Putin hold first three-way summit, Shenzhen (APEC).
  2. ICJ rules today on Myanmar Rohingya genocide case, The Hague.
  3. Ukraine strikes the Crimean Bridge for the third time in a week.
  4. Iran hits Gulf targets; 3 tankers struck by mines near Hormuz.
  5. Anthropic debuts on Nasdaq as ANT after an $83-a-share IPO.
  6. Tonga declares a 27-day emergency as El Nino drought worsens.
"""

import os
import struct
import zlib

W = 1024
H = 1024

# ---- palette -------------------------------------------------------------
NAVY = (18, 35, 63)
GOLD = (217, 164, 65)
PAPER = (247, 243, 234)
WHITE = (255, 255, 255)
INK = (26, 26, 26)
MUTED = (85, 85, 85)
BORDER = (216, 210, 196)
RED = (192, 57, 43)
TEAL = (31, 122, 110)
BLUE = (43, 98, 168)
ORANGE = (214, 106, 24)
GREEN = (46, 125, 50)
PURPLE = (106, 76, 147)
TINT = (238, 234, 224)

# ---- 5x7 bitmap font (7 rows of 5 bits, '#' = on) ------------------------
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
}


def text_width(text, scale):
    return len(text) * (5 * scale + scale) - scale


def wrap(text, max_chars):
    words = text.split(" ")
    lines = []
    cur = ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if len(trial) <= max_chars:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# ---- canvas ---------------------------------------------------------------
class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(w * h * 3)
        self.fill_rect(0, 0, w, h, bg)

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = color

    def fill_rect(self, x, y, w, h, color):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.px[i], self.px[i + 1], self.px[i + 2] = color

    def rect_border(self, x, y, w, h, color, t=2):
        self.fill_rect(x, y, w, t, color)
        self.fill_rect(x, y + h - t, w, t, color)
        self.fill_rect(x, y, t, h, color)
        self.fill_rect(x + w - t, y, t, h, color)

    def line(self, x0, y0, x1, y1, color, t=1):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            for a in range(t):
                for b in range(t):
                    self.set(x0 + a, y0 + b, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, color):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                    self.set(xx, yy, color)

    def circle_outline(self, cx, cy, r, color, t=3):
        for yy in range(cy - r - t, cy + r + t + 1):
            for xx in range(cx - r - t, cx + r + t + 1):
                d = ((xx - cx) ** 2 + (yy - cy) ** 2) ** 0.5
                if abs(d - r) <= t / 2.0 + 0.5:
                    self.set(xx, yy, color)

    def triangle(self, x0, y0, x1, y1, x2, y2, color):
        ys = sorted([y0, y1, y2])
        for yy in range(ys[0], ys[2] + 1):
            xs = []
            for (ax, ay, bx, by) in ((x0, y0, x1, y1), (x1, y1, x2, y2),
                                     (x2, y2, x0, y0)):
                if ay == by:
                    continue
                if min(ay, by) <= yy <= max(ay, by):
                    xs.append(ax + (bx - ax) * (yy - ay) / (by - ay))
            if len(xs) >= 2:
                for xx in range(int(min(xs)), int(max(xs)) + 1):
                    self.set(xx, yy, color)

    def draw_text(self, x, y, text, scale, color):
        cx = x
        for ch in text:
            glyph = FONT.get(ch, FONT[" "])
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits[col] == "1":
                        self.fill_rect(cx + col * scale, y + row * scale,
                                       scale, scale, color)
            cx += 6 * scale
        return cx

    def draw_text_centered(self, y, text, scale, color):
        x = (self.w - text_width(text, scale)) // 2
        self.draw_text(x, y, text, scale, color)


# ---- story pictograms ------------------------------------------------------
def icon_summit(c, cx, cy, color):
    # three leaders at a table
    for dx in (-34, 0, 34):
        c.circle(cx + dx, cy - 18, 13, color)
        c.fill_rect(cx + dx - 16, cy - 2, 32, 20, color)
    c.fill_rect(cx - 52, cy + 22, 104, 6, GOLD)


def icon_court(c, cx, cy, color):
    # scales of justice
    c.fill_rect(cx - 3, cy - 44, 6, 88, color)
    c.fill_rect(cx - 44, cy - 44, 88, 6, color)
    c.circle(cx, cy - 50, 7, color)
    for dx in (-40, 40):
        c.line(cx + dx, cy - 38, cx + dx, cy - 14, color, 3)
        c.triangle(cx + dx - 18, cy - 14, cx + dx + 18, cy - 14,
                   cx + dx, cy + 12, color)
    c.fill_rect(cx - 30, cy + 44, 60, 6, GOLD)


def icon_bridge(c, cx, cy, color):
    # suspension bridge with a blast above it
    c.fill_rect(cx - 48, cy - 6, 8, 44, color)
    c.fill_rect(cx + 40, cy - 6, 8, 44, color)
    c.fill_rect(cx - 52, cy + 34, 104, 8, color)
    # main cable as a shallow sagging curve, with suspenders
    c.line(cx - 48, cy - 6, cx - 24, cy + 8, color, 3)
    c.line(cx - 24, cy + 8, cx, cy + 12, color, 3)
    c.line(cx, cy + 12, cx + 24, cy + 8, color, 3)
    c.line(cx + 24, cy + 8, cx + 48, cy - 6, color, 3)
    c.line(cx - 24, cy + 8, cx - 24, cy + 34, color, 2)
    c.line(cx, cy + 12, cx, cy + 34, color, 2)
    c.line(cx + 24, cy + 8, cx + 24, cy + 34, color, 2)
    for dx, dy in ((-16, -36), (0, -46), (16, -36), (-28, -24), (28, -24)):
        c.line(cx, cy - 28, cx + dx, cy + dy, RED, 4)
    c.circle(cx, cy - 28, 8, RED)


def icon_tanker(c, cx, cy, color):
    # tanker hull with a bow wedge, cabin, flame, waves
    c.fill_rect(cx - 48, cy + 8, 84, 22, color)
    c.triangle(cx + 36, cy + 8, cx + 52, cy + 19, cx + 36, cy + 30, color)
    c.fill_rect(cx - 28, cy - 14, 22, 22, color)
    c.triangle(cx - 8, cy - 14, cx + 8, cy - 14, cx, cy - 44, RED)
    c.circle(cx, cy - 14, 6, GOLD)
    for yy in (cy + 42, cy + 50):
        c.line(cx - 52, yy, cx + 52, yy, BLUE, 3)


def icon_ipo(c, cx, cy, color):
    # rising chart bars and arrow
    for i, h in enumerate((18, 30, 44, 58)):
        x = cx - 48 + i * 26
        c.fill_rect(x, cy + 30 - h, 18, h, color)
    c.line(cx - 52, cy + 34, cx + 52, cy + 34, INK, 3)
    c.line(cx - 48, cy + 8, cx - 12, cy - 12, RED, 4)
    c.line(cx - 12, cy - 12, cx + 24, cy - 28, RED, 4)
    c.line(cx + 24, cy - 28, cx + 52, cy - 40, RED, 4)
    c.triangle(cx + 52, cy - 40, cx + 34, cy - 40, cx + 52, cy - 22, RED)


def icon_drought(c, cx, cy, color):
    # harsh sun over cracked dry ground
    c.circle(cx, cy - 26, 16, GOLD)
    for dx, dy in ((-28, -26), (28, -26), (0, -52), (-20, -48), (20, -48)):
        c.line(cx, cy - 26, cx + dx, cy + dy, GOLD, 4)
    c.line(cx - 52, cy + 34, cx + 52, cy + 34, color, 4)
    c.line(cx - 30, cy + 34, cx - 18, cy + 14, color, 4)
    c.line(cx + 6, cy + 34, cx + 16, cy + 18, color, 4)
    c.line(cx + 30, cy + 34, cx + 40, cy + 20, color, 4)


ICONS = (icon_summit, icon_court, icon_bridge, icon_tanker, icon_ipo,
         icon_drought)

STORIES = [
    ("SHENZHEN, CHINA", "TRUMP, XI AND PUTIN MEET",
     "FIRST THREE-WAY SUMMIT ON APEC SIDELINES", NAVY),
    ("THE HAGUE", "WORLD COURT RULES TODAY",
     "MYANMAR ROHINGYA GENOCIDE CASE DECIDED", PURPLE),
    ("UKRAINE", "CRIMEA BRIDGE HIT AGAIN",
     "THIRD STRIKE ON THE BRIDGE IN A WEEK", RED),
    ("THE GULF", "IRAN HITS GULF TARGETS",
     "3 TANKERS STRUCK BY MINES NEAR HORMUZ", ORANGE),
    ("WALL STREET", "ANTHROPIC DEBUTS ON NASDAQ",
     "AI FIRM LISTS AS ANT AFTER $83 IPO", TEAL),
    ("PACIFIC", "TONGA DECLARES EMERGENCY",
     "27-DAY ALERT AS EL NINO DROUGHT BITES", GREEN),
]


# ---- page -----------------------------------------------------------------
def build():
    c = Canvas(W, H, PAPER)

    # header
    c.fill_rect(0, 0, W, 168, NAVY)
    c.draw_text_centered(22, "WORLD NEWS", 5, WHITE)
    c.draw_text_centered(96, "THURSDAY 19 NOVEMBER 2026", 4, GOLD)
    c.fill_rect(312, 152, 400, 4, GOLD)

    # story grid: 2 columns x 3 rows
    top = 188
    row_h = 252
    gap = 18
    col_w = 476
    for i, (kicker, headline, body, accent) in enumerate(STORIES):
        row, col = divmod(i, 2)
        x = 24 + col * (col_w + 24)
        y = top + row * (row_h + gap)
        c.fill_rect(x, y, col_w, row_h, WHITE)
        c.rect_border(x, y, col_w, row_h, BORDER, 2)
        c.fill_rect(x, y, col_w, 8, accent)
        # icon column
        c.fill_rect(x + 2, y + 10, 116, row_h - 12, TINT)
        ICONS[i](c, x + 60, y + 132, accent)
        # text column
        tx = x + 134
        tw = col_w - 134 - 16
        c.draw_text(tx, y + 26, kicker, 2, accent)
        c.fill_rect(tx, y + 48, 44, 4, accent)
        lines = wrap(headline, tw // 18)
        ly = y + 64
        for line in lines[:2]:
            c.draw_text(tx, ly, line, 3, INK)
            ly += 28
        blines = wrap(body, tw // 12)
        ly += 8
        for line in blines[:3]:
            c.draw_text(tx, ly, line, 2, MUTED)
            ly += 20

    # footer
    c.fill_rect(0, 980, W, 44, NAVY)
    c.draw_text_centered(995, "SIX STORIES - ONE DAY - AROUND THE WORLD", 2,
                         WHITE)
    return c


def write_png(canvas, path):
    raw = bytearray()
    for y in range(canvas.h):
        raw.append(0)
        start = y * canvas.w * 3
        raw.extend(canvas.px[start:start + canvas.w * 3])
    compressed = zlib.compress(bytes(raw), 9)

    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        out += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", canvas.w, canvas.h, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", compressed)
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    canvas = build()
    write_png(canvas, os.path.join(out_dir, "entry.png"))


if __name__ == "__main__":
    main()
