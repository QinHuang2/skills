#!/usr/bin/env python3
"""Audit isometric HTML/SVG figures for viewBox bounds, degenerate polygons, text overlaps, and control bindings."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
import xml.etree.ElementTree as ET


def extract_svg_block(text: str) -> str | None:
    m = re.search(r"<svg\b.*?</svg>", text, re.DOTALL | re.IGNORECASE)
    return m.group(0) if m else None


def parse_points(pts_str: str) -> list[tuple[float, float]]:
    nums = [float(x) for x in re.findall(r"-?\d+(?:\.\d+)?", pts_str)]
    return [(nums[i], nums[i + 1]) for i in range(0, len(nums) - 1, 2)]


def polygon_area(pts: list[tuple[float, float]]) -> float:
    if len(pts) < 3:
        return 0.0
    acc = 0.0
    for i in range(len(pts)):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % len(pts)]
        acc += x1 * y2 - x2 * y1
    return abs(acc) * 0.5


def local_tag(tag: str) -> str:
    return tag.split("}")[-1].lower()


def audit_figure(path: Path) -> dict:
    raw = path.read_text(encoding="utf-8")
    errors: list[str] = []
    warnings: list[str] = []

    svg_str = raw if path.suffix.lower() == ".svg" else extract_svg_block(raw)
    if not svg_str:
        return {
            "file": str(path),
            "passed": False,
            "errors": ["No <svg> element found in figure."],
            "warnings": [],
        }

    try:
        root = ET.fromstring(svg_str)
    except ET.ParseError as exc:
        return {
            "file": str(path),
            "passed": False,
            "errors": [f"SVG XML parse error: {exc}"],
            "warnings": [],
        }

    vb = root.attrib.get("viewBox")
    if not vb:
        errors.append("SVG missing 'viewBox' attribute.")
        vb_x, vb_y, vb_w, vb_h = 0.0, 0.0, 1120.0, 680.0
    else:
        vb_vals = [float(v) for v in re.findall(r"-?\d+(?:\.\d+)?", vb)]
        if len(vb_vals) != 4:
            errors.append(f"Malformed viewBox: '{vb}'")
            vb_x, vb_y, vb_w, vb_h = 0.0, 0.0, 1120.0, 680.0
        else:
            vb_x, vb_y, vb_w, vb_h = vb_vals

    poly_count = 0
    degenerate_polys = 0
    out_of_bounds_pts = 0
    text_boxes: list[tuple[str, float, float, float, float]] = []

    for elem in root.iter():
        t = local_tag(elem.tag)
        if t == "polygon":
            poly_count += 1
            pts = parse_points(elem.attrib.get("points", ""))
            if len(pts) < 3 or polygon_area(pts) < 0.5:
                degenerate_polys += 1
            for px, py in pts:
                if px < vb_x - 20 or px > vb_x + vb_w + 20 or py < vb_y - 20 or py > vb_y + vb_h + 20:
                    out_of_bounds_pts += 1

        elif t == "path":
            d = elem.attrib.get("d", "").strip()
            if not d:
                errors.append("Empty <path d=\"\"> element found.")

        elif t == "text":
            label = "".join(elem.itertext()).strip()
            if not label:
                continue
            tx = float(elem.attrib.get("x", "0"))
            ty = float(elem.attrib.get("y", "0"))
            fs = float(re.sub(r"[^0-9.]", "", elem.attrib.get("font-size", "12")) or "12")
            anchor = elem.attrib.get("text-anchor", "start")
            est_w = len(label) * fs * 0.58
            x0 = tx - est_w if anchor == "end" else (tx - est_w * 0.5 if anchor == "middle" else tx)
            y0 = ty - fs
            text_boxes.append((label, x0, y0, x0 + est_w, ty + 2.0))
            if x0 < vb_x + 4 or (x0 + est_w) > vb_x + vb_w - 4 or y0 < vb_y + 4 or ty > vb_y + vb_h - 4:
                warnings.append(f"Callout text '{label}' sits dangerously close to or outside viewBox edge.")

    if degenerate_polys > 0:
        errors.append(f"{degenerate_polys} degenerate/zero-area <polygon> element(s) detected.")
    if out_of_bounds_pts > 0:
        warnings.append(f"{out_of_bounds_pts} polygon vertex coordinate(s) extend beyond SVG viewBox.")

    overlaps: list[str] = []
    for i in range(len(text_boxes)):
        l1, ax0, ay0, ax1, ay1 = text_boxes[i]
        for j in range(i + 1, len(text_boxes)):
            l2, bx0, by0, bx1, by1 = text_boxes[j]
            if ax0 < bx1 and ax1 > bx0 and ay0 < by1 and ay1 > by0:
                overlaps.append(f"'{l1}' <-> '{l2}'")
    if overlaps:
        errors.append(f"Overlapping SVG <text> labels detected: {overlaps}")

    controls_count = len(re.findall(r"<input\b", raw, re.IGNORECASE))
    if path.suffix.lower() == ".html" and controls_count == 0:
        warnings.append("Interactive HTML figure has zero <input> controls; consider adding live parameter sliders.")

    return {
        "file": str(path),
        "passed": len(errors) == 0,
        "polygons_checked": poly_count,
        "labels_checked": len(text_boxes),
        "interactive_inputs": controls_count,
        "errors": errors,
        "warnings": warnings,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit isometric SVG/HTML anatomy figures.")
    parser.add_argument("--input", type=Path, required=True, help="Path to .html or .svg figure")
    args = parser.parse_args()

    if not args.input.exists():
        raise SystemExit(f"Input file not found: {args.input}")

    report = audit_figure(args.input)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    sys.exit(0 if report["passed"] else 1)


if __name__ == "__main__":
    main()
