"""Build script for the news-image-01 entry.

Composes the three generated panel illustrations plus PIL vector text
(banner, per-panel captions, bottom ticker) into one 1024x1024 image at
assets/entry.png. Run locally: python3 compose.py

All text is drawn with PIL (DejaVu) so it is guaranteed legible -- no
AI-rendered text anywhere. The entry program (main.py) only copies the
composed file; this script is the reproducible record of how it was made.
"""
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "assets")

W, H = 1024, 1024
BANNER_H = 64
COLS_H = 820          # image + caption per column
TICKER_H = H - BANNER_H - COLS_H   # 140
IMG_H = 700
CAP_H = COLS_H - IMG_H             # 120
COL_W = [341, 342, 341]            # sums to 1024

NAVY = (16, 28, 44)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GOLD = (246, 201, 69)

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

PANELS = [
    ("panel-nvidia.png", (76, 185, 0), ("NVIDIA CEO RESIGNS", "SHARES -16%")),
    ("panel-ukraine.png", GOLD, ("UKRAINE TALKS OPEN", "TO EUROPE")),
    ("panel-gulf.png", (214, 69, 69), ("GULF ON EDGE", "TANKER MINED")),
]

TICKER = [
    "ALSO: MICROSOFT OUTAGE HITS OUTLOOK & TEAMS WORLDWIDE  \u2022  "
    "ISRAELI STRIKE ON GAZA HOSPITAL KILLS 6",
    "IEA FORECASTS Q4 OIL SURPLUS  \u2022  CHINA'S UNANNOUNCED PACIFIC "
    "DRILLS  \u2022  GOOGLE UNVEILS GEMINI 4",
]


def font(path, size):
    return ImageFont.truetype(path, size)


def fit_font(draw, text, path, start, max_w):
    size = start
    while size > 10:
        f = font(path, size)
        if draw.textlength(text, font=f) <= max_w:
            return f
        size -= 1
    return font(path, 10)


def crop_to(im, tw, th):
    """Center-crop to the target aspect, then resize with LANCZOS."""
    sw, sh = im.size
    target = tw / th
    if sw / sh > target:  # too wide: crop width
        nw = int(sh * target)
        x0 = (sw - nw) // 2
        im = im.crop((x0, 0, x0 + nw, sh))
    else:  # too tall: crop height
        nh = int(sw / target)
        y0 = (sh - nh) // 2
        im = im.crop((0, y0, sw, y0 + nh))
    return im.resize((tw, th), Image.LANCZOS)


def wrap(draw, text, path, start, max_w, max_lines):
    """Word-wrap to at most max_lines, shrinking the font if needed."""
    size = start
    while size > 12:
        f = font(path, size)
        words, lines, cur = text.split(), [], ""
        for w in words:
            trial = (cur + " " + w).strip()
            if draw.textlength(trial, font=f) <= max_w:
                cur = trial
            else:
                lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
        if len(lines) <= max_lines:
            return f, lines
        size -= 1
    return font(path, 12), lines


def main():
    canvas = Image.new("RGB", (W, H), NAVY)
    draw = ImageDraw.Draw(canvas)

    # --- Banner ---
    draw.rectangle([0, 0, W, BANNER_H], fill=NAVY)
    bf = fit_font(draw, "FRIDAY 13 NOVEMBER 2026", FONT_BOLD, 40, W - 40)
    tw = draw.textlength("FRIDAY 13 NOVEMBER 2026", font=bf)
    draw.text(((W - tw) / 2, (BANNER_H - bf.size) / 2 - 2),
              "FRIDAY 13 NOVEMBER 2026", font=bf, fill=WHITE)
    draw.rectangle([0, BANNER_H - 4, W, BANNER_H], fill=GOLD)

    # --- Three columns ---
    x = 0
    for fname, accent, (line1, line2) in PANELS:
        w = COL_W[PANELS.index((fname, accent, (line1, line2)))]
        im = Image.open(os.path.join(ASSETS, fname)).convert("RGB")
        canvas.paste(crop_to(im, w, IMG_H), (x, BANNER_H))
        cy = BANNER_H + IMG_H
        draw.rectangle([x, cy, x + w, cy + CAP_H], fill=NAVY)
        draw.rectangle([x, cy, x + w, cy + 6], fill=accent)
        f1 = fit_font(draw, line1, FONT_BOLD, 30, w - 16)
        f2 = fit_font(draw, line2, FONT_BOLD, 30, w - 16)
        t1 = draw.textlength(line1, font=f1)
        t2 = draw.textlength(line2, font=f2)
        draw.text((x + (w - t1) / 2, cy + 16), line1, font=f1, fill=WHITE)
        draw.text((x + (w - t2) / 2, cy + 62), line2, font=f2, fill=WHITE)
        x += w

    # White dividers between columns
    for dx in (341, 683):
        draw.rectangle([dx - 1, BANNER_H, dx + 1, BANNER_H + COLS_H],
                       fill=WHITE)

    # --- Ticker ---
    ty = BANNER_H + COLS_H
    draw.rectangle([0, ty, W, H], fill=BLACK)
    draw.rectangle([0, ty, W, ty + 3], fill=(214, 69, 69))
    y = ty + 14
    for text in TICKER:
        f, lines = wrap(draw, text, FONT_REG, 24, W - 32, 2)
        for ln in lines:
            lw = draw.textlength(ln, font=f)
            draw.text(((W - lw) / 2, y), ln, font=f, fill=WHITE)
            y += f.size + 8

    out = os.path.join(ASSETS, "entry.png")
    canvas.save(out, "PNG", optimize=True)
    size = os.path.getsize(out)
    print("PNG bytes:", size)
    if size > 1048576:
        canvas.save(out, "JPEG", quality=90, optimize=True)
        print("PNG too big; saved JPEG bytes:", os.path.getsize(out))
    print("wrote", out, canvas.size)


if __name__ == "__main__":
    main()
