#!/usr/bin/env python3
"""Draw a one-page newspaper poster for Friday 20 November 2026.

Everything is drawn from scratch with Pillow primitives: no photographs,
no downloaded artwork. Running this file writes entry.png next to it.
The output is deterministic (no randomness, no clock, no network).
"""

import math
import os

from PIL import Image, ImageDraw, ImageFont

CANVAS = 1024
PAPER = (246, 241, 227)
INK = (26, 24, 21)
SOFT_INK = (74, 68, 58)
RULE = (26, 24, 21)
ACCENT_RED = (178, 34, 34)
ACCENT_BLUE = (31, 78, 121)
ACCENT_GOLD = (184, 134, 11)
SEA = (46, 110, 138)
SEA_LIGHT = (110, 168, 188)
LAND = (222, 198, 142)
LAND_DARK = (196, 166, 102)
BAND_BG = (26, 24, 21)
BAND_FG = (246, 241, 227)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
SERIF_BOLD = os.path.join(FONT_DIR, "DejaVuSerif-Bold.ttf")
SERIF = os.path.join(FONT_DIR, "DejaVuSerif.ttf")
SANS = os.path.join(FONT_DIR, "DejaVuSans.ttf")
SANS_BOLD = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")


def load_font(path, size):
    return ImageFont.truetype(path, size)


def text_width(draw, text, font):
    box = draw.textbbox((0, 0), text, font=font)
    return box[2] - box[0]


def wrap_lines(draw, text, font, max_width):
    """Greedy word wrap returning a list of lines that fit max_width."""
    words = text.split()
    lines = []
    current = ""
    for word in words:
        trial = word if not current else current + " " + word
        if text_width(draw, trial, font) <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_wrapped(draw, text, font, x, y, max_width, line_gap, fill):
    """Draw wrapped text starting at (x, y); return the y just below it.

    Line height comes from the font's own ascent+descent metrics rather
    than a per-string bounding box, so descenders (g, y, p) never collide
    with the line below.
    """
    ascent, descent = font.getmetrics()
    line_height = ascent + descent + line_gap
    cursor = y
    for line in wrap_lines(draw, text, font, max_width):
        draw.text((x, cursor), line, font=font, fill=fill)
        cursor += line_height
    return cursor


def centred(draw, text, font, cx, y, fill):
    w = text_width(draw, text, font)
    draw.text((cx - w / 2, y), text, font=font, fill=fill)


# --------------------------------------------------------------------------
# Lead illustration: a cyclone spiral bearing down on a coastline.
# --------------------------------------------------------------------------

