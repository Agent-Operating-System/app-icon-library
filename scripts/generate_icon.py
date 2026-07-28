"""
Unified per-app icon generator, consolidating every fix from the 3-app pilot.
See CLAUDE.md for the full rationale behind each step.

Usage (as a library):
    from generate_icon import from_svg, from_raster

    from_svg(svg_text, "slug", "out_dir", hex_color="34A853")
    from_raster("path/to/appstore-icon-1024.png", "slug", "out_dir")

Both produce, under out_dir/<slug>/:
    <slug>-color.(svg|png)
    <slug>-black.(svg|png)
    <slug>-white.(svg|png)
    <slug>-outline-black.png
    <slug>-outline-white.png
    png/<slug>-<variant>-<size>.png  for size in SIZES
"""
import os
import re
import statistics
from collections import deque

import numpy as np
from scipy.ndimage import distance_transform_edt
from PIL import Image

SIZES = [4, 8, 16, 24, 32, 48, 64, 96, 128, 256, 512, 1024]
DEFAULT_STROKE_PX = 28          # conservative default; thinner than the 44px used when a
                                 # glyph's own strokes are known to be thick (tune up only
                                 # after a visual check shows the ring is too thin)
TILE_PADDING_PCT = 8            # margin added before outline generation if the mask
                                 # touches the canvas edge (would otherwise clip the stroke)


def _dist(a, b):
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 + (a[2] - b[2]) ** 2) ** 0.5


def _floodfill_bg(px, w, h, seeds, tolerance, ref_color, allowed):
    visited = [[False] * w for _ in range(h)]
    is_bg = [[False] * w for _ in range(h)]
    q = deque(seeds)
    while q:
        x, y = q.popleft()
        if x < 0 or x >= w or y < 0 or y >= h or visited[y][x]:
            continue
        visited[y][x] = True
        if not allowed[y][x]:
            continue
        r, g, b, a = px[x, y]
        if _dist((r, g, b), ref_color) <= tolerance:
            is_bg[y][x] = True
            q.append((x + 1, y)); q.append((x - 1, y))
            q.append((x, y + 1)); q.append((x, y - 1))
    return is_bg


