---
name: srt-whiteboard-animator
description: >-
  Convert SRT subtitle files (and optional voiceover audio) into warm-paper,
  hand-drawn whiteboard explainer animation videos (MP4) with subtitle-synchronized
  ink-then-color progressive reveals, region overlap protection, interactive
  browser preview, and multi-scene merging. Use when the user provides an .srt
  subtitle or narration script and wants a whiteboard animation, hand-drawn
  doodle explainer, or progressive visual lecture video.
---

# SRT Whiteboard Animator

## Overview

Use `.srt` subtitles not merely as bottom captions, but as the **temporal director** of a hand-drawn whiteboard canvas. Elements appear progressively in semantic narrative order on warm beige paper (`#F5EBD7`)—first sketching dark charcoal ink lines (`ink` phase), then brushing in restrained marker accents (`color` phase)—while preserving previously drawn regions across the scene.

Use this skill for educational explainers, book breakdowns, technical/business concept talks, and narrated long-form videos driven by `.srt` timelines.

## Workflow

Follow the **5-stage step-by-step confirmation pipeline** to avoid wasted rendering:

1. **Parse SRT into Storyboard Scenes**: Run `scripts/parse_srt.py` on the `.srt` file to group subtitle cues into `25–35s` narrative scenes (`storyboard.json`) and scaffold per-scene `.annotation.json` files.
2. **Design Scene Visual Strategy & Doodle Plate**: Read `references/whiteboard-visual-spec.md`. Present the scene-by-scene visual layout plan to the user, then generate one unified `1920x1080` warm-paper illustration (`scene_XX.png` or `scene_XX.svg` converted to PNG) per scene.
3. **Bind Subtitle Regions (`annotation.json`)**: Read `references/workflow-and-preview.md` and bind each subtitle beat to its canvas bounding region (`x`, `y`, `w`, `h`), drawing `sweep` direction (`left-to-right`, `top-to-bottom`, `radial`), `inkRatio` (`0.65` default), and `protected` flag.
4. **Generate Interactive Preview Console**: Run `scripts/render_whiteboard.py preview` to build a local `preview_scene_XX.html` inspection page and audit region overlaps before encoding video.
5. **Stream-Render & Merge MP4**: Run `scripts/render_whiteboard.py render` for each scene to compile H.264 `.mp4` progressive `ink -> color` reveals, then run `scripts/render_whiteboard.py merge` to concatenate all scenes (and optional voiceover audio) into the final video.

## Hard Visual & Timing Rules

- **Warm-Paper Aesthetic**: Always ground scenes on `#F5EBD7` warm paper with `#2B2B2B` charcoal line art and at most 3 marker accents (`#D9534F` vermilion, `#E67E22` warm ochre, `#2E6B9E` blueprint blue). Never use photorealistic 3D renders or dark neon backgrounds.
- **Breathing Whitespace**: Keep **>= 35% empty paper** on every scene plate so progressive reveals remain legible and uncluttered.
- **Narrative Order Over Grid Order**: Reveal regions strictly in the sequence concepts are spoken in the `.srt` timeline, using connector arrows between regions to guide the viewer's eye.
- **Two-Stage `Ink -> Color` Reveal**: Every region spends the first `60%–70%` of its subtitle window tracing high-contrast monochrome ink strokes before blending in marker color accents during the final `30%–40%`.
- **Overlap Protection**: Check `preview` overlap diagnostics so new region masks never accidentally blank out earlier `protected: true` regions.

## CLI Commands

```bash
# 1. Parse .srt into 25-35s scenes + starter annotation.json files
python3 srt-whiteboard-animator/scripts/parse_srt.py \
  --srt /path/to/captions.srt \
  --out-dir ./whiteboard_build \
  --target-scene-sec 30

# 2. Generate interactive browser preview & check region overlaps
python3 srt-whiteboard-animator/scripts/render_whiteboard.py preview \
  --image ./whiteboard_build/scene_01.png \
  --annotation ./whiteboard_build/scene_01.annotation.json \
  --output ./whiteboard_build/scene_01_preview.html

# 3. Render streaming ink->color whiteboard scene MP4
python3 srt-whiteboard-animator/scripts/render_whiteboard.py render \
  --image ./whiteboard_build/scene_01.png \
  --annotation ./whiteboard_build/scene_01.annotation.json \
  --output ./whiteboard_build/scene_01.mp4

# 4. Merge rendered scene MP4s (+ optional narration audio)
python3 srt-whiteboard-animator/scripts/render_whiteboard.py merge \
  --inputs ./whiteboard_build/scene_01.mp4 ./whiteboard_build/scene_02.mp4 \
  --audio /path/to/voiceover.mp3 \
  --output ./whiteboard_build/final_whiteboard.mp4
```

## Final QA

Accept the final animation only when:

- Scene boundaries fall cleanly on sentence breaks (`20–40s` per scene).
- `render_whiteboard.py preview` reports zero unintended overlaps on protected regions.
- Each concept begins drawing within `<= 150ms` of its corresponding `.srt` cue start time.
- Merged `.mp4` plays cleanly (`yuv420p` H.264) with exact audio-subtitle synchronization.
