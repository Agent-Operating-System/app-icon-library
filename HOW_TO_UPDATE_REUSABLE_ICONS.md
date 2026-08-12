# How to Update a Reusable Action Icon

This covers the **reusable action icon system** (e.g. "Find", "Retrieve", "Send Message" —
the shared action icons used across multiple apps like Notion, Google Drive, WhatsApp,
ChatDaddy), NOT the individual third-party app icons (that's a separate, simpler flow —
see `README.md`).

There are two Notion databases involved:

- **Reusable Icon DB** — the 26 master action icons (Find, Retrieve, Update/Edit, etc).
  Each one has 4 SVG variants (Solid Black, Solid White, Outline Black, Outline White)
  uploaded directly as Notion file attachments, plus a PNG page icon.
- **App Icon DB** (`18 🎨 Brand Assets / Media Library`) — one page per app (Notion,
  Google Drive, Google Calendar, WhatsApp, ChatDaddy). Each app page has its own 5-variant
  icon set (unrelated to this doc) PLUS a **"🧩 Reusable Action Icon Mashups"** section at
  the bottom — one composited image per action that app supports (action icon + that
  app's logo badge, bottom-left corner).

**The key thing to understand:** changing a reusable action's icon means regenerating
that icon's 4 variants AND every mashup image that uses it (one per app that shares that
action), then updating both the Reusable Icon page and every affected App Icon page.

---

## Part 1 — Export the new icon from Lordicon

### 1.1 Log in

1. Go to https://lordicon.com/login
2. Email: `info@chatdaddy.tech`
3. Password: **not stored in this repo** — get it from Shivonne or the team password
   manager. Do not add it to any file that gets committed.

### 1.2 Find the icon

1. Click **Icons** in the top nav (or go straight to
   `https://lordicon.com/icons/system/outline`).
