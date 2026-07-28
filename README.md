# App Icon Library

Reference set of SaaS/app icons: original color, black silhouette, and white silhouette, exported at multiple sizes, all on a 1:1 square canvas.

## Structure

```
icons/<app-slug>/
  <app-slug>-color.(svg|png)   # vector or high-res raster master, original brand color(s)
  <app-slug>-black.(svg|png)   # solid black silhouette master
  <app-slug>-white.(svg|png)   # solid white silhouette master
  png/
    <app-slug>-color-<size>.png
    <app-slug>-black-<size>.png
    <app-slug>-white-<size>.png
```

Sizes: 4, 8, 16, 24, 32, 48, 64, 96, 128, 256, 512, 1024 (px).

## Sourcing

- Where available, icons come from [Simple Icons](https://simpleicons.org) (CC0) — vector, official brand hex color, single-color glyph on a transparent background.
- Where an app isn't in Simple Icons, the icon is pulled from the app's official App Store / Play Store listing (their real published app icon), then background-cleaned via flood-fill.

## Black/white silhouette method

Two-stage automated background removal, so the silhouette shows the actual glyph, not just a colored blob:

1. **Corner flood-fill**: remove the true image background (flood-filled from the four corners by color distance). Used as-is for the **color** master, so the original badge/container is preserved.
2. **Container peel** (only runs if step 1 leaves >50% of the canvas opaque — a sign the icon is a colored "badge" like Pipedrive's, not a glyph directly on transparent like Lark or Simple Icons): flood-fill inward again from the new background edge, using the color of that edge as reference, to strip away the badge's colored container and isolate just the glyph.
3. **Component cleanup**: keep only connected foreground regions ≥10% of the largest one, to drop thin anti-aliasing/edge-halo artifacts left over from step 2.

Result: **color** keeps the full original badge (container + glyph); **black/white** show just the glyph silhouette, whether or not the source icon has a colored container.

## Licensing note

All logos are trademarks of their respective companies. Simple Icons entries are CC0-licensed reproductions; App Store-sourced icons are the companies' own copyrighted assets pulled from their public listings. This library is for internal reference use — check each brand's guidelines before external/public use, especially before recoloring or altering their mark.
