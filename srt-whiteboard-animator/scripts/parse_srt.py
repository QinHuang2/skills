#!/usr/bin/env python3
"""Parse .srt subtitle files into balanced 25-35s whiteboard storyboard scenes and starter annotation.json files."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

TIME_RE = re.compile(
    r"(\d{1,2}):(\d{2}):(\d{2})[,.](\d{3})\s*-->\s*(\d{1,2}):(\d{2}):(\d{2})[,.](\d{3})"
)

GRID_SLOTS_4 = [
    (110, 110, 780, 390),
    (1030, 110, 780, 390),
    (110, 580, 780, 390),
    (1030, 580, 780, 390),
]


def to_ms(h: str, m: str, s: str, ms: str) -> int:
    return ((int(h) * 3600 + int(m) * 60 + int(s)) * 1000) + int(ms)


def parse_srt(srt_text: str) -> list[dict]:
    cleaned = srt_text.lstrip("\ufeff").replace("\r\n", "\n")
    blocks = re.split(r"\n\s*\n", cleaned.strip())
    cues: list[dict] = []
    for block in blocks:
        lines = [ln.strip() for ln in block.splitlines() if ln.strip()]
        if not lines:
            continue
        time_idx = next((i for i, ln in enumerate(lines) if TIME_RE.search(ln)), None)
        if time_idx is None:
            continue
        m = TIME_RE.search(lines[time_idx])
        assert m is not None
        start_ms = to_ms(*m.groups()[:4])
        end_ms = to_ms(*m.groups()[4:])
        text = " ".join(lines[time_idx + 1 :]).strip()
        text = re.sub(r"<[^>]+>", "", text)
        if text and end_ms > start_ms:
            cues.append({"index": len(cues) + 1, "startMs": start_ms, "endMs": end_ms, "text": text})
    return cues


def chunk_scenes(cues: list[dict], target_sec: float) -> list[dict]:
    if not cues:
        return []
    target_ms = int(target_sec * 1000)
    max_ms = int(target_sec * 1350)
    scenes: list[dict] = []
    bucket: list[dict] = []

    for cue in cues:
        bucket.append(cue)
        span = bucket[-1]["endMs"] - bucket[0]["startMs"]
        ends_sentence = bool(re.search(r"[.!?。！？…]$", cue["text"]))
        if (span >= target_ms and ends_sentence) or span >= max_ms:
            scenes.append(make_scene(len(scenes) + 1, bucket))
            bucket = []

    if bucket:
        if scenes and (bucket[-1]["endMs"] - bucket[0]["startMs"]) < 9000:
            merged_cues = scenes[-1]["cues"] + bucket
            scenes[-1] = make_scene(len(scenes), merged_cues)
        else:
            scenes.append(make_scene(len(scenes) + 1, bucket))
    return scenes


def make_scene(num: int, cues: list[dict]) -> dict:
    g_start = cues[0]["startMs"]
    g_end = cues[-1]["endMs"]
    return {
        "sceneId": f"scene_{num:02d}",
        "globalStartMs": g_start,
        "globalEndMs": g_end,
        "durationMs": g_end - g_start,
        "cueCount": len(cues),
        "summaryText": " ".join(c["text"] for c in cues),
        "cues": cues,
    }


def build_starter_annotation(scene: dict, width: int = 1920, height: int = 1080) -> dict:
    cues = scene["cues"]
    g0 = scene["globalStartMs"]
    # Group cues into up to 4 clean non-overlapping visual islands per scene
    n_islands = min(4, max(1, len(cues)))
    groups: list[list[dict]] = [[] for _ in range(n_islands)]
    for idx, c in enumerate(cues):
        slot = min(n_islands - 1, (idx * n_islands) // len(cues))
        groups[slot].append(c)

    regions = []
    for i, grp in enumerate(groups):
        if not grp:
            continue
        gx, gy, gw, gh = GRID_SLOTS_4[i]
        sx = int(gx * width / 1920)
        sy = int(gy * height / 1080)
        sw = int(gw * width / 1920)
        sh = int(gh * height / 1080)
        regions.append(
            {
                "id": f"r{i+1}",
                "sequence": i + 1,
                "subtitleText": " ".join(x["text"] for x in grp),
                "startMs": max(0, grp[0]["startMs"] - g0),
                "endMs": max(100, grp[-1]["endMs"] - g0),
                "x": sx,
                "y": sy,
                "w": sw,
                "h": sh,
                "sweep": "left-to-right",
                "inkRatio": 0.65,
                "protected": True,
            }
        )

    return {
        "sceneId": scene["sceneId"],
        "canvasWidth": width,
        "canvasHeight": height,
        "paperColor": "#F5EBD7",
        "fps": 30,
        "durationMs": max(1000, scene["durationMs"]),
        "globalStartMs": g0,
        "regions": regions,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Parse .srt into whiteboard scenes and starter annotation.json files.")
    parser.add_argument("--srt", type=Path, required=True, help="Input .srt subtitle file")
    parser.add_argument("--out-dir", type=Path, required=True, help="Output folder for storyboard.json & annotations")
    parser.add_argument("--target-scene-sec", type=float, default=30.0)
    parser.add_argument("--width", type=int, default=1920)
    parser.add_argument("--height", type=int, default=1080)
    args = parser.parse_args()

    cues = parse_srt(args.srt.read_text(encoding="utf-8"))
    if not cues:
        raise SystemExit(f"No valid SRT subtitle cues found in {args.srt}")

    scenes = chunk_scenes(cues, args.target_scene_sec)
    args.out_dir.mkdir(parents=True, exist_ok=True)

    storyboard_path = args.out_dir / "storyboard.json"
    storyboard_path.write_text(
        json.dumps({"sourceSrt": str(args.srt), "totalCues": len(cues), "sceneCount": len(scenes), "scenes": scenes}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    annotation_files = []
    for sc in scenes:
        ann = build_starter_annotation(sc, args.width, args.height)
        ann_path = args.out_dir / f"{sc['sceneId']}.annotation.json"
        ann_path.write_text(json.dumps(ann, indent=2, ensure_ascii=False), encoding="utf-8")
        annotation_files.append(str(ann_path))

    print(
        json.dumps(
            {
                "storyboard": str(storyboard_path),
                "total_cues": len(cues),
                "scenes_created": len(scenes),
                "annotations": annotation_files,
            },
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