2. Click the **style dropdown** (top-left, shows something like "All Styles" or "System
   Outline"). A panel opens with columns: **Wired**, **System**, **Doodle**.
3. Under **System**, click **Outline** (thin line icons — this is what we use for all
   reusable action icons) or **Solid** (filled icons — used for the second pair of
   variants).
4. Type a search term in the search box (e.g. `inbox`, `plus`, `chat`). Lordicon shows
   a grid of matching icon cards below.

   **Important:** search terms don't always match the action name exactly. If nothing
   good comes up, try synonyms (e.g. "hierarchy" found nothing, but "levels" found
   `sliders-horizontal`, which was close enough). Check the "Search by related tags"
   chips under the search box for alternative wording.

   **Important:** the same icon's numeric ID is *not* guaranteed to match between
   Outline and Solid styles for every icon (it happened to line up for some icons by
   coincidence, but broke for others — e.g. `system-outline-361-inbox` was NOT the same
   icon as `system-solid-361-inbox`, which turned out to be `info-circle`). **Always
   search fresh in each style** — don't construct a Solid URL by guessing from the
   Outline URL.

5. Click the icon card you want. It loads in the right-hand preview panel.

### 1.3 Set format to SVG

1. In the right panel, find the **format dropdown** (starts showing "GIF").
2. Click it — a list opens, grouped into **Animated** (Lottie, GIF, MP4, WebP, APNG,
   HTML) and **Static** (SVG, PNG) and **Source** (AEP, MOGRT).
3. Click **SVG** under the Static group.

   Once you've done this for the first icon in a session, Lordicon remembers "SVG" as
   your format for the rest of that browser session — you don't need to reset it for
   every icon after the first, but it's safe to check it's still on SVG.

### 1.4 Set the color and export

1. Below the format dropdown, find **Colors** — a color swatch + hex text field
   (defaults to something like `121331`).
2. Click the hex field, select all, type `000000` for black. Press Enter/Tab.
3. Click the green **Export** button. A file downloads.
4. **Verify the download is actually correct before moving on** — this pipeline has bit
   us twice:
   - Sometimes the exported file is a `.svg`-named file that's actually a GIF binary.
     Run `file <filename>` in Terminal — it should say `SVG Scalable Vector Graphics
     image`, not `GIF image data`.
   - Sometimes the color change doesn't take (exports the previous color). Open the SVG
     in a text editor and check the `fill="#000"` / `stroke="#000"` value matches what
     you set.
5. Repeat step 2-4 with `FFFFFF` for the white variant.
6. Repeat the whole process (1.2–1.5) once for **Outline** style and once for **Solid**
   style — you need 4 files total per action: Outline Black, Outline White, Solid
   Black, Solid White.

---

## Part 2 — Update the Reusable Icon's Notion page

1. Open the action's page in the **Reusable Icon** database.
2. In the page body, find the 4 headings: `### Solid Black`, `### Solid White`,
   `### Outline Black`, `### Outline White`. Replace the image under each heading with
   the matching new file (drag-and-drop the new SVG onto the old image block, or delete
   the old image block and insert a new one).
   - `Solid Black` / `Outline Black`: plain image, no wrapper, no caption.
   - `Solid White` / `Outline White`: wrapped in a **gray background callout** (no icon
     on the callout itself — that was intentionally removed everywhere). Keep the image
     inside the existing callout block rather than deleting the callout.
3. **Page icon** (small icon shown in the sidebar/tab): Notion can't render a page icon
   set from a pure-stroke SVG (the Outline style has no fill, and page icons need one).
   Convert the Outline Black SVG to a PNG first (any SVG→PNG tool, e.g. opening it in a
   browser and screenshotting at a decent size like 256×256, or a proper conversion
   script), then set that PNG as the page icon.
4. If the icon's **image size looks tiny** in the page body: this happens because raw
   SVGs have a tiny native pixel size (usually 24×24) and Notion renders embedded images
   at native size. Convert to a big PNG (256×256) first, same as the page-icon step, and
   embed the PNG instead of the raw SVG.

---

## Part 3 — Regenerate affected mashups & update App Icon pages

Changing a reusable action's icon means every app that shares that action needs its
mashup image (action icon + that app's badge) regenerated.

### 3.1 Find which apps are affected

In the Reusable Icon database, open the action's row and check the **"Shared By
Apps"** property (this is a relation, linking to rows in the App Icon database). Every
app listed there needs its mashup regenerated.

### 3.2 Regenerate the mashup images

The compositing script lives in this repo (added when the mashup system was first
built):

```
scripts/build_chatdaddy.py   # reference example of the icon-generation pattern
```

The actual mashup compositor (action icon + circular app badge, white ring, bottom-left)
follows this logic — recreate or reuse a script with the same structure:

1. Download the app's badge from
   `icons/<app-slug>/png/<app-slug>-color-256.png` in this repo (or the raw GitHub URL).
2. Take the new Outline Black PNG (256×256) for the action.
3. Composite: 512×512 canvas, light-gray rounded-square card (40px margin, 80px corner
   radius), action icon centered at 50% canvas scale, app badge as a circle (34% canvas
   diameter) with a 10px white ring, positioned bottom-left, overlapping the card's
   corner by about a third.
4. **Give the badge ~16% inner padding within its circle** before cropping to a circle —
   without this, logos that fill their own square canvas edge-to-edge (Google Drive's
   triangle, Notion's cube) get their corners/points clipped by the circular mask.
5. Save as `icons/_reusable-mashups/<app-slug>/<app-slug>-<action-slug>.png` (slug =
   lowercase, spaces and `/` replaced with `-`, e.g. "Query / List Many" →
   `query-list-many`).

### 3.3 Push to GitHub

```
git add icons/_reusable-mashups/<app-slug>/
git commit -m "fix: regenerate <app> x <action> mashup with updated action icon"
git push origin main
```

Verify the raw URL resolves before moving on:

```
curl -I "https://raw.githubusercontent.com/Agent-Operating-System/app-icon-library/main/icons/_reusable-mashups/<app-slug>/<filename>.png"
```

Should return `200`. GitHub's CDN can take a minute to catch up after a push — if you
get a 404 immediately after pushing, wait ~60 seconds and retry before assuming
something's wrong.

### 3.4 Update the App Icon page(s) in Notion

For each affected app's page in the App Icon database:

1. Scroll to the **"🧩 Reusable Action Icon Mashups"** section at the bottom of the page.
2. Find the specific action's image in that grid.
3. Replace it with the newly regenerated mashup (same raw GitHub URL pattern, just the
   image content changed — if using an `image` block with an external URL, Notion may
   cache the old image; if it doesn't refresh, append `?v=2` (or increment) to the URL
   as a cache-buster, per the caching note in `README.md`).
4. Do not touch anything else on the page — the 5-variant color/black/white/outline
   preview section above the mashup grid is a separate, unrelated system for that app's
   own icon and should be left alone.

---

### 3.5 Regenerate the size ladder

Each reusable action icon also has a full size ladder (2, 4, 8, 12, 16, 24, 32, 48, 64,
96, 128, 200 px) for all 4 variants, stored in GitHub — same pattern as the mashups and
the third-party app icons, so Notion only needs to show one preview size while the real
range lives here. When you change an action's master SVG, regenerate its ladder:

```
python3 scripts/build_reusable_action_sizes.py
```

This reads the master SVGs from the local path hardcoded at the top of the script
(`SRC_ROOT`, currently Shivonne's machine — update this if the source-of-truth location
changes) and writes to `icons/_reusable-actions/<action-slug>/png/`. It regenerates
*all* 26 actions every run (not just the one you changed) — safe to run in full each
time since it's a few seconds per action, but if you only changed one action you can
comment out the others in the `ACTIONS` dict to save time.

**Known limit, not a bug:** the 2px and 4px renders of any Outline-style icon are
functionally just noise (the stroke is too thin to survive at that pixel count) — this
matches the same documented limitation as the third-party app icons' outline variants
(see "Line/outline method" above: "holds up down to ~16px"). They're still generated for
size-ladder consistency, just don't expect them to be visually legible.

After regenerating, `git add`, commit, push, then follow 3.4's cache-busting note if the
Notion preview doesn't refresh.

---

## Quick reference: file/folder map

```
icons/<app-slug>/                          # per-app icon set (existing system, unrelated to reusable icons)
icons/_reusable-mashups/<app-slug>/        # action-icon x app-badge composites, one per (app, action) pair
icons/_reusable-actions/<action-slug>/png/ # full 2-200px size ladder per reusable action, 4 variants each
```

The reusable action icons' master SVGs (Solid/Outline × Black/White) still live only as
file attachments directly on each action's Reusable Icon Notion page — that's the
source of truth. This repo only hosts the *derived* renders (size ladder + mashups),
which need a stable public URL for Notion to embed. If you update a master SVG on the
Notion page, you must also re-run `build_reusable_action_sizes.py` (3.5) and the mashup
regeneration (3.2) — the GitHub copies don't auto-sync from Notion.
