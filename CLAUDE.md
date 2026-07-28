# App Icon Library — working standards

Reference set of SaaS/app icons for internal use. This file exists so the next pass (the
full ~100-app run, or any future addition) doesn't repeat mistakes already made and fixed
during the 3-app pilot (Pipedrive, Lark, Google Sheets).

## Scripts

All generator scripts are in `scripts/`. Setup:

```
pip install -r scripts/requirements.txt   # Pillow, scipy, numpy
cd scripts && npm install                  # sharp, for SVG rasterization
```

- `floodfill2.py` — two-stage background removal (see below)
- `make_outline.py` — stroke/outline generation via Euclidean distance transform
- `make_gray.py` — gray/disabled tone from a black mask
- `make_tile.py` — padding/visual-weight normalization
- `resize_raster.py` — PNG master → full size ladder (PIL/LANCZOS)
- `resize_svg.js` — SVG master → full size ladder (sharp)

## Deliverable per app

Variants: `color`, `black` (solid silhouette), `white` (solid silhouette), `outline-black`
(stroke), `outline-white` (stroke). Sizes: 4, 8, 16, 24, 32, 48, 64, 96, 128, 256, 512, 1024
(px), all on a 1:1 square canvas. See README.md for the exact file/folder layout.

## Sourcing priority (check in this order)

1. **[Simple Icons](https://simpleicons.org)** (CC0) — vector, official brand hex baked in
   as the icon title/slug but **not** as a `fill` attribute on the raw file (see pitfall
   below). Best case, use directly.
2. **A clean vector icon-only monogram embedded on the brand's own marketing site** — look
   in the page's inline `<svg>` tags near the nav bar / header (grep for
   `viewBox` blocks near a `logo`/`monogram` class, or an `aria-label` matching the brand
   name). Sites often have a small icon-only mark (used when nav collapses) that's flat and
   clean, separate from the full wordmark and separate from the "badge" app-icon rendering.
   Use this for **black/white/outline** whenever the app-store icon is a "badge" style (see
   below) — it avoids inheriting bevel/gradient artifacts. Real example: Pipedrive's App
   Store icon is a glossy green badge with a beveled "p"; their own site has a flat "p"
   monogram SVG that gives a much cleaner silhouette.
3. **App Store / Play Store listing** (their real published icon, via the iTunes Search API
   or a Play Store page scrape) — fallback when neither of the above exists. Only reliable
   for **color**; for black/white/outline it works well for "glyph-on-transparent" icons
   (mark directly on a transparent/plain background, e.g. Lark) but only approximately for
   "badge" icons (colored container + separate glyph, e.g. Pipedrive) — check step 2 first
   for any badge-style icon.

## Background-removal method (for App Store-sourced icons)

Two-stage flood fill from `floodfill2.py`:

1. **Corner flood-fill**: flood-fill from the four image corners by color distance →
   removes the true background. This mask alone is what the **color** master uses, so the
   original badge/container is preserved.
2. **Container peel** (only if step 1 leaves >50% of the canvas opaque — the signature of a
   "badge" icon): flood-fill inward again, seeded from the new background edge, using that
   edge's color as reference, to strip the badge container and isolate the glyph.
3. **Component cleanup**: keep only connected foreground regions ≥10% of the largest one, to
   drop anti-aliasing edge-halo artifacts left by step 2.

**Critical pitfall already hit once:** steps 2–3 must only affect the mask used for
**black/white**, never the mask used for **color**. Applying the fully-peeled mask to color
strips the original container entirely (color output regresses to just the bare glyph on
transparent, losing the recognizable badge). Keep two separate masks (`is_bg_color` vs
`is_bg`) — see `floodfill2.py`.

## Outline/stroke method

Erode-and-subtract from the solid black silhouette mask:

1. Compute the **Euclidean distance transform** of the mask (`scipy.ndimage.distance_transform_edt`)
   — each foreground pixel's distance to the nearest background pixel.
2. Ring = mask pixels whose distance ≤ stroke width.

**Pitfall already hit once:** do NOT use a square structuring element (e.g. PIL's
`ImageFilter.MinFilter`) for the erosion — it produces sharp mitered corners at every turn,
which reads as "ugly"/too-technical rather than a normal line icon. Euclidean distance
transform is isotropic and gives smooth rounded corners automatically (the same reason
vector stroke tools default to round joins). Always sanity-check the result visually before
shipping a size ladder — this bug wasn't obvious from code review, only from looking at the
rendered image.

**Stroke width tuning:** default is ~4.3% of canvas (44px @ 1024px), but this must be
sanity-checked per icon. If the icon has a thin letterform stroke (e.g. the bowl of a "p"),
44px can exceed the glyph's own stroke width, so the inner and outer erosion boundaries of a
hole overlap into a double-line mess. Rule of thumb: stroke width should be comfortably less
than the thinnest stroke/ring in the source glyph. Check visually at 1024px before finalizing.

## Padding / visual-weight normalization (tile variant)

Icons vary wildly in how much of the canvas their "ink" fills — a badge icon can be ~100%,
a glyph-on-transparent icon can be 80% or less. Left unnormalized, icons won't read as the
same size sitting next to each other in a grid/directory UI. `make_tile.py` crops to the
ink bounding box and recenters it at a fixed padding percentage (tested at 14% margin / 72%
fill). Status: proposed, not yet finalized into the standard pipeline — confirm padding %
and whether it applies to color only or every variant before rolling into the full run.

## Gray / "disabled" tone

Reuses the black silhouette mask, filled with a neutral tone (tested: Tailwind gray-400,
`#9CA3AF`) instead of pure black — for muted/inactive UI states. Status: proposed, not yet
finalized (tone may change based on feedback).

## Storage & publishing workflow

- **Files live on GitHub** (`Agent-Operating-System/app-icon-library`, public repo) — Notion's
  API cannot accept binary image uploads at all, so raw files are never pushed to Notion.
  Reference: `raw.githubusercontent.com/Agent-Operating-System/app-icon-library/main/...`.
- **Notion catalogs it** — the "🎨 Brand Assets / Media Library" database gets one page per
  app, embedding the color/black/white/outline previews via external image URL (Notion's API
  supports this natively, no browser automation needed) plus a `Storage Link` property
  pointing at the GitHub folder.
- **Notion caches external images by URL.** After regenerating a file at the *same* URL
  (e.g. fixing a bug and re-pushing), Notion will keep showing the stale cached image unless
  the URL changes. Append a cache-busting query string (`?v=2`, `?v=3`, incrementing each
  time) to force a refetch. This has already been needed twice in this project.
- **Repo transfer**: `gh api repos/{owner}/{repo}/transfer -f new_owner={org}`. After
  transferring, GitHub keeps the old path as a redirect, but don't rely on it — update every
  downstream reference (Notion image URLs, `Storage Link` properties, page icons) to the new
  canonical URL, since redirects aren't guaranteed to persist indefinitely.
- **Notion `update_content` search-replace requires an exact match**, including leading tabs
  in indented blocks (columns, callouts). If an edit 400s with "no matches found," re-fetch
  the page first — content may have drifted from what you last wrote (e.g. Notion's own
  column-ratio auto-rebalancing can alter the block silently).

## Licensing note

All logos are trademarks of their respective companies. Simple Icons entries are
CC0-licensed reproductions; App Store-sourced and brand-site-sourced icons are the
companies' own copyrighted assets. This library is for internal reference use — check each
brand's guidelines before external/public use, especially before recoloring or altering
their mark. Note this per-app in the Notion page's `Usage Guidelines` property.
