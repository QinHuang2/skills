#!/usr/bin/env python3
"""CLI toolkit for deterministic HTML launch films: scaffold, check, procedural WAV sound, mux, and FFmpeg QA."""

from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path
import random
import re
import shutil
import struct
import subprocess
import sys
import wave


def find_bin(name: str) -> str | None:
    found = shutil.which(name)
    if found:
        return found
    for prefix in ("/opt/homebrew/bin", "/usr/local/bin"):
        candidate = Path(prefix) / name
        if candidate.exists():
            return str(candidate)
    return None


STARTER_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=1920, initial-scale=1.0" />
  <title>__TITLE__</title>
  <style>
    :root {
      --bg: #09090B;
      --surface: #131318;
      --ink: #FAFAFA;
      --muted: #A1A1AA;
      --accent: #FF5500;
      --border: #27272A;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    html, body {
      width: 1920px; height: 1080px; overflow: hidden;
      background: var(--bg); color: var(--ink);
      font-family: -apple-system, BlinkMacSystemFont, "Plus Jakarta Sans", "PingFang SC", sans-serif;
    }
    #stage {
      position: relative; width: 1920px; height: 1080px; overflow: hidden;
      padding: 80px 96px; display: flex; align-items: center; justify-content: center;
    }
    .hero-card {
      width: 1180px; padding: 72px 84px; border-radius: 24px;
      background: var(--surface); border: 1px solid var(--border);
      box-shadow: 0 40px 120px rgba(0, 0, 0, 0.55);
      will-change: transform, opacity;
    }
    .kicker {
      font-size: 16px; letter-spacing: 0.16em; text-transform: uppercase;
      color: var(--accent); font-weight: 700; margin-bottom: 24px;
    }
    h1 {
      font-size: 84px; line-height: 1.06; letter-spacing: -0.03em; margin-bottom: 28px;
    }
    .sub {
      font-size: 28px; line-height: 1.5; color: var(--muted); max-width: 820px;
    }
    #studio-hud {
      position: fixed; left: 24px; right: 24px; bottom: 20px; z-index: 9999;
      display: flex; align-items: center; gap: 14px; padding: 12px 18px;
      background: rgba(18, 18, 23, 0.92); border: 1px solid #3F3F46; border-radius: 12px;
      font-size: 13px; font-variant-numeric: tabular-nums;
    }
    #studio-hud.hidden { display: none; }
    #studio-hud button {
      background: var(--accent); color: #fff; border: none; border-radius: 6px;
      padding: 6px 12px; font-weight: 600; cursor: pointer;
    }
    #scrubber { flex: 1; accent-color: var(--accent); }
    #pin-marker {
      position: fixed; width: 18px; height: 18px; border-radius: 50%;
      border: 2px solid var(--accent); background: rgba(255, 85, 0, 0.28);
      transform: translate(-50%, -50%); pointer-events: none; display: none; z-index: 9998;
    }
  </style>
