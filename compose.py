"""Build script for the news-image-01 entry (Stage 5: front-page rebuild).

Composes the three generated panel illustrations plus PIL vector text
into one 1024x1024 front page at assets/entry.png. Run locally:
python3 compose.py

Layout (1024x1024):
  banner 50px   "FRIDAY 13 NOVEMBER 2026" + gold rule
  lead   74px   FAA grounding (the day's #1 story) on a deep-red strip
  hero  386px   the 3 generated panels (330px image + 56px caption)
  grid  514px   14 more verified stories, 2 cols x 7 rows, numbered,
                region tag + bold headline (no tiny text anywhere)
Total: 18 stories. All text is PIL (DejaVu) vector text -- no
AI-rendered text anywhere. Every headline stays legible at a 300px
downscale (tested). The entry program (main.py) only copies the
composed file; this script is the reproducible record of how it was made.

Every story printed was verified against live reporting (Reuters and
others) in Stage 5; numbers used are the conservative published
figures. No unverified items.
"""
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "assets")

W, H = 1024, 1024
BANNER_H = 50
LEAD_H = 74
HERO_IMG_H = 330
CAP_H = 56
GRID_H = H - BANNER_H - LEAD_H - HERO_IMG_H - CAP_H  # 514
GRID_ROWS = 7
ROW_H = GRID_H // GRID_ROWS  # 73

NAVY = (16, 28, 44)
PAPER = (245, 241, 232)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GOLD = (246, 201, 69)
RED = (139, 30, 30)
INK = (24, 24, 24)
HAIRLINE = (200, 192, 176)

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

# (file, crop y0 in source, accent, caption line1, caption line2)
PANELS = [
    ("panel-nvidia.png", 560, (76, 185, 0),
     ("NVIDIA CEO RESIGNS", "SHARES -16%")),
    ("panel-ukraine.png", 1124, GOLD,
     ("UKRAINE TALKS OPEN", "TO EUROPE")),
    ("panel-gulf.png", 800, (214, 69, 69),
     ("GULF ON EDGE", "TANKER MINED")),
]
COL_W = [341, 342, 341]  # sums to 1024

LEAD_HEAD = "ALL US FLIGHTS GROUNDED"
LEAD_SUB = ("FAA HALTS EVERY DEPARTURE  \u2022  4,700+ CANCELLED  "
            "\u2022  FIRST NATIONWIDE HALT SINCE 9/11")

TAG_COLORS = {
    "WORLD": (120, 90, 0), "USA": (30, 80, 160),
    "MIDDLE EAST": (160, 40, 40), "ASIA": (0, 120, 90),
    "EUROPE": (90, 60, 140), "SPACE": (40, 40, 40),
    "MARKETS": (0, 100, 60), "ECONOMY": (100, 60, 0),
    "SPORT": (0, 110, 50), "TECH": (40, 80, 160),
}

