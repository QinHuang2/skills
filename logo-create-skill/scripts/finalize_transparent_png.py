#!/usr/bin/env python3
"""Remove baked backgrounds from generated title art and fit to a PNG canvas."""

from __future__ import annotations

import argparse
from collections import deque
from pathlib import Path

import numpy as np
from PIL import Image


def parse_hex_color(value: str) -> tuple[int, int, int]:
    value = value.strip().lstrip("#")
    if len(value) != 6:
        raise argparse.ArgumentTypeError("Expected a 6-digit hex color, e.g. #00ff00")
    return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4))


def checker_candidate(rgb: np.ndarray) -> np.ndarray:
    rgb_i = rgb.astype(np.int16)
    mx = rgb_i.max(axis=2)
    mn = rgb_i.min(axis=2)
    saturation = mx - mn
    broad = (mx >= 218) & (mn >= 205) & (saturation <= 22)
    strict = (mx >= 236) & (mn >= 226) & (saturation <= 10)
    return broad | strict


def key_candidate(rgb: np.ndarray, key: tuple[int, int, int], tolerance: int) -> np.ndarray:
    key_arr = np.array(key, dtype=np.int16)
    distance = np.abs(rgb.astype(np.int16) - key_arr).max(axis=2)
    return distance <= tolerance


def connected_to_border(candidate: np.ndarray) -> np.ndarray:
    h, w = candidate.shape
    mask = np.zeros((h, w), dtype=bool)
    q: deque[tuple[int, int]] = deque()

    for x in range(w):
        for y in (0, h - 1):
            if candidate[y, x] and not mask[y, x]:
                mask[y, x] = True
                q.append((y, x))
    for y in range(h):
        for x in (0, w - 1):
            if candidate[y, x] and not mask[y, x]:
                mask[y, x] = True
                q.append((y, x))

    while q:
        y, x = q.popleft()
        for ny, nx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)):
            if 0 <= ny < h and 0 <= nx < w and candidate[ny, nx] and not mask[ny, nx]:
                mask[ny, nx] = True
                q.append((ny, nx))
    return mask


def build_alpha(rgb: np.ndarray, args: argparse.Namespace) -> np.ndarray:
    h, w, _ = rgb.shape
    remove = np.zeros((h, w), dtype=bool)

    if args.remove_checkerboard:
        candidate = checker_candidate(rgb)
        remove |= connected_to_border(candidate)
        remove |= candidate if args.clear_internal_checkerboard else False

    if args.key_color is not None:
        candidate = key_candidate(rgb, args.key_color, args.key_tolerance)
        remove |= connected_to_border(candidate)
        if args.clear_internal_key:
            remove |= candidate

    return np.where(remove, 0, 255).astype(np.uint8)


def process(args: argparse.Namespace) -> None:
    image = Image.open(args.input).convert("RGBA")
    rgba = np.asarray(image).copy()

    generated_alpha = build_alpha(rgba[:, :, :3], args)
    if args.preserve_existing_alpha:
        rgba[:, :, 3] = np.minimum(rgba[:, :, 3], generated_alpha)
    else:
        rgba[:, :, 3] = generated_alpha

    out = Image.fromarray(rgba)
    if args.width and args.height:
        out = out.resize((args.width, args.height), Image.Resampling.LANCZOS)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    out.save(args.output)

    alpha = np.asarray(out.getchannel("A"))
    corners = [
        alpha[0, 0],
        alpha[0, out.width - 1],
        alpha[out.height - 1, 0],
        alpha[out.height - 1, out.width - 1],
    ]
    print(
        {
            "file": str(args.output),
            "width": out.width,
            "height": out.height,
            "has_alpha": out.mode == "RGBA",
            "transparent_corners": sum(int(v == 0) for v in corners),
            "opaque_pixels": int((alpha > 0).sum()),
        }
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--width", type=int, default=1360)
    parser.add_argument("--height", type=int, default=560)
    parser.add_argument("--remove-checkerboard", action="store_true")
    parser.add_argument("--clear-internal-checkerboard", action="store_true", default=True)
    parser.add_argument("--key-color", type=parse_hex_color)
    parser.add_argument("--key-tolerance", type=int, default=16)
    parser.add_argument("--clear-internal-key", action="store_true")
    parser.add_argument("--preserve-existing-alpha", action="store_true")
    args = parser.parse_args()

    if not args.remove_checkerboard and args.key_color is None:
        raise SystemExit("Specify --remove-checkerboard or --key-color.")
    process(args)


if __name__ == "__main__":
    main()
