"""Генерирует битмап-шрифты (.fnt + .png, формат BMFont) и иконку приложения.

Запуск из корня репозитория:  python3 tools/gen_fonts.py
Нужен Pillow:                 pip install pillow
"""
from pathlib import Path

from PIL import Image, ImageDraw

from dotfont import FONTS, DotFont

ROOT = Path(__file__).resolve().parent.parent
FONT_DIR = ROOT / "resources" / "fonts"
DRAW_DIR = ROOT / "resources" / "drawables"
PAD = 2  # отступ между глифами в атласе

WHITE = (255, 255, 255, 255)


def build_font(font: DotFont):
    glyphs = []
    for ch in font.chars:
        cols, _ = font.glyph(ch)
        glyphs.append((ch, max(cols * font.cell, 1)))

    atlas_w = sum(w + PAD for _, w in glyphs) + PAD
    atlas_h = font.height_px() + 2 * PAD
    img = Image.new("RGBA", (atlas_w, atlas_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    lines = []
    x = PAD
    for ch, w in glyphs:
        font.draw(draw, ch, x, PAD, WHITE)
        lines.append(
            f"char id={ord(ch)} x={x} y={PAD} width={w} height={font.height_px()} "
            f"xoffset=0 yoffset=0 xadvance={font.advance_px(ch)} page=0 chnl=15"
        )
        x += w + PAD

    png_name = f"{font.name}.png"
    img.save(FONT_DIR / png_name)

    h = font.height_px()
    fnt = [
        f'info face="{font.name}" size={h} bold=0 italic=0 charset="" unicode=1 '
        f"stretchH=100 smooth=0 aa=1 padding=0,0,0,0 spacing=0,0",
        f"common lineHeight={h} base={h} scaleW={atlas_w} scaleH={atlas_h} pages=1 packed=0",
        f'page id=0 file="{png_name}"',
        f"chars count={len(lines)}",
        *lines,
    ]
    (FONT_DIR / f"{font.name}.fnt").write_text("\n".join(fnt) + "\n")


def build_fonts_xml():
    ids = {"big_dots": "BigDots", "sec_dots": "SecDots", "small_dots": "SmallDots"}
    rows = [
        f'    <font id="{ids[f.name]}" filename="{f.name}.fnt" antialias="false" />'
        for f in FONTS
    ]
    (FONT_DIR / "fonts.xml").write_text("<fonts>\n" + "\n".join(rows) + "\n</fonts>\n")


def build_launcher_icon(size=40):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse([0, 0, size - 1, size - 1], fill=(255, 255, 255, 255), outline=(0, 0, 0, 255))
    icon_font = DotFont("icon", w=4, h=9, t=1, cell=2, dot=2, gap=1, chars="")
    text = "14"
    x = (size - icon_font.width_px(text)) // 2
    y = (size - icon_font.height_px()) // 2
    icon_font.draw(d, text, x, y, (0, 0, 0, 255))
    img.save(DRAW_DIR / "launcher_icon.png")


if __name__ == "__main__":
    FONT_DIR.mkdir(parents=True, exist_ok=True)
    DRAW_DIR.mkdir(parents=True, exist_ok=True)
    for f in FONTS:
        build_font(f)
    build_fonts_xml()
    build_launcher_icon()
    print("Шрифты и иконка сгенерированы в", FONT_DIR.relative_to(ROOT), "и", DRAW_DIR.relative_to(ROOT))
