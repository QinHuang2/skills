---
name: motion-launch-director
description: >-
  Direct, compose, preview, and render deterministic code-driven product launch
  films, commercial motion graphics, and animated technical explainers using
  HTML/CSS/JS/Canvas, procedural WAV sound synthesis, interactive
  Point-at-the-Frame browser review, and FFmpeg contact-sheet QA. Use when the
  user wants a launch video, promo animation, kinetic typography piece, UI
  walkthrough film, or code-driven motion graphics rather than generative AI video.
---

# Motion Launch Director

## Overview

Direct commercial-grade motion graphics and product launch films entirely as deterministic code. Every composition lives in a self-contained HTML stage controlled by `window.__seek(t)` and `window.SCENE_MANIFEST`, ensuring frame-accurate scrubbing, zero randomness, surgical frame-pinned revisions, synchronized procedural sound effects, and automated contact-sheet quality assurance.

Use this skill for 16:9 product launch videos, brand reveal bumpers, kinetic typography films, UI feature demos, and technical motion explainers.

## Workflow

1. **Plan Story Arc & Rhythm**: Read `references/choreography-and-camera.md` to map the narrative arc (Hook 0–3s, Tension/Problem, Hero Reveal, Feature Beats, Lockup/CTA) with explicit timestamps and camera energy curves.
2. **Scaffold Starter Film**: Run `scripts/motion_cli.py new` to create a deterministic stage (`index.html` with built-in Point-at-the-Frame Studio HUD + `cues.json`).
3. **Compose Deterministic Scenes**: Implement every scene inside `renderAtTime(t)` so all transforms, opacities, counters, cursor paths, and canvas drawings are pure mathematical functions of `t` (in seconds). Never rely on uncontrolled `setTimeout`, CSS infinite animations detached from `t`, or unseeded `Math.random()`.
4. **Score Procedural Sound**: Read `references/audio-cues-and-qa.md`, align `cues.json` events (`riser`, `impact`, `whoosh`, `click`, `pulse`, `chime`) to scene transitions and UI actions, and run `scripts/motion_cli.py sound` to synthesize a sample-accurate stereo `.wav` track.
5. **Run Pre-Render Check**: Execute `scripts/motion_cli.py check` to verify `window.__seek` contract, `SCENE_MANIFEST` timeline continuity (zero dead gaps or overlaps), missing assets, and text safe margins.
6. **Point-at-the-Frame Review Loop**: Open `index.html` in the browser studio (or inspect via headless browser). When the user clicks a frame in Studio mode and provides a pin JSON (`{time, sceneId, xPct, yPct, selector, note}`), jump straight to the matching scene block in `index.html` and adjust only that element's choreography.
7. **Render & Post-Render QA**: Compile frames + `soundtrack.wav` into `.mp4` (`scripts/motion_cli.py mux` when frames are rendered), then run `scripts/motion_cli.py qa --video <mp4> --sheet <sheet.png>` to generate a 4fps tiled contact sheet and scan for frozen dead-air segments.

## Hard Motion Rules

- **Determinism Contract**: Calling `window.__seek(4.25)` in any order must produce the exact same pixel state every time.
- **No Linear Easing on Hero Motion**: Use expressive spring/exponential curves (`cubic-bezier(0.16, 1, 0.3, 1)` expo-out for entrances, `cubic-bezier(0.7, 0, 0.84, 0)` for exits) implemented mathematically in JS (`easeOutExpo`, `easeInOutCubic`, `springDamped`).
- **One Focal Action Per Beat**: Never animate four competing text blocks simultaneously. Lead the eye sequentially with 60–120ms stagger offsets.
- **Safe Title Margins**: Keep all typography inside the 90% title-safe inset (`>= 96px` horizontal, `>= 64px` vertical on `1920x1080`).
- **Audio-Visual Lock**: Every major visual cut, hero scale-in, or simulated cursor click must have a matching timestamped entry in `cues.json`.

## CLI Commands

```bash
# 1. Initialize a deterministic motion project
python3 motion-launch-director/scripts/motion_cli.py new \
  --dir ./launch-film \
  --title "Product Launch" \
  --duration 12 \
  --fps 60

# 2. Pre-render static contract & timeline check
python3 motion-launch-director/scripts/motion_cli.py check \
  --dir ./launch-film

# 3. Synthesize synchronized WAV audio track from cues.json
python3 motion-launch-director/scripts/motion_cli.py sound \
  --cues ./launch-film/cues.json \
  --output ./launch-film/soundtrack.wav

# 4. Post-render QA + 4fps contact sheet generation
python3 motion-launch-director/scripts/motion_cli.py qa \
  --video ./launch-film/out/final.mp4 \
  --sheet ./launch-film/out/contact-sheet.png
```

## Final QA

Accept the film only when:

- `motion_cli.py check` passes with zero timeline gaps, missing assets, or contract errors.
- Contact sheet (`contact-sheet.png`) shows clean frame progression with zero overlapping captions, clipped headlines, or > 1.2s unintentional static dead air.
- Audio cues align within <= 2 frames of visual impacts and UI clicks.
