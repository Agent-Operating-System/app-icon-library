"""SVG -> PIL.Image rasterization via a Node/sharp subprocess (PIL alone can't do SVG)."""
import subprocess
import tempfile
import os
from PIL import Image

_SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))


def rasterize_svg(svg_text, size, density=384):
    with tempfile.NamedTemporaryFile(suffix=".svg", mode="w", delete=False) as f:
        f.write(svg_text)
        svg_path = f.name
    out_path = svg_path.replace(".svg", ".png")
    try:
        subprocess.run(
            ["node", "-e", f"""
const sharp = require('sharp');
sharp('{svg_path}', {{ density: {density} }}).resize({size}, {size}).png().toFile('{out_path}')
  .catch(e => {{ console.error(e); process.exit(1); }});
"""],
            check=True, cwd=_SCRIPTS_DIR, capture_output=True, text=True,
        )
        return Image.open(out_path).convert("RGBA").copy()
    finally:
        os.unlink(svg_path)
        if os.path.exists(out_path):
            os.unlink(out_path)
