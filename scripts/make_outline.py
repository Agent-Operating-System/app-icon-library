import sys
import numpy as np
from scipy.ndimage import distance_transform_edt
from PIL import Image

def make_outline(mask_source_path, out_prefix, stroke_px=44):
    img = Image.open(mask_source_path).convert("RGBA")
    alpha = np.array(img.getchannel("A"), dtype=np.uint8)
    mask = alpha > 127

    # distance from each foreground pixel to the nearest background pixel (Euclidean, isotropic -> round joins)
    dist = distance_transform_edt(mask)
    ring = mask & (dist <= stroke_px)

    ring_alpha = (ring * 255).astype(np.uint8)

    w, h = img.size
    black_out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    white_out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    alpha_img = Image.fromarray(ring_alpha, mode="L")
    black_rgb = Image.new("RGBA", (w, h), (0, 0, 0, 255))
    white_rgb = Image.new("RGBA", (w, h), (255, 255, 255, 255))
    black_out = Image.composite(black_rgb, black_out, alpha_img)
    white_out = Image.composite(white_rgb, white_out, alpha_img)
    black_out.putalpha(alpha_img)
    white_out.putalpha(alpha_img)

    black_out.save(f"{out_prefix}-outline-black.png")
    white_out.save(f"{out_prefix}-outline-white.png")
    print(f"done: {out_prefix} outline (stroke={stroke_px}px @ {w}x{h}, euclidean)")

if __name__ == "__main__":
    stroke = int(sys.argv[3]) if len(sys.argv) > 3 else 44
    make_outline(sys.argv[1], sys.argv[2], stroke)
