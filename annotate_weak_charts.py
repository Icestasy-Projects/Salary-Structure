"""Add clean pattern annotations (circles, labels, necklines) to 3 weak Sharvari charts."""

import os
import math
from PIL import Image, ImageDraw, ImageFont

BASE = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(BASE, "extracted_images")

FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def draw_circle(draw, cx, cy, radius, color, width=4):
    draw.ellipse(
        [cx - radius, cy - radius, cx + radius, cy + radius],
        outline=color, width=width
    )


def draw_dashed_line(draw, x1, y1, x2, y2, color, width=3, dash_len=18, gap_len=10):
    dx = x2 - x1
    dy = y2 - y1
    length = math.sqrt(dx * dx + dy * dy)
    if length == 0:
        return
    ux, uy = dx / length, dy / length
    pos = 0
    while pos < length:
        seg_end = min(pos + dash_len, length)
        sx = x1 + ux * pos
        sy = y1 + uy * pos
        ex = x1 + ux * seg_end
        ey = y1 + uy * seg_end
        draw.line([(sx, sy), (ex, ey)], fill=color, width=width)
        pos += dash_len + gap_len


def annotate_dcb_double_top():
    """DCB Bank Double Top (1490x987). Two peaks near 195-200."""
    path = os.path.join(IMG_DIR, "vidhi", "img-001.png")
    img = Image.open(path)
    draw = ImageDraw.Draw(img)

    font_label = ImageFont.truetype(FONT_PATH, 22)
    font_neckline = ImageFont.truetype(FONT_PATH, 19)

    red = (220, 40, 40)
    blue = (30, 80, 200)

    # Peak 1: candle reaching ~200 around Nov/Dec (shifted down to be ON the candle)
    draw_circle(draw, 555, 180, 38, red, width=4)
    draw.text((520, 130), "Top 1", fill=red, font=font_label)

    # Peak 2: candle cluster reaching ~197 around Dec/Jan
    draw_circle(draw, 690, 178, 38, red, width=4)
    draw.text((655, 128), "Top 2", fill=red, font=font_label)

    # Neckline at ~182 level
    neckline_y = 295
    draw_dashed_line(draw, 65, neckline_y, 1250, neckline_y, blue, width=2)
    draw.text((1080, neckline_y - 24), "Neckline", fill=blue, font=font_neckline)

    out_path = os.path.join(IMG_DIR, "vidhi", "img-001-annotated.png")
    img.save(out_path, quality=95)
    print(f"Saved: {out_path}")


def annotate_hindustan_zinc_triple_top():
    """Hindustan Zinc Triple Top (1882x1138). Three peaks near 467-470 resistance."""
    path = os.path.join(IMG_DIR, "apurva", "img-002.png")
    img = Image.open(path)
    draw = ImageDraw.Draw(img)

    font_label = ImageFont.truetype(FONT_PATH, 22)
    font_line = ImageFont.truetype(FONT_PATH, 20)

    red = (220, 40, 40)
    dark_blue = (20, 60, 180)

    # Peak 1: around mid-Feb, candle reaching ~467 (well away from buttons)
    draw_circle(draw, 340, 160, 35, red, width=4)
    draw.text((305, 108), "Top 1", fill=red, font=font_label)

    # Peak 2: around mid-March, spike near 468
    draw_circle(draw, 590, 160, 35, red, width=4)
    draw.text((555, 108), "Top 2", fill=red, font=font_label)

    # Peak 3: around April area, peak near 468-470
    draw_circle(draw, 770, 158, 35, red, width=4)
    draw.text((735, 106), "Top 3", fill=red, font=font_label)

    # Label existing lines
    draw.text((1200, 105), "Resistance (470)", fill=dark_blue, font=font_line)
    draw.text((1200, 425), "Support (422)", fill=dark_blue, font=font_line)

    out_path = os.path.join(IMG_DIR, "apurva", "img-002-annotated.png")
    img.save(out_path, quality=95)
    print(f"Saved: {out_path}")


def annotate_mahindra_triple_bottom():
    """Mahindra Logistics Triple Bottom (1882x1154). Three lows near 402 support."""
    path = os.path.join(IMG_DIR, "apurva", "img-003.png")
    img = Image.open(path)
    draw = ImageDraw.Draw(img)

    font_label = ImageFont.truetype(FONT_PATH, 22)
    font_line = ImageFont.truetype(FONT_PATH, 20)

    green = (30, 150, 50)
    dark_blue = (20, 60, 180)

    # Bottom 1: Jul 3, candle dipping to ~400-402
    draw_circle(draw, 210, 430, 38, green, width=4)
    draw.text((160, 472), "Bottom 1", fill=green, font=font_label)

    # Bottom 2: Jul 9-11, candle touching ~402
    draw_circle(draw, 485, 428, 38, green, width=4)
    draw.text((435, 470), "Bottom 2", fill=green, font=font_label)

    # Bottom 3: Jul 15-17, candle near 402
    draw_circle(draw, 700, 422, 38, green, width=4)
    draw.text((650, 464), "Bottom 3", fill=green, font=font_label)

    # Label existing support line
    draw.text((1280, 380), "Support (402)", fill=dark_blue, font=font_line)

    # Neckline: resistance connecting reaction highs ~408-410
    neckline_y = 340
    draw_dashed_line(draw, 65, neckline_y, 1350, neckline_y, dark_blue, width=2)
    draw.text((1130, neckline_y - 24), "Neckline", fill=dark_blue, font=font_line)

    out_path = os.path.join(IMG_DIR, "apurva", "img-003-annotated.png")
    img.save(out_path, quality=95)
    print(f"Saved: {out_path}")


if __name__ == "__main__":
    print("Annotating 3 weak Sharvari charts...")
    annotate_dcb_double_top()
    annotate_hindustan_zinc_triple_top()
    annotate_mahindra_triple_bottom()
    print("Done!")
