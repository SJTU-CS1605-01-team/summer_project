#!/usr/bin/env python3
"""Render a legible evidence image from the first 10 rows of the processed CT CSV."""

import csv
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "processed" / "canada_ct_10_indicators_2021.csv"
OUTPUT = ROOT / "evidence" / "indicator_data_sample.png"


def font(size: int, bold: bool = False):
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/HelveticaNeue.ttc",
    ]
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            pass
    return ImageFont.load_default()


with SOURCE.open("r", encoding="utf-8", newline="") as f:
    reader = csv.reader(f)
    header = next(reader)
    rows = [row for _, row in zip(range(10), reader)]

header_font = font(20, bold=True)
body_font = font(19)
title_font = font(28, bold=True)
pad_x = 14
row_height = 42
title_height = 72

measure = Image.new("RGB", (1, 1))
md = ImageDraw.Draw(measure)
widths = []
for col, name in enumerate(header):
    texts = [name] + [row[col] for row in rows]
    measured = max(md.textbbox((0, 0), text, font=header_font if i == 0 else body_font)[2] for i, text in enumerate(texts))
    widths.append(max(135, measured + pad_x * 2))

canvas_width = sum(widths) + 2
canvas_height = title_height + row_height * (len(rows) + 1) + 2
img = Image.new("RGB", (canvas_width, canvas_height), "#FFFFFF")
draw = ImageDraw.Draw(img)
draw.rectangle((0, 0, canvas_width, title_height), fill="#123B5D")
draw.text((18, 18), "Canada-wide 2021 Census Tract sample - not yet filtered to Toronto City", fill="#FFFFFF", font=title_font)

x = 1
y = title_height
for col, name in enumerate(header):
    draw.rectangle((x, y, x + widths[col], y + row_height), fill="#2F75B5", outline="#D9E3F0", width=1)
    draw.text((x + pad_x, y + 10), name, fill="#FFFFFF", font=header_font)
    x += widths[col]

for row_idx, row in enumerate(rows):
    x = 1
    y = title_height + row_height * (row_idx + 1)
    fill = "#F3F7FB" if row_idx % 2 == 0 else "#FFFFFF"
    for col, value in enumerate(row):
        draw.rectangle((x, y, x + widths[col], y + row_height), fill=fill, outline="#D9E3F0", width=1)
        draw.text((x + pad_x, y + 10), value, fill="#1F2933", font=body_font)
        x += widths[col]

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
img.save(OUTPUT, format="PNG", optimize=True)
print(f"saved {OUTPUT} ({canvas_width}x{canvas_height})")
