#!/usr/bin/env python3
"""Export cat-themed X artwork to exact dimensions without stretching.

Requires Pillow. Input must already be composed close to target aspect ratio.
A large mismatch is refused rather than silently cutting off a face/action.
"""
import argparse
from pathlib import Path
from PIL import Image, ImageOps

SIZES = {"cover": (2000, 800), "inline": (1920, 1080)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--type", choices=SIZES, required=True)
    parser.add_argument("--align", choices=("center", "left", "right", "top", "bottom"), default="center")
    parser.add_argument("--max-aspect-error", type=float, default=0.08,
                        help="Maximum relative aspect ratio discrepancy before refusing crop (default: 0.08)")
    args = parser.parse_args()

    if not args.input.is_file():
        parser.error(f"File not found: {args.input}")
    target = SIZES[args.type]
    with Image.open(args.input) as original:
        image = ImageOps.exif_transpose(original).convert("RGB")
    src_ratio = image.width / image.height
    dst_ratio = target[0] / target[1]
    rel_error = abs(src_ratio / dst_ratio - 1)
    if rel_error > args.max_aspect_error:
        parser.error(f"Source aspect {src_ratio:.4f}, target {dst_ratio:.4f}; "
                     f"mismatch {rel_error:.1%} is too large. Re-compose or outpaint; do not blind-crop.")

    centers = {"center": (0.5, 0.5), "left": (0.0, 0.5), "right": (1.0, 0.5),
               "top": (0.5, 0.0), "bottom": (0.5, 1.0)}
    output = ImageOps.fit(image, target, method=Image.Resampling.LANCZOS,
                          centering=centers[args.align])
    args.output.parent.mkdir(parents=True, exist_ok=True)
    output.save(args.output, format="PNG", optimize=True)
    with Image.open(args.output) as check:
        actual = check.size
        assert actual == target, f"Unexpected size: {actual}"
        assert check.format == "PNG", f"Unexpected format: {check.format}"
    print(f"VERIFIED: {args.output} is {actual[0]}x{actual[1]} PNG")
    print("Visual QA still required: review subject face, eyes, limbs, text and safe margins.")


if __name__ == "__main__":
    main()