def paint_cyclone_scene(draw, box):
    x0, y0, x1, y1 = box
    w = x1 - x0
    h = y1 - y0

    # Sea fills the panel; the landmass hugs the right-hand edge.
    draw.rectangle(box, fill=SEA)
    coast = [
        (x0 + int(w * 0.62), y0),
        (x1, y0),
        (x1, y1),
        (x0 + int(w * 0.78), y1),
        (x0 + int(w * 0.70), y0 + int(h * 0.62)),
        (x0 + int(w * 0.80), y0 + int(h * 0.38)),
        (x0 + int(w * 0.66), y0 + int(h * 0.18)),
    ]
    draw.polygon(coast, fill=LAND)
    draw.line(coast + [coast[0]], fill=LAND_DARK, width=2)

    # Whitecaps: short pale strokes scattered on the water.
    for i in range(14):
        wx = x0 + 14 + (i * 37) % int(w * 0.52)
        wy = y0 + 12 + (i * 53) % (h - 24)
        draw.arc([wx, wy, wx + 22, wy + 9], start=200, end=340, fill=SEA_LIGHT, width=2)

    # The storm itself: concentric broken arcs around a calm eye.
    cx = x0 + int(w * 0.36)
    cy = y0 + int(h * 0.46)
    for radius, start, sweep, colour, width in (
        (86, 20, 300, (255, 255, 255), 9),
        (68, 160, 280, (226, 238, 244), 8),
        (50, 300, 290, (255, 255, 255), 7),
        (34, 80, 270, (205, 226, 238), 6),
        (20, 210, 250, (255, 255, 255), 5),
    ):
        draw.arc(
            [cx - radius, cy - radius, cx + radius, cy + radius],
            start=start,
            end=start + sweep,
            fill=colour,
            width=width,
        )
    draw.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=(240, 248, 252), outline=SEA, width=2)

    # Rain streaks slanting in from the storm toward the shore.
    for i in range(18):
        rx = cx + 30 + (i * 23) % int(w * 0.34)
        ry = cy - 70 + (i * 31) % 150
        draw.line([rx, ry, rx - 7, ry + 14], fill=(190, 220, 235), width=2)

    # Two coastal towns as simple rooftops on the land.
    for tx, ty in ((x0 + int(w * 0.84), y0 + int(h * 0.30)), (x0 + int(w * 0.88), y0 + int(h * 0.66))):
        draw.rectangle([tx, ty, tx + 20, ty + 13], fill=(120, 84, 52))
        draw.polygon([(tx - 3, ty), (tx + 10, ty - 9), (tx + 23, ty)], fill=(94, 58, 36))

    # Red-alert tag pinned to the top-left corner of the panel.
    tag_font = load_font(SANS_BOLD, 12)
    label = "RED ALERT"
    tw = text_width(draw, label, tag_font)
    draw.rectangle([x0 + 8, y0 + 8, x0 + 16 + tw, y0 + 28], fill=ACCENT_RED)
    draw.text((x0 + 12, y0 + 11), label, font=tag_font, fill=(255, 255, 255))

    draw.rectangle(box, outline=INK, width=2)


# --------------------------------------------------------------------------
# Small flat spot illustrations for the six grid stories.
# Each takes a bounding box roughly 296 x 74.
# --------------------------------------------------------------------------

def spot_palms(draw, box):
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=(245, 166, 90))
    draw.ellipse([x0 + 108, y0 + 8, x0 + 156, y0 + 56], fill=(250, 214, 110))
    draw.rectangle([x0, y1 - 12, x1, y1], fill=(58, 110, 74))
    for px in (x0 + 44, x0 + 238):
        draw.line([px, y1 - 10, px + 8, y0 + 22], fill=(70, 50, 30), width=4)
        for dx, dy in ((-18, -6), (-8, -12), (4, -13), (15, -8), (20, 0)):
            draw.line([px + 8, y0 + 22, px + 8 + dx, y0 + 22 + dy], fill=(46, 96, 58), width=3)
    big = load_font(SERIF_BOLD, 34)
    draw.text((x0 + 126, y0 + 34), "VI", font=big, fill=(26, 24, 21))
    draw.rectangle(box, outline=INK, width=1)


def spot_summit(draw, box):
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=(214, 226, 238))
    # Skyline blocks behind the table.
    for i, bh in enumerate((34, 48, 28, 42, 32, 46)):
        bx = x0 + 8 + i * 48
        draw.rectangle([bx, y1 - 16 - bh, bx + 34, y1 - 16], fill=(140, 160, 184))
    # Conference table with three seats.
    draw.rectangle([x0 + 58, y1 - 22, x1 - 58, y1 - 10], fill=(92, 64, 40))
    for cx, colour in ((x0 + 92, (178, 34, 34)), (x0 + 148, (31, 78, 121)), (x0 + 204, (60, 60, 60))):
        draw.ellipse([cx - 11, y1 - 46, cx + 11, y1 - 24], fill=colour)
        draw.rectangle([cx - 13, y1 - 26, cx + 13, y1 - 20], fill=colour)
    draw.rectangle(box, outline=INK, width=1)


