"""Рисует превью циферблата в docs/preview.png той же раскладкой, что и код на часах.

Запуск из корня репозитория:  python3 tools/preview.py
"""
from pathlib import Path

from PIL import Image, ImageDraw

from dotfont import BIG, SEC, SMALL

ROOT = Path(__file__).resolve().parent.parent
SCREEN = 260
BG, FG = (0, 0, 0), (255, 255, 255)

# те же константы, что в source/SuuntoLikeView.mc
SEC_GAP, DATE_GAP, ROW_GAP, METRIC_GAP = 6, 26, 26, 15


def main(time_txt="1451", sec_txt="37", date_txt="Wed 28.10", steps="8432", hr="72"):
    img = Image.new("RGB", (SCREEN, SCREEN), (120, 120, 120))
    d = ImageDraw.Draw(img)
    d.ellipse([0, 0, SCREEN - 1, SCREEN - 1], fill=BG)

    group_w = BIG.width_px(time_txt) + SEC_GAP + SEC.width_px(sec_txt)
    tx = (SCREEN - group_w) // 2
    ty = SCREEN // 2 - BIG.height_px() // 2
    BIG.draw(d, time_txt, tx, ty, FG)

    sx = tx + BIG.width_px(time_txt) + SEC_GAP
    sy = ty + BIG.height_px() - SEC.height_px()
    SEC.draw(d, sec_txt, sx, sy, FG)

    dy = ty - DATE_GAP - SMALL.height_px()
    SMALL.draw(d, date_txt, (SCREEN - SMALL.width_px(date_txt)) // 2, dy, FG)

    ry = ty + BIG.height_px() + ROW_GAP
    s1, s2 = "@" + steps, "&" + hr
    row_w = SMALL.width_px(s1) + METRIC_GAP + SMALL.width_px(s2)
    rx = (SCREEN - row_w) // 2
    SMALL.draw(d, s1, rx, ry, FG)
    SMALL.draw(d, s2, rx + SMALL.width_px(s1) + METRIC_GAP, ry, FG)

    out = ROOT / "docs" / "preview.png"
    out.parent.mkdir(exist_ok=True)
    img.resize((SCREEN * 2, SCREEN * 2), Image.NEAREST).save(out)
    print("Превью:", out.relative_to(ROOT))


if __name__ == "__main__":
    main()
