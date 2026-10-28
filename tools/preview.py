"""Рисует превью циферблата в docs/preview.png той же раскладкой, что и код на часах.

Запуск из корня репозитория:  python3 tools/preview.py
"""
import math
from pathlib import Path

from PIL import Image, ImageDraw

from dotfont import BIG, SEC, SMALL

ROOT = Path(__file__).resolve().parent.parent
SCREEN = 260
BG, FG = (255, 255, 255), (0, 0, 0)

# те же константы, что в source/SuuntoLikeView.mc
SEC_GAP, DATE_GAP, ROW_GAP = 6, 9, 9


def draw_ticks(d):
    c = SCREEN / 2
    for i in range(12):
        if i == 0:  # North: две точки
            for da in (-4, 4):
                b = math.radians(-90 + da)
                x, y = c + 121 * math.cos(b), c + 121 * math.sin(b)
                d.ellipse([x - 3, y - 3, x + 3, y + 3], fill=FG)
            continue
        a = math.radians(i * 30 - 90)
        d.line([(c + 116 * math.cos(a), c + 116 * math.sin(a)),
                (c + 126 * math.cos(a), c + 126 * math.sin(a))], fill=FG, width=3)


def main(time_txt="14:51", sec_txt="37", date_txt="Wed 28.10", steps="8432", hr="72"):
    img = Image.new("RGB", (SCREEN, SCREEN), (60, 60, 60))
    d = ImageDraw.Draw(img)
    d.ellipse([0, 0, SCREEN - 1, SCREEN - 1], fill=BG)
    draw_ticks(d)

    group_w = BIG.width_px(time_txt) + SEC_GAP + SEC.width_px(sec_txt)
    tx = (SCREEN - group_w) // 2
    ty = SCREEN // 2 - BIG.height_px() // 2
    BIG.draw(d, time_txt, tx, ty, FG)

    sx = tx + BIG.width_px(time_txt) + SEC_GAP
    sy = ty + BIG.height_px() - SEC.height_px()
    SEC.draw(d, sec_txt, sx, sy, FG)

    dy = ty - DATE_GAP - SMALL.height_px()
    SMALL.draw(d, date_txt, (SCREEN - SMALL.width_px(date_txt)) // 2, dy, FG)

    y1 = ty + BIG.height_px() + ROW_GAP
    s = "@" + steps
    SMALL.draw(d, s, (SCREEN - SMALL.width_px(s)) // 2, y1, FG)
    y2 = y1 + SMALL.height_px() + ROW_GAP
    s = "&" + hr
    SMALL.draw(d, s, (SCREEN - SMALL.width_px(s)) // 2, y2, FG)

    out = ROOT / "docs" / "preview.png"
    out.parent.mkdir(exist_ok=True)
    img.resize((SCREEN * 2, SCREEN * 2), Image.NEAREST).save(out)
    print("Превью:", out.relative_to(ROOT))


if __name__ == "__main__":
    main()