def spot_voyager(draw, box):
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=(16, 22, 44))
    for i in range(16):
        sx = x0 + 8 + (i * 53) % (x1 - x0 - 16)
        sy = y0 + 6 + (i * 29) % (y1 - y0 - 12)
        draw.ellipse([sx, sy, sx + 3, sy + 3], fill=(255, 255, 255))
    # Probe body with a big dish, far to the right.
    px, py = x1 - 66, y0 + 26
    draw.ellipse([px - 20, py - 14, px + 6, py + 14], outline=(230, 230, 230), width=3)
    draw.line([px + 4, py, px + 22, py + 16], fill=(230, 230, 230), width=2)
    draw.rectangle([px + 16, py + 12, px + 34, py + 24], fill=(200, 170, 80))
    # Signal arcs travelling back toward Earth at the left edge.
    for r in (26, 46, 66):
        draw.arc([px - r - 30, py - r, px - 30 + r, py + r], start=140, end=220, fill=(140, 200, 240), width=2)
    draw.ellipse([x0 + 12, y1 - 30, x0 + 40, y1 - 2], fill=(70, 140, 200))
    draw.rectangle(box, outline=INK, width=1)


def spot_eu_loan(draw, box):
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=(232, 228, 210))
    cx, cy, r = x0 + 66, y0 + 37, 27
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(31, 58, 140))
    for k in range(12):
        ang = math.radians(k * 30)
        sx = cx + int(17 * math.cos(ang))
        sy = cy + int(17 * math.sin(ang))
        draw.ellipse([sx - 3, sy - 3, sx + 3, sy + 3], fill=(250, 210, 60))
    coin_font = load_font(SANS_BOLD, 22)
    draw.ellipse([x0 + 120, y0 + 12, x0 + 176, y0 + 62], fill=(240, 200, 70), outline=(184, 134, 11), width=3)
    draw.text((x0 + 136, y0 + 24), "€45", font=coin_font, fill=(90, 64, 4))
    # A simple parliament block.
    bx = x0 + 196
    draw.rectangle([bx, y0 + 30, bx + 76, y1 - 10], fill=(150, 148, 138))
    draw.polygon([(bx - 4, y0 + 30), (bx + 38, y0 + 16), (bx + 80, y0 + 30)], fill=(110, 108, 98))
    for i in range(4):
        draw.rectangle([bx + 8 + i * 18, y0 + 40, bx + 15 + i * 18, y1 - 18], fill=(90, 88, 80))
    draw.rectangle(box, outline=INK, width=1)


def spot_drone_shield(draw, box):
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=(238, 224, 196))
    draw.rectangle([x0, y1 - 14, x1, y1], fill=(198, 168, 116))
    # Air-base buildings.
    draw.rectangle([x0 + 18, y1 - 38, x0 + 86, y1 - 14], fill=(128, 122, 108))
    draw.rectangle([x0 + 96, y1 - 30, x0 + 140, y1 - 14], fill=(112, 106, 94))
    # Drone in the upper right.
    dx, dy = x1 - 64, y0 + 20
    draw.rectangle([dx - 12, dy - 5, dx + 12, dy + 5], fill=(40, 40, 40))
    for ox, oy in ((-16, -8), (16, -8), (-16, 8), (16, 8)):
        draw.ellipse([dx + ox - 6, dy + oy - 3, dx + ox + 6, dy + oy + 3], outline=(40, 40, 40), width=2)
    # Interception burst between drone and base.
    bx, by = x0 + 168, y0 + 34
    for ang in range(0, 360, 45):
        rad = math.radians(ang)
        draw.line(
            [bx + int(6 * math.cos(rad)), by + int(6 * math.sin(rad)),
             bx + int(18 * math.cos(rad)), by + int(18 * math.sin(rad))],
            fill=(230, 120, 30), width=3,
        )
    draw.ellipse([bx - 5, by - 5, bx + 5, by + 5], fill=(250, 180, 60))
    draw.rectangle(box, outline=INK, width=1)


