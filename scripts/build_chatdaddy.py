#!/usr/bin/env python3
"""Custom build for ChatDaddy's own icon (badge = <rect> bg + <path> glyph on top,
not a Simple-Icons-style single-tone glyph and not a Skype-style overlapping-path
badge where uniform recolor still reads). The pipeline's with_fill() only rewrites
<path> fill, so calling from_svg() directly would leave the blue rect background
untouched for black/white masters. Instead: color = full original SVG unmodified;
black/white = ONLY the 3 glyph <path> elements (rects dropped), recolored, on
transparent canvas - matching how every other app's silhouette master looks Given the reusable_icon_pipeline
"""
import sys, os, re
sys.path.insert(0, os.path.dirname(__file__))
from generate_icon import make_outline, export_ladder, SIZES
from rasterize import rasterize_svg
from PIL import Image

SLUG = "chatdaddy"
OUT_ROOT = "/tmp/app-icon-library-repo/icons"
APP_DIR = f"{OUT_ROOT}/{SLUG}"
PNG_DIR = f"{APP_DIR}/png"
os.makedirs(PNG_DIR, exist_ok=True)

SOURCE_SVG = open("/tmp/chatdaddy-icon-work/chatdaddy-color-source.svg").read()

# color: full original SVG (badge + gradient + white glyph), completely unmodified
color_svg = SOURCE_SVG

# black/white: extract ONLY the 3 glyph <path> elements (drop the 2 <rect> bg elements),
# recolor them, transparent canvas, same 0 0 36 36 viewBox so proportions match
glyph_paths = re.findall(r'<path\b[^>]*/>', SOURCE_SVG)
assert len(glyph_paths) == 3, f"expected 3 glyph paths, found {len(glyph_paths)}"

def build_glyph_svg(hexcolor):
    recolored = []
    for p in glyph_paths:
        # strip existing fill=".." and inject the new one
        p2 = re.sub(r'\sfill="[^"]*"', '', p)
        p2 = p2.replace('<path ', f'<path fill="#{hexcolor}" ')
        recolored.append(p2)
    return (
        '<svg width="36" height="36" viewBox="0 0 36 36" fill="none" '
        'xmlns="http://www.w3.org/2000/svg">' + "".join(recolored) + "</svg>"
    )

black_svg = build_glyph_svg("000000")
white_svg = build_glyph_svg("FFFFFF")

open(f"{APP_DIR}/{SLUG}-color.svg", "w").write(color_svg)
open(f"{APP_DIR}/{SLUG}-black.svg", "w").write(black_svg)
open(f"{APP_DIR}/{SLUG}-white.svg", "w").write(white_svg)

print("Wrote color/black/white SVG masters")

# outline: derive from black glyph raster via Euclidean distance transform,
# same method as the rest of the pipeline (not a min-filter)
black_1024 = rasterize_svg(black_svg, 1024)
outline_black, outline_white = make_outline(black_1024, stroke_px=28)
outline_black.save(f"{APP_DIR}/{SLUG}-outline-black.png")
outline_white.save(f"{APP_DIR}/{SLUG}-outline-white.png")
print("Wrote outline-black/outline-white masters")

# size ladder for color/black/white via SVG rasterization at each size
for name, svg in [("color", color_svg), ("black", black_svg), ("white", white_svg)]:
    for s in SIZES:
        rasterize_svg(svg, s).save(f"{PNG_DIR}/{SLUG}-{name}-{s}.png")
    print(f"  {name}: {len(SIZES)} sizes done")

# size ladder for outline variants (from the pre-rendered 1024 masters)
for name, master in [("outline-black", outline_black), ("outline-white", outline_white)]:
    export_ladder(master, PNG_DIR, f"{SLUG}-{name}")
    print(f"  {name}: {len(SIZES)} sizes done")

print(f"\nDONE: {SLUG} icon set built at {APP_DIR}")
