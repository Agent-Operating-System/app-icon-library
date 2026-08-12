#!/usr/bin/env python3
"""Generate a full size ladder (2-200px) for every reusable action icon's 4 variants,
rasterized from the master SVGs that live locally on Shivonne's machine (these SVGs
are not themselves committed to this repo - only the derived PNG size ladder is,
same pattern as the mashups: source of truth for the SVG is the Reusable Icon Notion
page's file attachment, GitHub just hosts the size-ladder renders for embedding)."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from rasterize import rasterize_svg

SIZES = [2, 4, 8, 12, 16, 24, 32, 48, 64, 96, 128, 200]

SRC_ROOT = "/Users/shivonne/Claude Code/app-icon-library/lordicon-system-line-final"
OUT_ROOT = "/tmp/app-icon-library-repo/icons/_reusable-actions"

# variant folder name in source -> output variant name
VARIANTS = {
    "black": "outline-black",
    "white": "outline-white",
    "solid-black": "solid-black",
    "solid-white": "solid-white",
}

# ID -> slug (matches the Notion "Icon Master" title, kebab-cased)
ACTIONS = {
    "A01": "add-content-block",
    "A02": "add-comment",
    "A03": "create-page-record-contact",
    "A04": "create-folder-drive",
    "A05": "create-file",
    "A06": "create-calendar-event",
    "A07": "quick-add-event",
    "A08": "update-edit",
    "A09": "restore",
    "A10": "archive-delete-cancel",
    "A11": "upload-replace-file",
    "A12": "copy-duplicate",
    "A13": "export",
    "A14": "move",
    "A15": "share-add-permission",
    "A16": "remove-permission-access",
    "A17": "attendee-management",
    "A18": "find",
    "A19": "query-list-many",
    "A20": "retrieve",
    "A21": "get-children-hierarchy",
    "A22": "get-comments",
    "A23": "get-permissions-availability",
    "A25": "api-request",
    "A26": "send-message",
    "A27": "send-structured-message",
}

total = 0
errors = []
for action_id, slug in ACTIONS.items():
    out_dir = f"{OUT_ROOT}/{slug}/png"
    os.makedirs(out_dir, exist_ok=True)
    for src_folder, variant_name in VARIANTS.items():
        svg_path = f"{SRC_ROOT}/{src_folder}/{action_id}.svg"
        if not os.path.exists(svg_path):
            errors.append(f"MISSING SOURCE: {svg_path}")
            continue
        svg_text = open(svg_path).read()
        for size in SIZES:
            try:
                img = rasterize_svg(svg_text, size)
                img.save(f"{out_dir}/{slug}-{variant_name}-{size}.png")
                total += 1
            except Exception as e:
                errors.append(f"{action_id} {variant_name} {size}px: {e}")
    print(f"{action_id} ({slug}): done", flush=True)

print(f"\n{'='*60}")
print(f"Generated {total} PNGs across {len(ACTIONS)} actions x {len(VARIANTS)} variants x {len(SIZES)} sizes")
if errors:
    print(f"\nERRORS ({len(errors)}):")
    for e in errors:
        print(f"  {e}")
