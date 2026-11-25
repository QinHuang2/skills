#!/usr/bin/env python3
"""Preview, stream-render (ink -> color), and merge SRT whiteboard animation scenes using Python stdlib + FFmpeg."""

from __future__ import annotations

import argparse
import base64
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


def find_bin(name: str) -> str | None:
    found = shutil.which(name)
    if found:
        return found
    for prefix in ("/opt/homebrew/bin", "/usr/local/bin"):
        candidate = Path(prefix) / name
        if candidate.exists():
            return str(candidate)
    return None


def check_overlaps(regions: list[dict]) -> list[str]:
    ordered = sorted(regions, key=lambda r: int(r.get("sequence", 0)))
    errors: list[str] = []
    for i, prev in enumerate(ordered):
        if not prev.get("protected", True):
            continue
        ax0, ay0 = float(prev["x"]), float(prev["y"])
        ax1, ay1 = ax0 + float(prev["w"]), ay0 + float(prev["h"])
        prev_area = max(1.0, float(prev["w"]) * float(prev["h"]))
        for later in ordered[i + 1 :]:
            bx0, by0 = float(later["x"]), float(later["y"])
            bx1, by1 = bx0 + float(later["w"]), by0 + float(later["h"])
            ix = max(0.0, min(ax1, bx1) - max(ax0, bx0))
            iy = max(0.0, min(ay1, by1) - max(ay0, by0))
            inter = ix * iy
            if inter / prev_area > 0.05:
                errors.append(
                    f"Region '{later['id']}' (seq {later['sequence']}) overlaps protected region "
                    f"'{prev['id']}' (seq {prev['sequence']}) by {(inter / prev_area) * 100:.1f}%."
                )
    return errors


def cmd_preview(args: argparse.Namespace) -> None:
    ann = json.loads(args.annotation.read_text(encoding="utf-8"))
    overlap_errors = check_overlaps(ann.get("regions", []))

    template_path = Path(__file__).resolve().parent.parent / "assets" / "preview_template.html"
    tpl = template_path.read_text(encoding="utf-8")

    if args.embed_image and args.image.exists():
        mime = "image/svg+xml" if args.image.suffix.lower() == ".svg" else "image/png"
        b64 = base64.b64encode(args.image.read_bytes()).decode("ascii")
        img_src = f"data:{mime};base64,{b64}"
    else:
        img_src = os.path.relpath(args.image.resolve(), args.output.resolve().parent)

    html = (
        tpl.replace("__SCENE_ID__", str(ann.get("sceneId", "scene")))
        .replace("__IMAGE_SRC__", img_src)
        .replace("__ANNOTATION_JSON__", json.dumps(ann, ensure_ascii=False))
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(html, encoding="utf-8")

    report = {
        "preview_html": str(args.output),
        "regions_count": len(ann.get("regions", [])),
        "overlap_errors": overlap_errors,
        "passed": len(overlap_errors) == 0,
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))
    sys.exit(0 if report["passed"] else 1)


