"""Рисует превью циферблата в docs/preview.png той же раскладкой, что и код на часах.

Запуск из корня репозитория:  python3 tools/preview.py
"""
from pathlib import Path

from PIL import Image, ImageDraw

from dotfont import BIG, SEC, SMALL

ROOT = Path(__file__).resolve().parent.parent
SCREEN = 260
BG, FG, UNDER = (255, 255, 255), (0, 0, 0), (85, 85, 85)

# те же константы, что в source/SuuntoLikeView.mc
SEC_GAP, DATE_GAP = 6, 26


def main(time_txt="1451", sec_txt="37", date_txt="Wed 28.10"):
    img = Image.new("RGB", (SCREEN, SCREEN), (120, 120, 120))
    d = ImageDraw.Draw(img)
    d.ellipse([0, 0, SCREEN - 1, SCREEN - 1], fill=BG)

    group_w = BIG.width_px(time_txt) + SEC_GAP + SEC.width_px(sec_txt)
    tx = (SCREEN - group_w) // 2
    block_h = SMALL.height_px() + DATE_GAP + BIG.height_px()
    dy = (SCREEN - block_h) // 2
    ty = dy + SMALL.height_px() + DATE_GAP

    sx = tx + BIG.width_px(time_txt) + SEC_GAP
    sy = ty + BIG.height_px() - SEC.height_px()

    # два слоя: тёмно-серая сплошная подложка, поверх чёрные точки
    for color, fill in ((UNDER, True), (FG, False)):
        SMALL.draw(d, date_txt, (SCREEN - SMALL.width_px(date_txt)) // 2, dy, color, fill)
        BIG.draw(d, time_txt, tx, ty, color, fill)
        SEC.draw(d, sec_txt, sx, sy, color, fill)

    out = ROOT / "docs" / "preview.png"
    out.parent.mkdir(exist_ok=True)
    img.resize((SCREEN * 2, SCREEN * 2), Image.NEAREST).save(out)
    print("Превью:", out.relative_to(ROOT))


if __name__ == "__main__":
    main()
