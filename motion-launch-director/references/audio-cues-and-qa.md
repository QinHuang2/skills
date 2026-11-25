# Audio Cues Contract & QA Diagnostics Specification

Use this reference when authoring `cues.json`, synthesizing soundtracks with `motion_cli.py sound`, or running pre/post-render quality checks.

---

## 1. `SCENE_MANIFEST` Contract (Inside `index.html`)

Every film must expose `window.SCENE_MANIFEST` as a contiguous, ordered array covering `[0, duration]`:

```javascript
window.SCENE_MANIFEST = [
  { id: "cold-open", start: 0.0, end: 2.5, label: "Problem Statement" },
  { id: "hero-reveal", start: 2.5, end: 6.0, label: "Product Stage Reveal" },
  { id: "workflow-demo", start: 6.0, end: 9.8, label: "Guided Cursor Action" },
  { id: "lockup", start: 9.8, end: 12.0, label: "Brand Lockup & CTA" }
];
```

`motion_cli.py check` verifies:
- `window.__seek` function exists.
- `SCENE_MANIFEST` starts at `0.0`, has no negative durations, and leaves no timeline gaps `> 0.05s` or overlaps.
- All local `<img src="...">` or CSS `url(...)` references exist on disk.

---

## 2. `cues.json` Procedural Audio Schema

`motion_cli.py sound` synthesizes clean 44.1kHz 16-bit stereo WAV audio directly from `cues.json` with zero external audio libraries:

```json
{
  "duration": 12.0,
  "bpm": 120,
  "bed": {
    "enabled": true,
    "root_hz": 110.0,
    "gain": 0.14
  },
  "events": [
    { "time": 0.05, "type": "pulse", "gain": 0.45, "pan": 0.0 },
    { "time": 1.60, "type": "riser", "duration": 0.9, "gain": 0.50, "pan": 0.0 },
    { "time": 2.50, "type": "impact", "gain": 0.75, "pan": 0.0 },
    { "time": 2.52, "type": "whoosh", "duration": 0.35, "gain": 0.45, "pan": -0.25 },
    { "time": 6.80, "type": "click", "gain": 0.55, "pan": 0.15 },
    { "time": 9.80, "type": "chime", "duration": 1.4, "freq": 523.25, "gain": 0.50, "pan": 0.0 }
  ]
}
```

### Supported Cue Types
- **`riser`**: Exponential upward frequency sweep + filtered shimmer building tension into a cut (`duration`: `0.5–1.5s`).
- **`impact`**: Deep sub-bass sine drop (`130Hz -> 34Hz`) + crisp transient punch for hero reveals.
- **`whoosh`**: Band-shaped noise sweep with stereo pan movement for camera transitions and card slides.
- **`click`**: Crisp dual-transient mechanical UI switch click (`1800Hz` + `4200Hz` micro-burst) synced to cursor depression.
- **`pulse`**: Soft low-mid rhythmic heartbeat tick (`95Hz`) for telemetry/counter sequences.
- **`chime`**: Warm harmonic triad bell (`f`, `1.5f`, `2f`) with smooth exponential decay for brand lockups.

---

## 3. Post-Render QA (`motion_cli.py qa`)

When an `.mp4` (or frame folder) is produced, `motion_cli.py qa` inspects it with `ffprobe` and `ffmpeg`:
- **Duration & Stream Audit**: Confirms resolution (`1920x1080` default), frame rate, pixel format (`yuv420p` for universal playback), and audio stream presence.
- **Freeze / Dead-Air Detection**: Runs FFmpeg `freezedetect` (`noise=-50dB`, `d=1.25`) to flag unintended static stretches (ignoring the final 1.5s brand lockup hold).
- **4fps Contact Sheet (`--sheet`)**: Renders a timestamped grid sheet so you can visually scan pacing, visual density, contrast, and transition smoothness in a single image.
