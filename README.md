# App Icon Library

Reference set of SaaS/app icons: original color, solid black/white silhouette, and black/white line (stroke-outline) versions, exported at multiple sizes, all on a 1:1 square canvas.

## Structure

```
icons/<app-slug>/
  <app-slug>-color.(svg|png)           # vector or high-res raster master, original brand color(s)
  <app-slug>-black.(svg|png)           # solid black silhouette master
  <app-slug>-white.(svg|png)           # solid white silhouette master
  <app-slug>-outline-black.png         # black line/stroke-outline master
  <app-slug>-outline-white.png         # white line/stroke-outline master
  png/
    <app-slug>-color-<size>.png
    <app-slug>-black-<size>.png
    <app-slug>-white-<size>.png
    <app-slug>-outline-black-<size>.png
    <app-slug>-outline-white-<size>.png
```

Sizes: 4, 8, 16, 24, 32, 48, 64, 96, 128, 256, 512, 1024 (px).

## Sourcing

Priority order, highest quality first:

1. **[Simple Icons](https://simpleicons.org)** (CC0) — vector, official brand hex color, single-color glyph on a transparent background. Best case: use directly.
2. **Official vector monogram from the brand's own marketing site** — many sites embed a clean icon-only SVG (no gradients/bevels) inline in their page markup (e.g. the nav bar's collapsed/mobile logo), separate from the full wordmark. This is often better than the app-store icon for black/white/outline, since store icons frequently carry glossy bevel/gradient rendering that muddies a silhouette (see Pipedrive below). When present, use it for **black/white/outline**; the color master can still be the app-store icon since that's the actual recognizable app-grid tile.
3. **App Store / Play Store listing** (their real published app icon) — fallback when neither of the above exists. Background-cleaned via flood-fill (see method below), which works well for glyph-on-transparent icons but only approximates a silhouette for colored "badge" icons.

**Pipedrive** is the example of #2: its App Store icon is a glossy green rounded-square badge with a beveled white "p"; flood-fill can isolate the "p" shape but inherits every gradient artifact. Pipedrive's own site embeds a clean flat vector "p" monogram (`viewBox="0 0 32 32"`) in its nav — that SVG is now the source for `pipedrive-black.svg` / `pipedrive-white.svg` / the outline, while `pipedrive-color.png` stays the app-store badge.

## Black/white silhouette method

Two-stage automated background removal, so the silhouette shows the actual glyph, not just a colored blob:

1. **Corner flood-fill**: remove the true image background (flood-filled from the four corners by color distance). Used as-is for the **color** master, so the original badge/container is preserved.
2. **Container peel** (only runs if step 1 leaves >50% of the canvas opaque — a sign the icon is a colored "badge" like Pipedrive's, not a glyph directly on transparent like Lark or Simple Icons): flood-fill inward again from the new background edge, using the color of that edge as reference, to strip away the badge's colored container and isolate just the glyph.
3. **Component cleanup**: keep only connected foreground regions ≥10% of the largest one, to drop thin anti-aliasing/edge-halo artifacts left over from step 2.

Result: **color** keeps the full original badge (container + glyph); **black/white** show just the glyph silhouette, whether or not the source icon has a colored container.

## Line/outline method

Derived automatically from the solid black silhouette mask — no separate manual redraw:

1. Take the solid silhouette's alpha mask.
2. Erode it by a fixed stroke width using a min-filter (default ~4.3% of canvas, e.g. 44px at 1024px).
3. Subtract the eroded mask from the original to leave a ring of that stroke width along every edge — outer contour and any interior holes (e.g. the grid cells inside the Google Sheets icon, or the bowl of Pipedrive's "p", come through as inner outline lines for free).

Stroke width needs a per-icon sanity check: on a thin letterform (Pipedrive's "p") the default 44px is wider than the bowl's own ring, so the inner and outer erosion boundaries overlap into a double-line mess — dropping to ~28px fixed it. Rule of thumb: stroke width should be comfortably less than the thinnest stroke in the source glyph.

This holds up down to ~16px; below that the stroke gets thin enough to lose crispness, same limitation any detailed line icon has at very small sizes.

## Licensing note

All logos are trademarks of their respective companies. Simple Icons entries are CC0-licensed reproductions; App Store-sourced icons are the companies' own copyrighted assets pulled from their public listings. This library is for internal reference use — check each brand's guidelines before external/public use, especially before recoloring or altering their mark.
