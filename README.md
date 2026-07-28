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

**Pitfall already hit once — a "badge" can fill the entire canvas with zero outer margin** (e.g. LinkedIn's flat blue "in" icon: solid blue, edge-to-edge, no separate matte). Here the corner-seeded flood-fill's reference color IS the badge's own brand fill, not true background, so it eats the *entire* badge — correct for the black/white glyph, but wrong for color (loses the badge fill entirely). `fg_fraction` can't distinguish this from a legitimate matte removal (e.g. Lark's bird on white leaves a similarly-sized remainder). The real signal is **saturation of the corner reference color**: a genuine background matte is neutral (white/black/gray, low saturation) at any brightness; a brand fill is usually a saturated, colorful hue. `generate_icon.py`'s `remove_background()` checks this — if the corner color's saturation (`max(rgb) - min(rgb)`) is above 25, stage-1 removal is skipped entirely for the **color** mask (kept as the full original image), while the glyph mask for black/white is unaffected.

**Some icons just don't survive automated silhouette extraction — know when to stop and flag it.** Disney+'s icon is a cursive script wordmark ("Disney+") over a gradient/starry background. The two-stage removal can technically isolate *something*, but the result is an unrecognizable abstract shape, not legible text — cursive/stylized wordmarks don't have the clean glyph-vs-background contrast this pipeline assumes. When a black/white/outline result doesn't actually read as the brand mark, don't ship it — ship color only and flag the app as needing a manually-sourced vector wordmark for the other variants, same as the Notion page does for Disney+.

## Line/outline method

Derived automatically from the solid black silhouette mask — no separate manual redraw:

1. Take the solid silhouette's alpha mask.
2. Compute the Euclidean distance transform of the mask (`scipy.ndimage.distance_transform_edt`) — each foreground pixel's distance to the nearest background pixel.
3. Ring = mask pixels whose distance is ≤ the stroke width (default ~4.3% of canvas, e.g. 44px at 1024px). Outer contour and any interior holes (e.g. the grid cells inside the Google Sheets icon, or the bowl of Pipedrive's "p") come through as inner outline lines for free, with smooth rounded corners since the distance transform is isotropic.

**Do not use a square min-filter (e.g. PIL's `ImageFilter.MinFilter`) for the erosion step** — it was the first approach here and produced sharp, mitered corners at every turn instead of a smooth stroke, reading as "ugly"/technical rather than a proper line icon. The Euclidean distance transform is the fix; it's the same reason vector stroke tools default to round joins.

Stroke width needs a per-icon sanity check: on a thin letterform (Pipedrive's "p") the default 44px is wider than the bowl's own ring, so the inner and outer erosion boundaries overlap into a double-line mess — dropping to ~28px fixed it. Rule of thumb: stroke width should be comfortably less than the thinnest stroke in the source glyph.

**Also check whether the source mask touches the canvas edge before generating an outline.** Google Sheets' Simple Icons source has zero margin (its ink spans the full canvas top-to-bottom, by Simple Icons' design — they expect consumers to add their own padding). Solid black/white/color are fine edge-to-edge, but an outline's stroke ring has nowhere to close on an edge it's flush against, so it renders visibly clipped/cut off at that edge. Fix: pad the mask first (`make_tile.py`, ~8% margin) and generate the outline from the padded version — solid variants stay edge-to-edge as before, only the outline source gets padded.

This holds up down to ~16px; below that the stroke gets thin enough to lose crispness, same limitation any detailed line icon has at very small sizes.

## Licensing note

All logos are trademarks of their respective companies. Simple Icons entries are CC0-licensed reproductions; App Store-sourced icons are the companies' own copyrighted assets pulled from their public listings. This library is for internal reference use — check each brand's guidelines before external/public use, especially before recoloring or altering their mark.