</head>
<body>
  <main id="stage">
    <section class="hero-card" id="hero-card">
      <div class="kicker" id="kicker">01 / LAUNCH FILM</div>
      <h1 id="headline">__TITLE__</h1>
      <p class="sub" id="subcopy">Deterministic code-driven motion stage. Press S to toggle Studio HUD, click any frame to copy a spatial revision pin.</p>
    </section>
  </main>

  <div id="pin-marker"></div>
  <div id="studio-hud">
    <button id="play-btn" type="button">Pause</button>
    <span id="time-readout">0.00s / __DURATION__.00s</span>
    <input id="scrubber" type="range" min="0" max="__DURATION__" step="0.0166667" value="0" />
    <span id="scene-readout">cold-open</span>
    <span id="pin-status" style="color:#A1A1AA;">Click stage to pin frame</span>
  </div>

  <script>
    window.FILM_CONFIG = { duration: __DURATION__, fps: __FPS__ };
    window.SCENE_MANIFEST = [
      { id: "cold-open", start: 0.0, end: __S1__, label: "Cold Open" },
      { id: "hero-reveal", start: __S1__, end: __S2__, label: "Hero Stage" },
      { id: "lockup", start: __S2__, end: __DURATION__, label: "Brand Lockup" }
    ];

    const clamp01 = (v) => Math.max(0, Math.min(1, v));
    const progress = (t, s, d) => clamp01((t - s) / Math.max(0.0001, d));
    const easeOutExpo = (p) => (p >= 1 ? 1 : 1 - Math.pow(2, -10 * p));

    const card = document.getElementById("hero-card");
    const headline = document.getElementById("headline");
    const subcopy = document.getElementById("subcopy");
    const timeReadout = document.getElementById("time-readout");
    const sceneReadout = document.getElementById("scene-readout");
    const scrubber = document.getElementById("scrubber");

    let currentTime = 0;
    let playing = !new URLSearchParams(location.search).has("headless");
    if (new URLSearchParams(location.search).has("headless")) {
      document.getElementById("studio-hud").classList.add("hidden");
    }

    function activeScene(t) {
      return window.SCENE_MANIFEST.find((s) => t >= s.start && t <= s.end) || window.SCENE_MANIFEST[0];
    }

    window.__seek = function(t) {
      currentTime = Math.max(0, Math.min(window.FILM_CONFIG.duration, Number(t) || 0));
      const enter = easeOutExpo(progress(currentTime, 0, 1.1));
      const subEnter = easeOutExpo(progress(currentTime, 0.35, 1.0));
      const drift = 1 + 0.025 * (currentTime / window.FILM_CONFIG.duration);

      card.style.opacity = String(enter);
      card.style.transform = `translateY(${(1 - enter) * 48}px) scale(${(0.94 + 0.06 * enter) * drift})`;
      headline.style.opacity = String(enter);
      subcopy.style.opacity = String(subEnter);

      const sc = activeScene(currentTime);
      timeReadout.textContent = `${currentTime.toFixed(2)}s / ${window.FILM_CONFIG.duration.toFixed(2)}s`;
      sceneReadout.textContent = sc ? sc.id : "";
      scrubber.value = String(currentTime);
      return currentTime;
    };

    let lastWall = performance.now();
    function tick(now) {
      const dt = (now - lastWall) / 1000;
      lastWall = now;
      if (playing) {
        const next = currentTime + dt;
        window.__seek(next >= window.FILM_CONFIG.duration ? 0 : next);
      }
      requestAnimationFrame(tick);
    }

    document.getElementById("play-btn").addEventListener("click", (e) => {
      playing = !playing;
      e.target.textContent = playing ? "Pause" : "Play";
    });
    scrubber.addEventListener("input", (e) => {
      playing = false;
      document.getElementById("play-btn").textContent = "Play";
      window.__seek(parseFloat(e.target.value));
    });
    window.addEventListener("keydown", (e) => {
      if (e.key.toLowerCase() === "s") {
        document.getElementById("studio-hud").classList.toggle("hidden");
      }
    });
    document.getElementById("stage").addEventListener("click", (e) => {
      playing = false;
      document.getElementById("play-btn").textContent = "Play";
      const rect = e.currentTarget.getBoundingClientRect();
      const xPct = Number((((e.clientX - rect.left) / rect.width) * 100).toFixed(1));
      const yPct = Number((((e.clientY - rect.top) / rect.height) * 100).toFixed(1));
      const marker = document.getElementById("pin-marker");
      marker.style.left = `${e.clientX}px`;
      marker.style.top = `${e.clientY}px`;
      marker.style.display = "block";
      const target = e.target.id ? `#${e.target.id}` : e.target.tagName.toLowerCase();
      const note = prompt("Frame revision note for agent:", "Adjust timing or styling here") || "";
      const payload = {
        time: Number(currentTime.toFixed(2)),
        frame: Math.round(currentTime * window.FILM_CONFIG.fps),
        sceneId: activeScene(currentTime).id,
        xPct,
        yPct,
        selector: target,
        note
      };
      if (navigator.clipboard) {
        navigator.clipboard.writeText(JSON.stringify(payload));
      }
      document.getElementById("pin-status").textContent = `Pinned @ ${payload.time}s (${payload.sceneId}) copied`;
    });

    window.__seek(0);
    requestAnimationFrame(tick);
  </script>