def spot_capitol(draw, box):
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=(220, 232, 242))
    cx = x0 + 88
    draw.rectangle([cx - 52, y1 - 26, cx + 52, y1 - 8], fill=(232, 230, 222), outline=(120, 118, 108))
    draw.rectangle([cx - 30, y1 - 38, cx + 30, y1 - 26], fill=(232, 230, 222), outline=(120, 118, 108))
    draw.pieslice([cx - 30, y1 - 62, cx + 30, y1 - 26], start=180, end=360, fill=(96, 120, 150))
    draw.rectangle([cx - 2, y1 - 68, cx + 2, y1 - 60], fill=(96, 120, 150))
    for i in range(5):
        wx = cx - 42 + i * 21
        draw.rectangle([wx, y1 - 21, wx + 9, y1 - 12], fill=(96, 120, 150))
    # Gavel at the right.
    gx, gy = x1 - 74, y0 + 26
    draw.rectangle([gx - 20, gy - 9, gx + 8, gy + 9], fill=(110, 72, 36))
    draw.line([gx + 4, gy + 6, gx + 34, gy + 34], fill=(110, 72, 36), width=5)
    draw.rectangle([gx - 24, gy + 38, gx + 26, gy + 44], fill=(80, 52, 26))
    draw.rectangle(box, outline=INK, width=1)


# --------------------------------------------------------------------------
# Page assembly
# --------------------------------------------------------------------------

GRID_STORIES = [
    {
        "kicker": "CULTURE",
        "spot": spot_palms,
        "headline": "GTA VI's first full day",
        "body": "Launched 19 Nov on PS5 and Xbox after a 13-year wait. "
                "Launch-day streams smashed viewer records; critics gave it a 99 Metascore.",
    },
    {
        "kicker": "ASIA / APEC",
        "spot": spot_summit,
        "headline": "APEC summit in Shenzhen",
        "body": "Trump, Xi and Putin hold a first-ever trilateral on the sidelines, "
                "with Iran and nuclear arms cuts on the table.",
    },
    {
        "kicker": "SCIENCE",
        "spot": spot_voyager,
        "headline": "Voyager 1, a light-day away",
        "body": "The probe has crossed one light-day from Earth — 16.1 billion miles. "
                "NASA confirms the milestone at JPL.",
    },
    {
        "kicker": "EUROPE",
        "spot": spot_eu_loan,
        "headline": "EU proposes €45bn loan for Ukraine",
        "body": "€25bn for the military and €20bn for the budget, repaid only "
                "after Russia pays reparations.",
    },
    {
        "kicker": "MIDDLE EAST",
        "spot": spot_drone_shield,
        "headline": "Iran fires on US base in Kuwait",
        "body": "Drones targeted Ali Al Salem Air Base. Kuwait says they were "
                "intercepted; no US personnel were hurt.",
    },
    {
        "kicker": "UNITED STATES",
        "spot": spot_capitol,
        "headline": "Jeffries nominated for Speaker",
        "body": "House Democrats picked Hakeem Jeffries 251–11. He would be the "
                "first Black Speaker; the House votes on 3 January.",
    },
]

ALSO_TODAY = (
    "Pew report: Islam to pass Christianity as largest faith by 2035  ·  "
    "Modi meets the Prince and Princess of Wales  ·  "
    "Fed minutes point to more rate rises  ·  "
    "Canada's Carney recalibrates China ties"
)


