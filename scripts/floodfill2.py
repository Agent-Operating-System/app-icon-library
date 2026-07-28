import sys
import statistics
from collections import deque
from PIL import Image

def dist(a, b):
    return ((a[0]-b[0])**2 + (a[1]-b[1])**2 + (a[2]-b[2])**2) ** 0.5

def floodfill_bg(px, w, h, seeds, tolerance, ref_color, allowed):
    """BFS from seeds, marking allowed[y][x] pixels within tolerance of ref_color as bg."""
    visited = [[False]*w for _ in range(h)]
    is_bg = [[False]*w for _ in range(h)]
    q = deque(seeds)
    while q:
        x, y = q.popleft()
        if x < 0 or x >= w or y < 0 or y >= h or visited[y][x]:
            continue
        visited[y][x] = True
        if not allowed[y][x]:
            continue
        r, g, b, a = px[x, y]
        if dist((r, g, b), ref_color) <= tolerance:
            is_bg[y][x] = True
            q.append((x+1, y)); q.append((x-1, y))
            q.append((x, y+1)); q.append((x, y-1))
    return is_bg

def process(path, out_prefix, tol1=30, tol2=70, container_area_threshold=0.5):
    img = Image.open(path).convert("RGBA")
    w, h = img.size
    px = img.load()

    all_true = [[True]*w for _ in range(h)]
    corner_seeds = [(x, 0) for x in range(w)] + [(x, h-1) for x in range(w)] + \
                   [(0, y) for y in range(h)] + [(w-1, y) for y in range(h)]
    bg_ref = px[0, 0][:3]
    is_bg_color = floodfill_bg(px, w, h, corner_seeds, tol1, bg_ref, all_true)
    is_bg = [row[:] for row in is_bg_color]

    fg_count = sum(row.count(False) for row in is_bg)
    fg_fraction = fg_count / (w * h)
    stage2_applied = False

    if fg_fraction > container_area_threshold:
        stage2_applied = True
        boundary_seeds = []
        boundary_colors = []
        for y in range(h):
            for x in range(w):
                if is_bg[y][x]:
                    continue
                for nx, ny in ((x+1,y),(x-1,y),(x,y+1),(x,y-1)):
                    if 0 <= nx < w and 0 <= ny < h and is_bg[ny][nx]:
                        boundary_seeds.append((x, y))
                        boundary_colors.append(px[x, y][:3])
                        break
        ref2 = tuple(int(statistics.median(c[i] for c in boundary_colors)) for i in range(3))
        allowed = [[not is_bg[y][x] for x in range(w)] for y in range(h)]
        extra_bg = floodfill_bg(px, w, h, boundary_seeds, tol2, ref2, allowed)
        for y in range(h):
            for x in range(w):
                if extra_bg[y][x]:
                    is_bg[y][x] = True

    if stage2_applied:
        labels = [[0]*w for _ in range(h)]
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
                    stack.extend([(cx+1,cy),(cx-1,cy),(cx,cy+1),(cx,cy-1)])
                sizes[lbl] = count
        if sizes:
            keep_threshold = max(sizes.values()) * 0.1
            for y in range(h):
                for x in range(w):
                    lbl = labels[y][x]
                    if lbl and sizes[lbl] < keep_threshold:
                        is_bg[y][x] = True

    color_out = Image.new("RGBA", (w, h))
    black_out = Image.new("RGBA", (w, h))
    white_out = Image.new("RGBA", (w, h))
    cpx = color_out.load(); bpx = black_out.load(); wpx = white_out.load()

    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if is_bg_color[y][x]:
                cpx[x, y] = (0, 0, 0, 0)
            else:
                cpx[x, y] = (r, g, b, 255)
            if is_bg[y][x]:
                bpx[x, y] = wpx[x, y] = (0, 0, 0, 0)
            else:
                bpx[x, y] = (0, 0, 0, 255)
                wpx[x, y] = (255, 255, 255, 255)

    color_out.save(f"{out_prefix}-color.png")
    black_out.save(f"{out_prefix}-black.png")
    white_out.save(f"{out_prefix}-white.png")
    print(f"done: {out_prefix} | stage2_applied={stage2_applied} | fg_fraction={fg_fraction:.2f}")

if __name__ == "__main__":
    process(sys.argv[1], sys.argv[2])
