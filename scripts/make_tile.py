import sys
from PIL import Image

def make_tile(src_path, out_path, padding_pct=14):
    img = Image.open(src_path).convert("RGBA")
    w, h = img.size
    bbox = img.getbbox()
    if bbox is None:
        img.save(out_path)
        return
    cropped = img.crop(bbox)
    cw, ch = cropped.size

    inner = w * (1 - 2 * padding_pct / 100)
    scale = inner / max(cw, ch)
    new_w, new_h = max(1, round(cw * scale)), max(1, round(ch * scale))
    resized = cropped.resize((new_w, new_h), Image.LANCZOS)

    canvas = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    paste_x = (w - new_w) // 2
    paste_y = (h - new_h) // 2
    canvas.paste(resized, (paste_x, paste_y), resized)
    canvas.save(out_path)
    ink_fraction = (max(cw, ch) / w) * 100
    print(f"done: {out_path} | original ink span={ink_fraction:.0f}% of canvas -> normalized to {100-2*padding_pct:.0f}%")

if __name__ == "__main__":
    padding = float(sys.argv[3]) if len(sys.argv) > 3 else 14
    make_tile(sys.argv[1], sys.argv[2], padding)
