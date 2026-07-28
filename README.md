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

- **Glyph-on-transparent icons** (e.g. Simple Icons, Lark): silhouette is the actual mark shape, filled solid black or white.
- **Badge-style icons** (colored container + glyph, e.g. Pipedrive): the automated pipeline can't cleanly separate the glyph from its container, so the silhouette is the full badge shape (solid rounded-square) rather than just the inner glyph. This is an accepted tradeoff to keep the whole set scriptable across 100 apps rather than hand-fixing each badge-style icon.

## Licensing note

All logos are trademarks of their respective companies. Simple Icons entries are CC0-licensed reproductions; App Store-sourced icons are the companies' own copyrighted assets pulled from their public listings. This library is for internal reference use — check each brand's guidelines before external/public use, especially before recoloring or altering their mark.