def remove_background(raster_path, tol1=30, tol2=70, container_area_threshold=0.5):
    """Two-stage flood fill. Returns (color_mask_bg, glyph_mask_bg, img) - both are
    is_bg boolean grids; color_mask_bg is stage-1 only (keeps a badge's container),
    glyph_mask_bg is the further-peeled version for black/white silhouettes."""
    img = Image.open(raster_path).convert("RGBA")
    w, h = img.size
    px = img.load()

    all_true = [[True] * w for _ in range(h)]
    corner_seeds = ([(x, 0) for x in range(w)] + [(x, h - 1) for x in range(w)] +
                     [(0, y) for y in range(h)] + [(w - 1, y) for y in range(h)])
    bg_ref = px[0, 0][:3]
    is_bg_color = _floodfill_bg(px, w, h, corner_seeds, tol1, bg_ref, all_true)
    is_bg = [row[:] for row in is_bg_color]

    fg_fraction = sum(row.count(False) for row in is_bg) / (w * h)

    # Pitfall: some icons are a single solid-color square with NO separate outer
    # matte (e.g. LinkedIn's flat blue "in" badge, edge-to-edge, no padding). Here
    # the corner color IS the icon's own brand fill, not true background, so corner
    # flood-fill eats the entire badge, leaving only the inner glyph - correct for
    # the black/white silhouette, but wrong for "color" (loses the badge entirely).
    # Distinguishing signal: a genuine background matte is neutral (white/black/gray
    # padding, low saturation) regardless of how light or dark it is; a brand fill
    # is usually a saturated, colorful hue. fg_fraction alone can't tell these
    # apart - a real matte-removal (e.g. Lark's bird on white) and a wrongly-eaten
    # brand fill (LinkedIn's blue badge) can leave a similarly-sized remainder.
    saturation = max(bg_ref) - min(bg_ref)
    if saturation > 25:
        is_bg_color = [[False] * w for _ in range(h)]

    if fg_fraction > container_area_threshold:
        boundary_seeds, boundary_colors = [], []
        for y in range(h):
            for x in range(w):
                if is_bg[y][x]:
                    continue
                for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                    if 0 <= nx < w and 0 <= ny < h and is_bg[ny][nx]:
                        boundary_seeds.append((x, y))
                        boundary_colors.append(px[x, y][:3])
                        break
        ref2 = tuple(int(statistics.median(c[i] for c in boundary_colors)) for i in range(3))
        allowed = [[not is_bg[y][x] for x in range(w)] for y in range(h)]
        extra_bg = _floodfill_bg(px, w, h, boundary_seeds, tol2, ref2, allowed)
        for y in range(h):
            for x in range(w):
                if extra_bg[y][x]:
                    is_bg[y][x] = True

        # connected-component cleanup: drop small anti-aliasing edge-halo fragments
        labels = [[0] * w for _ in range(h)]
        sizes = {}
        next_label = 1
        for y in range(h):
            for x in range(w):
                if is_bg[y][x] or labels[y][x]:
                    continue
                lbl = next_label; next_label += 1
                stack = [(x, y)]
                count = 0
                while stack:
                    cx, cy = stack.pop()
                    if cx < 0 or cx >= w or cy < 0 or cy >= h:
                        continue
                    if is_bg[cy][cx] or labels[cy][cx]:
                        continue
                    labels[cy][cx] = lbl
                    count += 1
                    stack.extend([(cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)])
                sizes[lbl] = count
        if sizes:
            keep_threshold = max(sizes.values()) * 0.1
            for y in range(h):
                for x in range(w):
                    lbl = labels[y][x]
                    if lbl and sizes[lbl] < keep_threshold:
                        is_bg[y][x] = True

    return is_bg_color, is_bg, img


def _mask_to_rgba(img, is_bg, fill=None):
    w, h = img.size
    px = img.load()
    out = Image.new("RGBA", (w, h))
    opx = out.load()
    for y in range(h):
        for x in range(w):
            if is_bg[y][x]:
                opx[x, y] = (0, 0, 0, 0)
            elif fill is None:
                r, g, b, a = px[x, y]
                opx[x, y] = (r, g, b, 255)
            else:
                opx[x, y] = fill + (255,)
    return out