def cmd_render(args: argparse.Namespace) -> None:
    ffmpeg = find_bin("ffmpeg")
    if not ffmpeg:
        raise SystemExit("ffmpeg binary not found in PATH or /opt/homebrew/bin.")
    if not args.image.exists():
        raise SystemExit(f"Scene image not found: {args.image}")

    ann = json.loads(args.annotation.read_text(encoding="utf-8"))
    overlap_errors = check_overlaps(ann.get("regions", []))
    if overlap_errors and not args.ignore_overlaps:
        raise SystemExit(f"Protected region overlap detected: {overlap_errors}")

    w = int(ann.get("canvasWidth", 1920))
    h = int(ann.get("canvasHeight", 1080))
    fps = int(ann.get("fps", 30))
    dur_sec = max(1.0, round(float(ann.get("durationMs", 10000)) / 1000.0, 3))
    paper = str(ann.get("paperColor", "#F5EBD7")).lstrip("#")
    regions = sorted(ann.get("regions", []), key=lambda r: int(r.get("sequence", 0)))

    # Build FFmpeg filter_complex:
    # Base canvas = warm paper (#F5EBD7).
    # Source plate scaled to WxH; for each region i:
    #   1) Ink sketch layer (high-contrast monochrome linework on warm paper) revealed progressively via animated crop/overlay during [t0, t_ink]
    #   2) Full-color marker plate faded in smoothly over [t_ink, t1]
    filters: list[str] = [
        f"color=c=0x{paper}:s={w}x{h}:r={fps}:d={dur_sec}[bg0]",
        f"[0:v]scale={w}:{h},format=rgba[plate]",
    ]
    cur_bg = "bg0"

    pr = int(paper[0:2], 16)
    pg = int(paper[2:4], 16)
    pb = int(paper[4:6], 16)

    for idx, r in enumerate(regions, start=1):
        rx = max(0, min(w - 2, int(r["x"])))
        ry = max(0, min(h - 2, int(r["y"])))
        rw = max(2, min(w - rx, int(r["w"])))
        rh = max(2, min(h - ry, int(r["h"])))
        t0 = round(float(r["startMs"]) / 1000.0, 3)
        t1 = max(round(t0 + 0.25, 3), round(float(r["endMs"]) / 1000.0, 3))
        ink_ratio = max(0.35, min(0.85, float(r.get("inkRatio", 0.65))))
        t_ink = round(t0 + (t1 - t0) * ink_ratio, 3)
        ink_dur = max(0.12, round(t_ink - t0, 3))
        col_dur = max(0.12, round(t1 - t_ink, 3))
        sweep = r.get("sweep", "left-to-right")

        # Crop region into ink & color branches, tinting ink branch onto warm paper tone
        filters.append(
            f"[plate]crop={rw}:{rh}:{rx}:{ry},split=2[rc_raw_{idx}][ri_raw_{idx}]"
        )
        filters.append(
            f"[ri_raw_{idx}]hue=s=0,eq=contrast=1.35:brightness=0.03,"
            f"colorbalance=rs={(pr-200)/255.0:.2f}:gs={(pg-200)/255.0:.2f}:bs={(pb-200)/255.0:.2f}[ri_{idx}]"
        )

        # Create a warm-paper curtain wipe over the ink layer so strokes uncover cleanly along sweep direction
        filters.append(f"color=c=0x{paper}:s={rw}x{rh}:r={fps}:d={dur_sec}[mask_{idx}]")
        if sweep == "top-to-bottom":
            wipe_y = f"({ry})+({rh})*clip((t-{t0})/{ink_dur},0,1)"
            wipe_x = f"{rx}"
        else:
            wipe_x = f"({rx})+({rw})*clip((t-{t0})/{ink_dur},0,1)"
            wipe_y = f"{ry}"

        filters.append(
            f"[{cur_bg}][ri_{idx}]overlay=x={rx}:y={ry}:enable='gte(t,{t0})'[bg_ink_raw_{idx}]"
        )
        filters.append(
            f"[bg_ink_raw_{idx}][mask_{idx}]overlay=x='{wipe_x}':y='{wipe_y}':enable='between(t,{t0},{t_ink})'[bg_ink_{idx}]"
        )
        filters.append(
            f"[rc_raw_{idx}]format=rgba,fade=t=in:st={t_ink}:d={col_dur}:alpha=1[rc_{idx}]"
        )
        next_bg = f"bg_{idx}"
        filters.append(
            f"[bg_ink_{idx}][rc_{idx}]overlay=x={rx}:y={ry}:enable='gte(t,{t_ink})'[{next_bg}]"
        )
        cur_bg = next_bg

    filters.append(f"[{cur_bg}]format=yuv420p[vout]")
    filter_complex = ";".join(filters)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        ffmpeg,
        "-y",
        "-loop",
        "1",
        "-t",
        str(dur_sec),
        "-i",
        str(args.image),
        "-filter_complex",
        filter_complex,
        "-map",
        "[vout]",
        "-t",
        str(dur_sec),
        "-r",
        str(fps),
        "-c:v",
        "libx264",
        "-crf",
        "19",
        "-preset",
        "fast",
        str(args.output),
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    print(
        json.dumps(
            {
                "output": str(args.output),
                "scene_id": ann.get("sceneId"),
                "duration_sec": dur_sec,
                "regions_rendered": len(regions),
                "size_bytes": args.output.stat().st_size,
            },
            indent=2,
        )
    )


def cmd_merge(args: argparse.Namespace) -> None:
    ffmpeg = find_bin("ffmpeg")
    if not ffmpeg:
        raise SystemExit("ffmpeg binary not found in PATH or /opt/homebrew/bin.")
    for clip in args.inputs:
        if not clip.exists():
            raise SystemExit(f"Input scene clip missing: {clip}")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as tf:
        for clip in args.inputs:
            safe_p = str(clip.resolve()).replace("'", "'\\''")
            tf.write(f"file '{safe_p}'\n")
        list_path = Path(tf.name)

    try:
        cmd = [ffmpeg, "-y", "-f", "concat", "-safe", "0", "-i", str(list_path)]
        if args.audio and args.audio.exists():
            cmd.extend(["-i", str(args.audio), "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest"])
        else:
            cmd.extend(["-c", "copy"])
        cmd.append(str(args.output))
        subprocess.run(cmd, check=True, capture_output=True)
    finally:
        list_path.unlink(missing_ok=True)

    print(
        json.dumps(
            {
                "output": str(args.output),
                "clips_merged": len(args.inputs),
                "audio_muxed": bool(args.audio and args.audio.exists()),
                "size_bytes": args.output.stat().st_size,
            },
            indent=2,
        )
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="SRT Whiteboard Animator preview, stream-renderer, and merger.")
    sub = parser.add_subparsers(dest="command", required=True)

    p_prev = sub.add_parser("preview", help="Generate browser preview HTML and audit overlaps")
    p_prev.add_argument("--image", type=Path, required=True)
    p_prev.add_argument("--annotation", type=Path, required=True)
    p_prev.add_argument("--output", type=Path, required=True)
    p_prev.add_argument("--embed-image", action="store_true", help="Inline image as base64 data URI")
    p_prev.set_defaults(func=cmd_preview)

    p_ren = sub.add_parser("render", help="Render streaming ink->color whiteboard scene MP4")
    p_ren.add_argument("--image", type=Path, required=True)
    p_ren.add_argument("--annotation", type=Path, required=True)
    p_ren.add_argument("--output", type=Path, required=True)
    p_ren.add_argument("--ignore-overlaps", action="store_true")
    p_ren.set_defaults(func=cmd_render)

    p_mrg = sub.add_parser("merge", help="Concatenate rendered scene MP4 clips (+ optional voiceover)")
    p_mrg.add_argument("--inputs", type=Path, nargs="+", required=True)
    p_mrg.add_argument("--audio", type=Path, default=None)
    p_mrg.add_argument("--output", type=Path, required=True)
    p_mrg.set_defaults(func=cmd_merge)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
