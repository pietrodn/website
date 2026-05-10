#!/usr/bin/env python3
"""Compose a 3x2 quiz mosaic: 3 AI-generated works mixed with 3 human-made works."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).parent
TILE_W, TILE_H = 600, 800
GAP = 20
BG = (20, 20, 24)
LABEL_BG = (0, 0, 0, 200)
LABEL_FG = (255, 255, 255)

# Ordering — non-alternating pattern (H-AI-H / H-AI-AI) so the sequence
# doesn't leak the answer. Visually-similar pairs are kept non-adjacent:
#   Rembrandt(3)  <-> Pseudomnesia(6)     (diagonal, ritratti)
#   Migrant(1)    <-> MCB 90 Miles(5)     (diagonale, reportage umano/AI)
#   Wanderer(4)   <-> Théâtre(2)          (diagonale, paesaggio/scena)
# (file, label, is_ai)
TILES = [
    ("migrant_mother.jpg",              "1", False),
    ("theatre_opera_spatial.jpg",       "2", True),
    ("rembrandt_self_portrait_1659.jpg", "3", False),
    ("wanderer_sea_fog.jpg",            "4", False),
    ("brown_90miles_car_raft.jpg",      "5", True),
    ("pseudomnesia_electrician.jpg",    "6", True),
]

def fit_crop(img: Image.Image, w: int, h: int) -> Image.Image:
    """Scale + center-crop to exactly w x h."""
    target_ratio = w / h
    src_ratio = img.width / img.height
    if src_ratio > target_ratio:
        new_h = h
        new_w = int(round(img.width * h / img.height))
    else:
        new_w = w
        new_h = int(round(img.height * w / img.width))
    img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
    left = (new_w - w) // 2
    top = (new_h - h) // 2
    return img.crop((left, top, left + w, top + h))


def find_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for path in (
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/Library/Fonts/Arial.ttf",
    ):
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def make_mosaic(reveal: bool = False) -> Image.Image:
    cols, rows = 3, 2
    W = cols * TILE_W + (cols + 1) * GAP
    H = rows * TILE_H + (rows + 1) * GAP
    canvas = Image.new("RGB", (W, H), BG)
    font_label = find_font(90)
    font_caption = find_font(28)

    for idx, (fname, label, is_ai) in enumerate(TILES):
        r, c = divmod(idx, cols)
        x = GAP + c * (TILE_W + GAP)
        y = GAP + r * (TILE_H + GAP)
        src = Image.open(HERE / fname).convert("RGB")
        tile = fit_crop(src, TILE_W, TILE_H)
        canvas.paste(tile, (x, y))

        overlay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
        od = ImageDraw.Draw(overlay)
        box_w, box_h = 100, 100
        od.rectangle([x, y, x + box_w, y + box_h], fill=LABEL_BG)
        bbox = od.textbbox((0, 0), label, font=font_label)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        od.text(
            (x + (box_w - tw) // 2 - bbox[0], y + (box_h - th) // 2 - bbox[1]),
            label, fill=LABEL_FG, font=font_label,
        )
        if reveal:
            tag = "AI" if is_ai else "UMANO"
            tag_color = (220, 60, 60, 230) if is_ai else (60, 170, 80, 230)
            tag_bbox = od.textbbox((0, 0), tag, font=font_caption)
            tag_w = tag_bbox[2] - tag_bbox[0] + 24
            tag_h = tag_bbox[3] - tag_bbox[1] + 16
            tx = x + TILE_W - tag_w - 12
            ty = y + TILE_H - tag_h - 12
            od.rectangle([tx, ty, tx + tag_w, ty + tag_h], fill=tag_color)
            od.text(
                (tx + 12 - tag_bbox[0], ty + 8 - tag_bbox[1]),
                tag, fill=(255, 255, 255), font=font_caption,
            )
        canvas = Image.alpha_composite(canvas.convert("RGBA"), overlay).convert("RGB")

    return canvas


if __name__ == "__main__":
    out1 = HERE.parent / "quiz_mosaic.png"
    out2 = HERE.parent / "quiz_mosaic_reveal.png"
    make_mosaic(reveal=False).save(out1, optimize=True)
    make_mosaic(reveal=True).save(out2, optimize=True)
    print(f"Wrote {out1}")
    print(f"Wrote {out2}")
