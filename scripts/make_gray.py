import sys
from PIL import Image

GRAY = (156, 163, 175)  # Tailwind gray-400, common "disabled/inactive" tone

def make_gray(black_master_path, out_path):
    img = Image.open(black_master_path).convert("RGBA")
    alpha = img.getchannel("A")
    gray_out = Image.new("RGBA", img.size, GRAY + (0,))
    gray_out.putalpha(alpha)
    gray_out.save(out_path)
    print(f"done: {out_path}")

if __name__ == "__main__":
    make_gray(sys.argv[1], sys.argv[2])
