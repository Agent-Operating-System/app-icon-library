import sys
from PIL import Image

SIZES = [4, 8, 16, 24, 32, 48, 64, 96, 128, 256, 512, 1024]

def run(master_path, out_dir, base_name):
    img = Image.open(master_path).convert("RGBA")
    for s in SIZES:
        resized = img.resize((s, s), Image.LANCZOS)
        resized.save(f"{out_dir}/{base_name}-{s}.png")
    print(f"exported {len(SIZES)} sizes for {base_name}")

if __name__ == "__main__":
    run(sys.argv[1], sys.argv[2], sys.argv[3])
