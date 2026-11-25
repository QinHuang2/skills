#!/usr/bin/env python3
"""Validate 9:16 vertical video plan.json against platform UI safe zones, speaker face box, and pacing rules."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def boxes_overlap(a: dict, b: dict) -> bool:
    ax0, ay0, ax1, ay1 = float(a["x"]), float(a["y"]), float(a["x"]) + float(a["w"]), float(a["y"]) + float(a["h"])
    bx0, by0, bx1, by1 = float(b["x"]), float(b["y"]), float(b["x"]) + float(b["w"]), float(b["y"]) + float(b["h"])
    return ax0 < bx1 and ax1 > bx0 and ay0 < by1 and ay1 > by0


def check_safe_zone(name: str, box: dict, w: int, h: int, face_box: dict | None, check_face: bool = True) -> list[str]:
    errs: list[str] = []
    x, y, bw, bh = float(box["x"]), float(box["y"]), float(box["w"]), float(box["h"])
    x1, y1 = x + bw, y + bh

    top_limit = h * (180.0 / 1920.0)
    bot_limit = h * (1580.0 / 1920.0)
    rail_x = w * (900.0 / 1080.0)
    rail_y0 = h * (820.0 / 1920.0)
    rail_y1 = h * (1620.0 / 1920.0)

    if x < 24 or x1 > w - 24:
        errs.append(f"{name} exceeds horizontal canvas margin ({x:.0f}..{x1:.0f} on {w}px width).")
    if y < top_limit:
        errs.append(f"{name} intrudes into top platform UI bar (y={y:.0f} < {top_limit:.0f}).")
    if y1 > bot_limit:
        errs.append(f"{name} intrudes into bottom platform caption/scrub chrome (y1={y1:.0f} > {bot_limit:.0f}).")
    if x1 > rail_x and y1 > rail_y0 and y < rail_y1:
        errs.append(f"{name} collides with right-rail engagement buttons (x1={x1:.0f} > {rail_x:.0f} in y={rail_y0:.0f}..{rail_y1:.0f}).")
    if check_face and face_box and boxes_overlap(box, face_box):
        errs.append(f"{name} overlaps protected speakerFaceBox ({face_box}).")
    return errs


def validate_plan(plan: dict) -> dict:
    errors: list[str] = []
    warnings: list[str] = []

    canvas = plan.get("canvas", {})
    w = int(canvas.get("width", 1080))
    h = int(canvas.get("height", 1920))
    dur = float(plan.get("duration", 0.0))
    if round(w / max(1, h), 3) != round(9 / 16, 3):
        warnings.append(f"Canvas {w}x{h} is not standard 9:16 vertical aspect ratio.")
    if dur <= 0:
        errors.append("Plan 'duration' must be > 0 seconds.")

    face_box = plan.get("speakerFaceBox", {"x": 300, "y": 420, "w": 480, "h": 520})

    hook = plan.get("hook")
    if not hook:
        warnings.append("No 'hook' block defined for the critical 0-3s retention window.")
    else:
        if float(hook.get("start", 0.0)) > 0.25:
            warnings.append(f"Hook starts late at {hook.get('start')}s (recommend <= 0.2s).")
        if "box" in hook:
            errors.extend(check_safe_zone("hook.box", hook["box"], w, h, face_box, check_face=True))

    cuts = sorted(plan.get("cuts", []), key=lambda c: float(c.get("start", 0.0)))
    for idx, c in enumerate(cuts):
        st, en = float(c["start"]), float(c["end"])
        zm = float(c.get("zoom", 1.0))
        if en <= st:
            errors.append(f"cuts[{idx}] has non-positive duration ({st} -> {en}).")
        if en - st > 7.5:
            warnings.append(f"cuts[{idx}] holds static framing for {en - st:.1f}s (> 7.5s); consider adding a punch-in or card.")
        if zm < 1.0 or zm > 1.30:
            warnings.append(f"cuts[{idx}] zoom={zm} outside recommended [1.0, 1.18] talking-head range.")
        if idx > 0 and abs(st - float(cuts[idx - 1]["end"])) > 0.05:
            errors.append(f"Gap or overlap between cuts[{idx-1}] and cuts[{idx}].")

    for i, card in enumerate(plan.get("cards", [])):
        cid = card.get("id", f"card_{i}")
        if float(card["end"]) <= float(card["start"]):
            errors.append(f"Card '{cid}' has invalid timing.")
        if "box" in card:
            # Cutaway cards may intentionally cover speaker when broll/full-card, otherwise check face
            is_cutaway = bool(card.get("cutaway", False))
            errors.extend(check_safe_zone(f"card '{cid}'", card["box"], w, h, face_box, check_face=not is_cutaway))

    captions = sorted(plan.get("captions", []), key=lambda c: float(c.get("start", 0.0)))
    for i, cap in enumerate(captions):
        st, en = float(cap["start"]), float(cap["end"])
        txt = str(cap.get("text", "")).strip()
        if en <= st:
            errors.append(f"captions[{i}] has non-positive duration ({st} -> {en}).")
        if i > 0 and st < float(captions[i - 1]["end"]) - 0.02:
            errors.append(f"captions[{i}] overlaps previous caption ({captions[i-1]['end']}s > {st}s).")
        if len(txt.split()) > 8 or len(txt) > 28:
            warnings.append(f"captions[{i}] ('{txt[:24]}...') is dense for 9:16; split into 2-5 word beats.")
        if "box" in cap:
            errors.extend(check_safe_zone(f"captions[{i}]", cap["box"], w, h, face_box, check_face=True))

    return {
        "passed": len(errors) == 0,
        "canvas": f"{w}x{h}",
        "duration_sec": dur,
        "cuts_count": len(cuts),
        "cards_count": len(plan.get("cards", [])),
        "captions_count": len(captions),
        "errors": errors,
        "warnings": warnings,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate vertical short plan.json safe zones and timing.")
    parser.add_argument("--plan", type=Path, required=True, help="Path to plan.json")
    args = parser.parse_args()

    if not args.plan.exists():
        raise SystemExit(f"Plan file not found: {args.plan}")

    plan = json.loads(args.plan.read_text(encoding="utf-8"))
    report = validate_plan(plan)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    sys.exit(0 if report["passed"] else 1)


if __name__ == "__main__":
    main()