</body>
</html>
"""


def cmd_new(args: argparse.Namespace) -> None:
    proj = args.dir.resolve()
    proj.mkdir(parents=True, exist_ok=True)
    (proj / "assets").mkdir(exist_ok=True)
    (proj / "out").mkdir(exist_ok=True)

    dur = float(args.duration)
    s1 = round(dur * 0.25, 2)
    s2 = round(dur * 0.78, 2)
    html = (
        STARTER_HTML.replace("__TITLE__", args.title)
        .replace("__DURATION__", f"{dur:g}")
        .replace("__FPS__", str(args.fps))
        .replace("__S1__", str(s1))
        .replace("__S2__", str(s2))
    )
    index_path = proj / "index.html"
    index_path.write_text(html, encoding="utf-8")

    cues = {
        "duration": dur,
        "bpm": 120,
        "bed": {"enabled": True, "root_hz": 110.0, "gain": 0.12},
        "events": [
            {"time": 0.05, "type": "impact", "gain": 0.68, "pan": 0.0},
            {"time": max(0.2, round(s1 - 0.65, 2)), "type": "riser", "duration": 0.65, "gain": 0.45, "pan": 0.0},
            {"time": s1, "type": "whoosh", "duration": 0.32, "gain": 0.48, "pan": -0.2},
            {"time": round((s1 + s2) / 2, 2), "type": "click", "gain": 0.55, "pan": 0.15},
            {"time": s2, "type": "chime", "duration": 1.3, "freq": 523.25, "gain": 0.48, "pan": 0.0},
        ],
    }
    cues_path = proj / "cues.json"
    cues_path.write_text(json.dumps(cues, indent=2), encoding="utf-8")

    print(
        json.dumps(
            {"created": str(proj), "index": str(index_path), "cues": str(cues_path), "duration": dur, "fps": args.fps},
            indent=2,
        )
    )


def cmd_check(args: argparse.Namespace) -> None:
    proj = args.dir.resolve()
    index_path = proj / "index.html"
    errors: list[str] = []
    warnings: list[str] = []

    if not index_path.exists():
        raise SystemExit(f"Missing index.html in {proj}")

    text = index_path.read_text(encoding="utf-8")
    if "window.__seek" not in text:
        errors.append("Missing deterministic scrubber contract: window.__seek(t).")
    if "SCENE_MANIFEST" not in text:
        errors.append("Missing window.SCENE_MANIFEST timeline declaration.")
    if "Math.random(" in text:
        warnings.append("Unseeded Math.random() detected; replace with deterministic hash of frame/index.")

    scenes: list[tuple[str, float, float]] = []
    for m in re.finditer(
        r"\{\s*id\s*:\s*[\"']([^\"']+)[\"']\s*,\s*start\s*:\s*([0-9.]+)\s*,\s*end\s*:\s*([0-9.]+)",
        text,
    ):
        scenes.append((m.group(1), float(m.group(2)), float(m.group(3))))

    if scenes:
        scenes_sorted = sorted(scenes, key=lambda x: x[1])
        if scenes_sorted[0][1] > 0.05:
            errors.append(f"First scene '{scenes_sorted[0][0]}' starts at {scenes_sorted[0][1]}s (> 0.0s).")
        for idx, (sid, st, en) in enumerate(scenes_sorted):
            if en <= st:
                errors.append(f"Scene '{sid}' has non-positive duration ({st} -> {en}).")
            if idx > 0:
                prev_id, _, prev_en = scenes_sorted[idx - 1]
                gap = st - prev_en
                if gap > 0.05:
                    errors.append(f"Timeline gap of {gap:.2f}s between '{prev_id}' and '{sid}'.")
                elif gap < -0.05:
                    warnings.append(f"Scene overlap of {-gap:.2f}s between '{prev_id}' and '{sid}'.")
    else:
        warnings.append("Could not statically parse scene entries in SCENE_MANIFEST.")

    for ref in re.findall(r"(?:src|href)=[\"']([^\"'#?]+)[\"']", text):
        if ref.startswith(("http://", "https://", "data:")):
            continue
        if not (proj / ref).exists():
            errors.append(f"Referenced local asset missing: {ref}")

    cues_path = proj / "cues.json"
    if cues_path.exists():
        cues = json.loads(cues_path.read_text(encoding="utf-8"))
        if not cues.get("events"):
            warnings.append("cues.json has zero sound events.")
    else:
        warnings.append("No cues.json found in project folder.")

    report = {
        "project": str(proj),
        "passed": len(errors) == 0,
        "scenes_parsed": len(scenes),
        "errors": errors,
        "warnings": warnings,
    }
    print(json.dumps(report, indent=2))
    sys.exit(0 if report["passed"] else 1)


def synthesize_wav(cues: dict, output_path: Path, sample_rate: int = 44100) -> dict:
    duration = float(cues.get("duration", 10.0))
    total_samples = max(1, int(duration * sample_rate))
    left = [0.0] * total_samples
    right = [0.0] * total_samples

    bed = cues.get("bed", {})
    if bed.get("enabled", False):
        root = float(bed.get("root_hz", 110.0))
        gain = float(bed.get("gain", 0.12))
        for i in range(total_samples):
            t = i / sample_rate
            fade = min(1.0, t / 0.6, (duration - t) / 0.8)
            fade = max(0.0, fade)
            sig = (
                0.55 * math.sin(2 * math.pi * root * t)
                + 0.30 * math.sin(2 * math.pi * (root * 1.5) * t)
                + 0.15 * math.sin(2 * math.pi * (root * 2.0) * t)
            ) * gain * fade
            left[i] += sig * 0.96
            right[i] += sig * 1.04

    rng = random.Random(42)
    events = cues.get("events", [])
    for ev in events:
        t0 = float(ev.get("time", 0.0))
        etype = ev.get("type", "click")
        gain = float(ev.get("gain", 0.5))
        pan = max(-1.0, min(1.0, float(ev.get("pan", 0.0))))
        l_gain = math.sqrt(0.5 * (1.0 - pan))
        r_gain = math.sqrt(0.5 * (1.0 + pan))
        start_idx = max(0, int(t0 * sample_rate))

        if etype == "impact":
            edur = float(ev.get("duration", 0.65))
            n = int(edur * sample_rate)
            for k in range(n):
                idx = start_idx + k
                if idx >= total_samples:
                    break
                lt = k / sample_rate
                freq = 36.0 + 105.0 * math.exp(-16.0 * lt)
                env = math.exp(-5.2 * lt)
                punch = (rng.uniform(-1, 1) * math.exp(-65.0 * lt)) * 0.35
                val = (math.sin(2 * math.pi * freq * lt) * env + punch) * gain
                left[idx] += val * l_gain
                right[idx] += val * r_gain

        elif etype == "riser":
            edur = float(ev.get("duration", 0.8))
            n = int(edur * sample_rate)
            phase = 0.0
            for k in range(n):
                idx = start_idx + k
                if idx >= total_samples:
                    break
                p = k / max(1, n)
                freq = 140.0 * (8.0 ** (p * p))
                phase += 2 * math.pi * freq / sample_rate
                env = (p ** 2.2) * (1.0 - 0.15 * max(0.0, (p - 0.92) / 0.08))
                shimmer = rng.uniform(-0.35, 0.35) * (p ** 3)
                val = (0.7 * math.sin(phase) + shimmer) * env * gain
                left[idx] += val * l_gain
                right[idx] += val * r_gain

        elif etype == "whoosh":
            edur = float(ev.get("duration", 0.32))
            n = int(edur * sample_rate)
            prev = 0.0
            for k in range(n):
                idx = start_idx + k
                if idx >= total_samples:
                    break
                p = k / max(1, n)
                env = math.sin(math.pi * p) ** 1.6
                alpha = 0.08 + 0.45 * math.sin(math.pi * p)
                raw = rng.uniform(-1.0, 1.0)
                prev = prev + alpha * (raw - prev)
                dyn_pan = max(-1.0, min(1.0, pan + (p - 0.5) * 0.7))
                val = prev * env * gain * 1.6
                left[idx] += val * math.sqrt(0.5 * (1.0 - dyn_pan))
                right[idx] += val * math.sqrt(0.5 * (1.0 + dyn_pan))

        elif etype == "click":
            n = int(0.045 * sample_rate)
            for k in range(n):
                idx = start_idx + k
                if idx >= total_samples:
                    break
                lt = k / sample_rate
                val = (
                    0.65 * math.sin(2 * math.pi * 1950.0 * lt) * math.exp(-120.0 * lt)
                    + 0.45 * math.sin(2 * math.pi * 4100.0 * lt) * math.exp(-210.0 * lt)
                ) * gain
                left[idx] += val * l_gain
                right[idx] += val * r_gain

        elif etype == "pulse":
            n = int(0.18 * sample_rate)
            for k in range(n):
                idx = start_idx + k
                if idx >= total_samples:
                    break
                lt = k / sample_rate
                val = math.sin(2 * math.pi * 92.0 * lt) * math.exp(-22.0 * lt) * gain
                left[idx] += val * l_gain
                right[idx] += val * r_gain

        elif etype == "chime":
            edur = float(ev.get("duration", 1.3))
            base = float(ev.get("freq", 523.25))
            n = int(edur * sample_rate)
            for k in range(n):
                idx = start_idx + k
                if idx >= total_samples:
                    break
                lt = k / sample_rate
                env = (1.0 - math.exp(-120.0 * lt)) * math.exp(-2.8 * lt)
                val = (
                    0.55 * math.sin(2 * math.pi * base * lt)
                    + 0.28 * math.sin(2 * math.pi * base * 1.25 * lt)
                    + 0.20 * math.sin(2 * math.pi * base * 1.5 * lt)
                ) * env * gain
                left[idx] += val * l_gain
                right[idx] += val * r_gain

    output_path.parent.mkdir(parents=True, exist_ok=True)
    peak = max(max((abs(v) for v in left), default=0.0), max((abs(v) for v in right), default=0.0))
    scale = 0.92 / peak if peak > 0.92 else 1.0

    pcm = bytearray()
    for l_val, r_val in zip(left, right):
        li = max(-32767, min(32767, int(l_val * scale * 32767)))
        ri = max(-32767, min(32767, int(r_val * scale * 32767)))
        pcm.extend(struct.pack("<hh", li, ri))

    with wave.open(str(output_path), "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(bytes(pcm))

    return {
        "output": str(output_path),
        "duration_sec": duration,
        "events_rendered": len(events),
        "sample_rate": sample_rate,
        "peak_normalized": round(min(peak, 0.92), 3),
    }


def cmd_sound(args: argparse.Namespace) -> None:
    cues = json.loads(args.cues.read_text(encoding="utf-8"))
    info = synthesize_wav(cues, args.output)
    print(json.dumps(info, indent=2))


def cmd_mux(args: argparse.Namespace) -> None:
    ffmpeg = find_bin("ffmpeg")
    if not ffmpeg:
        raise SystemExit("ffmpeg binary not found in PATH or /opt/homebrew/bin.")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        ffmpeg,
        "-y",
        "-framerate",
        str(args.fps),
        "-i",
        str(args.frames_pattern),
    ]
    if args.audio and args.audio.exists():
        cmd.extend(["-i", str(args.audio), "-shortest"])
    cmd.extend(
        [
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-crf",
            "18",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            str(args.output),
        ]
    )
    subprocess.run(cmd, check=True)
    print(json.dumps({"output": str(args.output), "size_bytes": args.output.stat().st_size}, indent=2))


def cmd_qa(args: argparse.Namespace) -> None:
    ffmpeg = find_bin("ffmpeg")
    ffprobe = find_bin("ffprobe")
    if not ffmpeg or not ffprobe:
        raise SystemExit("ffmpeg/ffprobe not found in PATH or /opt/homebrew/bin.")
    if not args.video.exists():
        raise SystemExit(f"Video not found: {args.video}")

    probe_out = subprocess.check_output(
        [ffprobe, "-v", "error", "-show_format", "-show_streams", "-of", "json", str(args.video)],
        text=True,
    )
    probe = json.loads(probe_out)
    duration = float(probe.get("format", {}).get("duration", 0.0))
    streams = probe.get("streams", [])
    v_stream = next((s for s in streams if s.get("codec_type") == "video"), {})
    a_stream = next((s for s in streams if s.get("codec_type") == "audio"), None)

    freeze_proc = subprocess.run(
        [ffmpeg, "-i", str(args.video), "-vf", "freezedetect=n=-50dB:d=1.25", "-f", "null", "-"],
        capture_output=True,
        text=True,
    )
    freezes: list[dict] = []
    cur_start: float | None = None
    for line in freeze_proc.stderr.splitlines():
        m_st = re.search(r"freeze_start:\s*([0-9.]+)", line)
        m_en = re.search(r"freeze_end:\s*([0-9.]+)", line)
        if m_st:
            cur_start = float(m_st.group(1))
        elif m_en and cur_start is not None:
            end_t = float(m_en.group(1))
            if end_t < max(0.0, duration - 1.5):
                freezes.append({"start": round(cur_start, 2), "end": round(end_t, 2)})
            cur_start = None

    sheet_path_str: str | None = None
    if args.sheet:
        args.sheet.parent.mkdir(parents=True, exist_ok=True)
        total_thumbs = max(4, min(32, int(math.ceil(duration * 2))))
        cols = 4
        rows = max(1, math.ceil(total_thumbs / cols))
        fps_sample = max(0.5, round(total_thumbs / max(0.5, duration), 2))
        vf = f"fps={fps_sample},scale=480:-1,tile={cols}x{rows}:padding=8:margin=8:color=0x111114"
        subprocess.run(
            [ffmpeg, "-y", "-i", str(args.video), "-vf", vf, "-frames:v", "1", str(args.sheet)],
            check=True,
            capture_output=True,
        )
        sheet_path_str = str(args.sheet)

    warnings: list[str] = []
    if v_stream.get("pix_fmt") != "yuv420p":
        warnings.append(f"Pixel format is '{v_stream.get('pix_fmt')}', recommend 'yuv420p' for universal compatibility.")
    if a_stream is None:
        warnings.append("No audio stream detected in video.")
    if freezes:
        warnings.append(f"Mid-film static freeze intervals (>1.25s) detected: {freezes}")

    report = {
        "video": str(args.video),
        "duration_sec": round(duration, 2),
        "width": v_stream.get("width"),
        "height": v_stream.get("height"),
        "pix_fmt": v_stream.get("pix_fmt"),
        "has_audio": a_stream is not None,
        "freeze_warnings": freezes,
        "contact_sheet": sheet_path_str,
        "warnings": warnings,
        "passed": len(freezes) == 0,
    }
    print(json.dumps(report, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description="Motion Launch Director CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    p_new = sub.add_parser("new", help="Scaffold a deterministic motion project")
    p_new.add_argument("--dir", type=Path, required=True)
    p_new.add_argument("--title", type=str, default="Product Launch")
    p_new.add_argument("--duration", type=float, default=12.0)
    p_new.add_argument("--fps", type=int, default=60)
    p_new.set_defaults(func=cmd_new)

    p_chk = sub.add_parser("check", help="Validate deterministic HTML stage and manifest")
    p_chk.add_argument("--dir", type=Path, required=True)
    p_chk.set_defaults(func=cmd_check)

    p_snd = sub.add_parser("sound", help="Synthesize stereo WAV audio from cues.json")
    p_snd.add_argument("--cues", type=Path, required=True)
    p_snd.add_argument("--output", type=Path, required=True)
    p_snd.set_defaults(func=cmd_sound)

    p_mux = sub.add_parser("mux", help="Compile PNG frame sequence + WAV into H.264 MP4")
    p_mux.add_argument("--frames-pattern", type=str, required=True, help="e.g. ./frames/frame_%04d.png")
    p_mux.add_argument("--audio", type=Path, default=None)
    p_mux.add_argument("--fps", type=int, default=60)
    p_mux.add_argument("--output", type=Path, required=True)
    p_mux.set_defaults(func=cmd_mux)

    p_qa = sub.add_parser("qa", help="Run post-render FFmpeg freeze check and contact-sheet export")
    p_qa.add_argument("--video", type=Path, required=True)
    p_qa.add_argument("--sheet", type=Path, default=None)
    p_qa.set_defaults(func=cmd_qa)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
