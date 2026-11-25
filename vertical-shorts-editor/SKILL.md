---
name: vertical-shorts-editor
description: >-
  Edit and motion-package 9:16 vertical talking-head videos (TikTok, Instagram
  Reels, YouTube Shorts, Douyin, Channels) from raw footage and word-level
  timestamps or SRT transcripts using a structured plan.json blueprint, safe-zone
  validation, karaoke word-pop captions, rhythm punch-in cuts, B-roll cutaways,
  and FFmpeg or Remotion compilation. Use when the user wants automated vertical
  short-form video editing, creator-style captions, or 9:16 motion packaging.
---

# Vertical Shorts Editor

## Overview

Treat short-form vertical editing (`1080x1920`, `9:16`) as code rather than manual timeline scrubbing. Ingest raw talking-head footage plus word-level timings (WhisperX/Whisper JSON or `.srt`), author a rhythm-snapped `plan.json` blueprint (hook banner, punch-in zoom cuts, karaoke word-pop captions, B-roll cutaways, and motion scene cards), validate platform safe zones, and compile to H.264 `.mp4` via FFmpeg or scaffold a Remotion project.

Use this skill for TikTok, Reels, YouTube Shorts, 抖音, and 视频号 vertical edits.

## Workflow

1. **Probe Source Footage & Timestamps**: Inspect video dimensions, frame rate, and duration with `ffprobe`. Ingest word-level timestamps (`words.json` from WhisperX/Whisper) or `.srt` captions.
2. **Design `plan.json` Blueprint**: Read `references/plan-schema-and-safezones.md` and `references/scene-cards-catalog.md` to build `plan.json`:
   - **0–3s Pattern-Interrupt Hook**: High-contrast hook badge/title inside the upper safe zone (`y: 220–420`).
   - **Punch-In Camera Rhythm**: Alternate `1.00x` base framing and `1.12x–1.16x` punch-in crops snapped to sentence starts or key emphasis words every `3.5–6.0s`.
   - **Karaoke Word-Pop Captions**: Group `2–5` spoken words (or `6–12` CJK characters) per caption beat in the lower-third safe zone (`y: 1260–1520`), highlighting the active spoken token.
   - **B-Roll & Motion Cards**: Schedule supplementary B-roll clips or graphic overlay cards (`metric-badge`, `versus-split`, `step-list`, `myth-fact`, `quote-card`) during conceptual explanations.
3. **Validate Safe Zones & Pacing**: Run `scripts/validate_plan.py` against `plan.json` to block any caption or graphic that collides with TikTok/Reels/Douyin UI chrome (`y < 180`, `y > 1580`, or right rail `x > 900, y > 820`) or covers the speaker's face box.
4. **Compile Vertical Deliverable**:
   - **Direct MP4 Render**: Run `scripts/compile_vertical.py render` to produce `1080x1920` H.264/AAC `.mp4` plus `.ass` karaoke subtitles (automatically falling back to RGBA overlay plates when `ffmpeg` lacks `libass`).
   - **Remotion Project Scaffold**: Run `scripts/compile_vertical.py scaffold-remotion` when the user wants a full React/Remotion codebase for custom JSX motion cards.

## Hard Editing Rules

- **First 2.5 Seconds Decide Retention**: Never open on dead silence, throat clearing, or an unstyled frame. Trim leading dead air and land the visual hook banner at `t = 0.0s`.
- **Respect 9:16 Safe Zones**:
  - Top status/search bar exclusion: `y < 180`
  - Right engagement icon rail exclusion: `x > 900` for `y` in `[820, 1620]`
  - Bottom author/caption/scrub bar exclusion: `y > 1580`
  - Speaker eye-line / face protection box: default `[300, 420, 480, 520]` unless overridden in `plan.json`.
- **Snap Cuts to Speech Transients**: Never punch-zoom mid-syllable; align `cuts` within `<= 60ms` of a word onset or pause boundary.
- **Short Scannable Caption Chunks**: Never dump 3-line subtitle paragraphs on a vertical screen. Keep caption beats to `1–2` tight lines (`<= 14` CJK chars or `<= 5` English words).

## CLI Commands

```bash
# 1. Validate plan.json safe zones, face avoidance, and pacing rhythm
python3 vertical-shorts-editor/scripts/validate_plan.py \
  --plan /path/to/plan.json

# 2. Render 1080x1920 MP4 + .ass karaoke subtitles directly via FFmpeg
python3 vertical-shorts-editor/scripts/compile_vertical.py render \
  --video /path/to/raw_input.mp4 \
  --plan /path/to/plan.json \
  --output /path/to/final_short.mp4

# 3. Or scaffold a Remotion TypeScript composition driven by plan.json
python3 vertical-shorts-editor/scripts/compile_vertical.py scaffold-remotion \
  --plan /path/to/plan.json \
  --out-dir ./remotion-short
```

## Final QA

Accept the short only when:

- `validate_plan.py` passes with zero safe-zone violations, face-box collisions, or timeline overlaps.
- Output resolution is exact `1080x1920` (`yuv420p` H.264 + AAC audio) with zero black pillarbox bars.
- Captions pop cleanly in sync with speech and remain 100% unobstructed by TikTok/Reels/Douyin right-rail and bottom chrome.