def build_poster():
    img = Image.new("RGB", (CANVAS, CANVAS), PAPER)
    d = ImageDraw.Draw(img)

    masthead_font = load_font(SERIF_BOLD, 52)
    dateline_font = load_font(SANS_BOLD, 17)
    kicker_font = load_font(SANS_BOLD, 14)
    lead_head_font = load_font(SERIF_BOLD, 36)
    body_font = load_font(SERIF, 15)
    caption_font = load_font(SANS, 12)
    cell_head_font = load_font(SERIF_BOLD, 18)
    cell_body_font = load_font(SANS, 12)
    band_label_font = load_font(SANS_BOLD, 13)
    band_font = load_font(SANS, 14)

    margin = 32

    # ---- Masthead -------------------------------------------------------
    d.line([margin, 26, CANVAS - margin, 26], fill=RULE, width=3)
    centred(d, "THE WORLD IN ONE DAY", masthead_font, CANVAS // 2, 36, INK)
    centred(d, "FRIDAY, 20 NOVEMBER 2026  ·  ALL THE DAY'S NEWS ON ONE PAGE", dateline_font, CANVAS // 2, 104, SOFT_INK)
    d.line([margin, 134, CANVAS - margin, 134], fill=RULE, width=3)
    d.line([margin, 140, CANVAS - margin, 140], fill=RULE, width=1)

    # ---- Lead story -----------------------------------------------------
    lead_top = 156
    lead_bottom = 456
    art_box = (margin, lead_top + 8, margin + 470, lead_bottom - 34)
    paint_cyclone_scene(d, art_box)
    d.text(
        (margin, lead_bottom - 26),
        "Cyclone Akvan spirals toward the Odisha–Andhra coast.",
        font=caption_font, fill=SOFT_INK,
    )

    tx = margin + 492
    tw = CANVAS - margin - tx
    d.text((tx, lead_top + 6), "WEATHER / ASIA  ·  LEAD STORY", font=kicker_font, fill=ACCENT_RED)
    y = draw_wrapped(d, "Cyclone Akvan makes landfall in India", lead_head_font, tx, lead_top + 28, tw, 2, INK)
    y += 4
    lead_body = (
        "A severe storm hits the Odisha–Andhra coast between Narsapur and Puri "
        "at midday today, Friday 20 November. Red alerts are in force along "
        "the shoreline, schools have been shut, and evacuations are under way "
        "as the cyclone drives heavy rain and storm surge inland."
    )
    y = draw_wrapped(d, lead_body, body_font, tx, y, tw, 3, INK)
    y += 4
    d.text((tx, y), "Red alerts · Schools shut · Evacuations under way", font=load_font(SANS_BOLD, 13), fill=ACCENT_BLUE)

    d.line([margin, lead_bottom + 8, CANVAS - margin, lead_bottom + 8], fill=RULE, width=2)

    # ---- Six-story grid -------------------------------------------------
    grid_top = lead_bottom + 20
    grid_bottom = 888
    cols, rows = 3, 2
    gutter = 16
    cell_w = (CANVAS - 2 * margin - (cols - 1) * gutter) // cols
    cell_h = (grid_bottom - grid_top - (rows - 1) * gutter) // rows

    for idx, story in enumerate(GRID_STORIES):
        col = idx % cols
        row = idx // cols
        cx0 = margin + col * (cell_w + gutter)
        cy0 = grid_top + row * (cell_h + gutter)
        cx1 = cx0 + cell_w
        cy1 = cy0 + cell_h
        d.rectangle([cx0, cy0, cx1, cy1], outline=RULE, width=1)
        pad = 10
        d.text((cx0 + pad, cy0 + 7), story["kicker"], font=kicker_font, fill=ACCENT_BLUE)
        spot_box = (cx0 + pad, cy0 + 28, cx1 - pad, cy0 + 92)
        story["spot"](d, spot_box)
        hy = draw_wrapped(d, story["headline"], cell_head_font, cx0 + pad, cy0 + 98, cell_w - 2 * pad, 1, INK)
        draw_wrapped(d, story["body"], cell_body_font, cx0 + pad, hy + 4, cell_w - 2 * pad, 3, SOFT_INK)

    # ---- Also-today strip ----------------------------------------------
    band_top = 900
    band_bottom = 992
    d.rectangle([margin, band_top, CANVAS - margin, band_bottom], fill=BAND_BG)
    d.text((margin + 14, band_top + 10), "ALSO TODAY", font=band_label_font, fill=(250, 210, 60))
    draw_wrapped(
        d, ALSO_TODAY, band_font,
        margin + 14, band_top + 32,
        CANVAS - 2 * margin - 28, 4, BAND_FG,
    )

    return img


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    out_path = os.path.join(here, "entry.png")
    poster = build_poster()
    poster.save(out_path, format="PNG", optimize=True)
    print(f"wrote {out_path} ({poster.size[0]}x{poster.size[1]})")


if __name__ == "__main__":
    main()