# (tag, headline) -- all verified in Stage 5
GRID = [
    ("WORLD", "TRUMP, XI AND PUTIN TO MEET IN CHINA"),
    ("SPACE", "STARSHIP FLIGHT 15 REACHES ORBIT"),
    ("WORLD", "POPE'S MASS DRAWS 500,000 IN PERU"),
    ("MIDDLE EAST", "TURKEY AND QATAR SIGN DEFENCE PACT"),
    ("ASIA", "BUS CRASH IN INDIA KILLS 26"),
    ("USA", "TANKER CAPSIZES RIVER BOAT IN NEW ORLEANS"),
    ("MARKETS", "YEN SLIDES PAST 160 TO THE DOLLAR"),
    ("ECONOMY", "US PRODUCER PRICES UP 6.5%"),
    ("SPORT", "POCHETTINO TO MANAGE MAN UTD"),
    ("USA", "BOEBERT LOSES COLORADO HOUSE SEAT"),
    ("ASIA", "NORTH KOREA RESHAPES ITS FLAG"),
    ("EUROPE", "DRONE DEBRIS SETS KYIV HOSPITAL ABLAZE"),
    ("MIDDLE EAST", "ISRAELI STRIKE ON GAZA HOSPITAL KILLS 6"),
    ("TECH", "MICROSOFT OUTAGE HITS OUTLOOK & TEAMS"),
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


def crop_to(im, tw, th, y0=None):
    """Crop to the target aspect (with optional source y0 for tall
    images), then resize with LANCZOS."""
    sw, sh = im.size
    target = tw / th
    if sw / sh > target:  # too wide: crop width
        nw = int(sh * target)
        x0 = (sw - nw) // 2
        im = im.crop((x0, 0, x0 + nw, sh))
    else:  # too tall: crop height
        nh = int(sw / target)
        if y0 is None:
            y0 = (sh - nh) // 2
        y0 = max(0, min(y0, sh - nh))
        im = im.crop((0, y0, sw, y0 + nh))
    return im.resize((tw, th), Image.LANCZOS)


def wrap2(draw, text, path, start, max_w):
    """Wrap to at most 2 lines, shrinking the font if needed."""
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
        if len(lines) <= 2:
            return f, lines
        size -= 1
    return font(path, 12), lines


def main():
    canvas = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(canvas)

    # --- Banner ---
    draw.rectangle([0, 0, W, BANNER_H], fill=NAVY)
    bf = fit_font(draw, "FRIDAY 13 NOVEMBER 2026", FONT_BOLD, 34, W - 40)
    tw = draw.textlength("FRIDAY 13 NOVEMBER 2026", font=bf)
    draw.text(((W - tw) / 2, (BANNER_H - bf.size) / 2 - 2),
              "FRIDAY 13 NOVEMBER 2026", font=bf, fill=WHITE)
    draw.rectangle([0, BANNER_H - 4, W, BANNER_H], fill=GOLD)

    # --- Lead strip: FAA grounding ---
    ly = BANNER_H
    draw.rectangle([0, ly, W, ly + LEAD_H], fill=RED)
    lf = fit_font(draw, LEAD_HEAD, FONT_BOLD, 32, W - 40)
    lw = draw.textlength(LEAD_HEAD, font=lf)
    draw.text(((W - lw) / 2, ly + 6), LEAD_HEAD, font=lf, fill=WHITE)
    sf = fit_font(draw, LEAD_SUB, FONT_REG, 18, W - 40)
    sw = draw.textlength(LEAD_SUB, font=sf)
    draw.text(((W - sw) / 2, ly + 42), LEAD_SUB, font=sf, fill=GOLD)

    # --- Hero row: 3 panels ---
    hy = BANNER_H + LEAD_H
    x = 0
    for (fname, y0, accent, (line1, line2)), w in zip(PANELS, COL_W):
        im = Image.open(os.path.join(ASSETS, fname)).convert("RGB")
        canvas.paste(crop_to(im, w, HERO_IMG_H, y0), (x, hy))
        cy = hy + HERO_IMG_H
        draw.rectangle([x, cy, x + w, cy + CAP_H], fill=NAVY)
        draw.rectangle([x, cy, x + w, cy + 5], fill=accent)
        f1 = fit_font(draw, line1, FONT_BOLD, 24, w - 16)
        f2 = fit_font(draw, line2, FONT_BOLD, 24, w - 16)
        t1 = draw.textlength(line1, font=f1)
        t2 = draw.textlength(line2, font=f2)
        draw.text((x + (w - t1) / 2, cy + 10), line1, font=f1, fill=WHITE)
        draw.text((x + (w - t2) / 2, cy + 33), line2, font=f2, fill=WHITE)
        x += w
    for dx in (341, 683):
        draw.rectangle([dx - 1, hy, dx + 1, hy + HERO_IMG_H + CAP_H],
                       fill=WHITE)

    # --- Grid: 14 stories, 2 cols x 7 rows ---
    gy = BANNER_H + LEAD_H + HERO_IMG_H + CAP_H
    draw.rectangle([0, gy, W, gy + 3], fill=RED)
    cell_w = W // 2
    for i, (tag, head) in enumerate(GRID):
        col, row = i % 2, i // 2
        cx = col * cell_w
        cy = gy + 3 + row * ROW_H
        # number + tag
        num = "%02d" % (i + 1)
        tf = font(FONT_BOLD, 13)
        draw.text((cx + 14, cy + 7), num, font=tf, fill=RED)
        tag_x = cx + 14 + draw.textlength(num + "  ", font=tf)
        draw.text((tag_x, cy + 7), tag, font=tf,
                  fill=TAG_COLORS.get(tag, INK))
        # headline, up to 2 lines; 21px keeps 2 lines inside the 73px
        # row (24 + 21 + 2 + 21 = 68) -- Stage 5 fix: 23px overflowed
        # the last row off the bottom of the page.
        hf, lines = wrap2(draw, head, FONT_BOLD, 21, cell_w - 28)
        hyy = cy + 24
        for ln in lines:
            draw.text((cx + 14, hyy), ln, font=hf, fill=INK)
            hyy += hf.size + 2
        # hairlines
        if row < GRID_ROWS - 1:
            draw.rectangle([cx + 14, cy + ROW_H - 1, cx + cell_w - 14,
                            cy + ROW_H], fill=HAIRLINE)
    draw.rectangle([W // 2 - 1, gy + 3, W // 2 + 1, H], fill=HAIRLINE)

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