def pad_to_avoid_edge(img, padding_pct=TILE_PADDING_PCT):
    """Crop to ink bbox, shrink, recenter with margin - avoids outline clipping when the
    source mask touches the canvas edge. Only used as input to outline generation."""
    w, h = img.size
    bbox = img.getbbox()
    if bbox is None:
        return img
    touches_edge = bbox[0] == 0 or bbox[1] == 0 or bbox[2] == w or bbox[3] == h
    if not touches_edge:
        return img
    cropped = img.crop(bbox)
    cw, ch = cropped.size
    inner = w * (1 - 2 * padding_pct / 100)
    scale = inner / max(cw, ch)
    new_w, new_h = max(1, round(cw * scale)), max(1, round(ch * scale))
    resized = cropped.resize((new_w, new_h), Image.LANCZOS)
    canvas = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    canvas.paste(resized, ((w - new_w) // 2, (h - new_h) // 2), resized)
    return canvas


def make_outline(black_mask_img, stroke_px=DEFAULT_STROKE_PX):
    """Euclidean-distance-transform erode+subtract - NOT a square min-filter (mitered
    corners). Auto-pads first if the mask touches the canvas edge."""
    source = pad_to_avoid_edge(black_mask_img)
    alpha = np.array(source.getchannel("A"), dtype=np.uint8)
    mask = alpha > 127
    dist = distance_transform_edt(mask)
    ring = mask & (dist <= stroke_px)
    ring_alpha = Image.fromarray((ring * 255).astype(np.uint8), mode="L")

    w, h = source.size
    black_rgb = Image.new("RGBA", (w, h), (0, 0, 0, 255))
    white_rgb = Image.new("RGBA", (w, h), (255, 255, 255, 255))
    transparent = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    black_out = Image.composite(black_rgb, transparent, ring_alpha)
    white_out = Image.composite(white_rgb, transparent, ring_alpha)
    black_out.putalpha(ring_alpha)
    white_out.putalpha(ring_alpha)
    return black_out, white_out


def export_ladder(master_img, out_dir, base_name):
    os.makedirs(out_dir, exist_ok=True)
    for s in SIZES:
        master_img.resize((s, s), Image.LANCZOS).save(f"{out_dir}/{base_name}-{s}.png")


def from_raster(source_path, slug, out_root, stroke_px=DEFAULT_STROKE_PX):
    """App-store-icon-sourced pipeline: two-stage flood fill + outline."""
    app_dir = f"{out_root}/{slug}"
    png_dir = f"{app_dir}/png"
    os.makedirs(png_dir, exist_ok=True)

    is_bg_color, is_bg_glyph, img = remove_background(source_path)
    color = _mask_to_rgba(img, is_bg_color)
    black = _mask_to_rgba(img, is_bg_glyph, fill=(0, 0, 0))
    white = _mask_to_rgba(img, is_bg_glyph, fill=(255, 255, 255))
    outline_black, outline_white = make_outline(black, stroke_px)

    color.save(f"{app_dir}/{slug}-color.png")
    black.save(f"{app_dir}/{slug}-black.png")
    white.save(f"{app_dir}/{slug}-white.png")
    outline_black.save(f"{app_dir}/{slug}-outline-black.png")
    outline_white.save(f"{app_dir}/{slug}-outline-white.png")

    for name, master in [("color", color), ("black", black), ("white", white),
                          ("outline-black", outline_black), ("outline-white", outline_white)]:
        export_ladder(master, png_dir, f"{slug}-{name}")
    print(f"[raster] {slug}: done")


def from_svg(svg_text, slug, out_root, hex_color, stroke_px=DEFAULT_STROKE_PX, rasterize_fn=None):
    """Vector-sourced pipeline (Simple Icons or a scraped brand-site monogram).
    rasterize_fn(svg_text: str, size: int) -> PIL.Image must be supplied by the caller
    (uses `sharp` via a Node subprocess - see resize_svg.js) since PIL alone can't
    rasterize SVG."""
    app_dir = f"{out_root}/{slug}"
    png_dir = f"{app_dir}/png"
    os.makedirs(png_dir, exist_ok=True)

    def with_fill(svg, hexcolor):
        if re.search(r'<path[^>]*\sfill=', svg):
            return re.sub(r'(<path[^>]*\sfill=")[^"]*(")', rf'\g<1>#{hexcolor}\g<2>', svg)
        return re.sub(r'<path ', f'<path fill="#{hexcolor}" ', svg, count=0)

    color_svg = with_fill(svg_text, hex_color)
    black_svg = with_fill(svg_text, "000000")
    white_svg = with_fill(svg_text, "FFFFFF")

    open(f"{app_dir}/{slug}-color.svg", "w").write(color_svg)
    open(f"{app_dir}/{slug}-black.svg", "w").write(black_svg)
    open(f"{app_dir}/{slug}-white.svg", "w").write(white_svg)

    black_1024 = rasterize_fn(black_svg, 1024)
    outline_black, outline_white = make_outline(black_1024, stroke_px)
    outline_black.save(f"{app_dir}/{slug}-outline-black.png")
    outline_white.save(f"{app_dir}/{slug}-outline-white.png")

    for name, svg in [("color", color_svg), ("black", black_svg), ("white", white_svg)]:
        for s in SIZES:
            rasterize_fn(svg, s).save(f"{png_dir}/{slug}-{name}-{s}.png")
    for name, master in [("outline-black", outline_black), ("outline-white", outline_white)]:
        export_ladder(master, png_dir, f"{slug}-{name}")
    print(f"[svg] {slug}: done")
