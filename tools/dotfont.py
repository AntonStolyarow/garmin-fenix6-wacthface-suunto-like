"""Точечные сегментные шрифты в стиле Suunto Core.

Каждый символ строится из сегментов (как 7-сегментный индикатор),
а каждый сегмент собран из квадратиков ("точек") на сетке.
"""

# Сегменты: a верх, b прав.верх, c прав.низ, d низ, e лев.низ, f лев.верх,
# g середина, k / l - центральная вертикаль сверху / снизу (для M, W, T).
# Модификатор после "|": w - широкий символ, n - узкий (в толщину сегмента).
GLYPHS = {
    "0": "abcdef", "1": "bc", "2": "abged", "3": "abgcd", "4": "fgbc",
    "5": "afgcd", "6": "afgedc", "7": "abc", "8": "abcdefg", "9": "abcdfg",
    "-": "g",
    # буквы для дней недели: Sun Mon Tue Wed Thu Fri Sat
    "S": "afgcd", "M": "afbekl|w", "T": "Akl", "W": "fedcl|w", "F": "afge",
    "u": "ecd", "n": "gec", "o": "gecd", "e": "abfged", "d": "bcdeg",
    "h": "fegc", "r": "ge", "i": "e|n", "a": "abgecd", "t": "fged",
}

# Иконки (рисуются в мелком шрифте как отдельные символы).
# Для каждой иконки - варианты под разную высоту шрифта (в квадратиках).
ICONS = {
    "@": {  # шаги
        9: [
            ".XX.....",
            "XXXX....",
            "XXXX.XX.",
            ".XX.XXXX",
            "....XXXX",
            ".XX.XXX.",
            ".XX.....",
            ".....XX.",
            ".....XX.",
        ],
        7: [
            ".XX.....",
            "XXXX....",
            "XXXX.XX.",
            ".XX.XXXX",
            "....XXXX",
            ".XX..XX.",
            ".....XX.",
        ],
    },
    "&": {  # сердце (пульс)
        9: [
            ".......",
            ".XX.XX.",
            "XXXXXXX",
            "XXXXXXX",
            "XXXXXXX",
            ".XXXXX.",
            "..XXX..",
            "...X...",
            ".......",
        ],
        7: [
            ".XX.XX.",
            "XXXXXXX",
            "XXXXXXX",
            "XXXXXXX",
            ".XXXXX.",
            "..XXX..",
            "...X...",
        ],
    },
}


class DotFont:
    """w, h, t - ширина/высота символа и толщина сегмента в квадратиках;
    cell, dot - шаг сетки и размер квадратика в px; gap - колонок между символами.
    """

    def __init__(self, name, w, h, t, cell, dot, gap, chars, icons=False):
        self.name = name
        self.w, self.h, self.t = w, h, t
        self.cell, self.dot, self.gap = cell, dot, gap
        self.chars = chars
        self.icons = icons

    def _segs(self, w):
        h, t = self.h, self.t
        mid = (h - t) // 2
        # Вертикали включают углы, горизонтали - без крайнего столбика. Так угол закрашен,
        # только если к перекладине примыкает вертикаль (иначе торчит "засечка").
        up, low = range(0, mid + t), range(mid, h)
        hor, full = range(1, w - 1), range(0, w)
        cc = (w - t) // 2
        return {
            "a": {(r, c) for r in range(t) for c in hor},
            "A": {(r, c) for r in range(t) for c in full},  # верх на всю ширину (для T)
            "g": {(r, c) for r in range(mid, mid + t) for c in hor},
            "d": {(r, c) for r in range(h - t, h) for c in hor},
            "f": {(r, c) for r in up for c in range(t)},
            "b": {(r, c) for r in up for c in range(w - t, w)},
            "e": {(r, c) for r in low for c in range(t)},
            "c": {(r, c) for r in low for c in range(w - t, w)},
            "k": {(r, c) for r in up for c in range(cc, cc + t)},
            "l": {(r, c) for r in low for c in range(cc, cc + t)},
        }

    def glyph(self, ch):
        """Возвращает (ширина в колонках, набор закрашенных клеток (row, col))."""
        t, h = self.t, self.h
        if ch == ":":
            off = h // 4
            rows = list(range(off, off + t)) + list(range(h - off - t, h - off))
            return t, {(r, c) for r in rows for c in range(t)}
        if ch == ".":
            return t, {(r, c) for r in range(h - t, h) for c in range(t)}
        if ch == " ":
            return self.w // 2, set()
        if ch in ICONS:
            assert h in ICONS[ch], f"нет варианта иконки {ch!r} высотой {h}"
            rows = ICONS[ch][h]
            cells = {(r, c) for r, row in enumerate(rows) for c, x in enumerate(row) if x == "X"}
            return len(rows[0]), cells
        spec, _, mod = GLYPHS[ch].partition("|")
        w = {"w": self.w + 3, "n": self.t}.get(mod, self.w)
        seg = self._segs(w)
        cells = set()
        for s in spec:
            cells |= seg[s]
        return w, cells

    def height_px(self):
        return self.h * self.cell

    def advance_px(self, ch):
        return (self.glyph(ch)[0] + self.gap) * self.cell

    def width_px(self, text):
        """Ширина строки без хвостового промежутка (как inkWidth в коде циферблата)."""
        return sum(self.advance_px(ch) for ch in text) - self.gap * self.cell

    def draw(self, draw, text, x0, y0, color):
        x = x0
        for ch in text:
            _, cells = self.glyph(ch)
            for r, c in cells:
                px, py = x + c * self.cell, y0 + r * self.cell
                draw.rectangle([px, py, px + self.dot - 1, py + self.dot - 1], fill=color)
            x += self.advance_px(ch)


DIGITS = "0123456789"
LETTERS = "".join(sorted(set("SunMonTueWedThuFriSat")))

# Шрифты циферблата (размеры подобраны под экран Fenix 6, 260x260)
BIG = DotFont("big_dots", w=8, h=21, t=3, cell=3, dot=2, gap=2, chars=DIGITS + ":")
SEC = DotFont("sec_dots", w=7, h=11, t=3, cell=3, dot=2, gap=2, chars=DIGITS)
SMALL = DotFont("small_dots", w=4, h=7, t=1, cell=3, dot=2, gap=2,
                chars=DIGITS + ".- " + LETTERS + "@&")

FONTS = [BIG, SEC, SMALL]
