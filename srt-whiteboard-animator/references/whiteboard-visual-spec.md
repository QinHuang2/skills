# Whiteboard Aesthetic & Illustration Specification

Read this specification before designing scene illustrations (SVG or image generation prompts) for `srt-whiteboard-animator`.

---

## 1. Signature Visual DNA

- **Paper Canvas**: Solid `#F5EBD7` (RGB `245, 235, 215`) flat warm parchment—no heavy vignette, crumpled creases, or desk-photo borders that interfere with clean region masking.
- **Primary Ink**: `#2B2B2B` matte charcoal marker strokes (`3px–5px` at `1920x1080`), slightly organic/hand-sketched weight rather than sterile `1px` CAD hairlines.
- **Restrained Accent Palette** (pick max 2–3 per video, filling `<= 15%` of total pixels):
  - **Vermilion Highlight (`#D9534F`)**: Core pain points, warnings, key focal numbers.
  - **Warm Ochre (`#E67E22`)**: Mechanisms, transitions, energy/flow arrows.
  - **Blueprint Blue (`#2E6B9E`)**: Solutions, frameworks, structural containers.
- **Whitespace Floor**: At least **35%–45%** of the `1920x1080` canvas must remain pure `#F5EBD7` paper.

---

## 2. Four Spatial Composition Archetypes (25–35s Scenes)

Choose a distinct spatial skeleton for consecutive scenes so the whiteboard never feels repetitive:

1. **Z-Path Story Flow (`4–5` regions)**: Top-left hook -> Top-right tension -> Diagonal arrow to Bottom-left insight -> Bottom-right takeaway box.
2. **Hub & Spokes (`1 + 4` regions)**: Central core metaphor drawn first (`region 1`), followed clockwise by 4 satellite concept sketches connected by hand-drawn dotted arrows.
3. **Left-vs-Right Contrast Split (`2 + 3` regions)**: Center vertical hand-drawn divider; old/naive mental model sketched down the left column, upgraded model revealed down the right column.
4. **Ascending Step Ladder (`3–4` regions)**: Bottom-left foundation block stepping up-right across 3–4 progressive tiers toward a flagged summit outcome.

---

## 3. Image Prompt / SVG Authoring Rules

- **Non-Overlapping Islands**: Keep at least `36px–48px` of clean `#F5EBD7` paper margin between distinct concept clusters so rectangular or padded region masks in `annotation.json` isolate each concept cleanly without slicing neighboring strokes!
- **Concise Hand-Lettered Labels**: Pair each doodle cluster with a short 2–5 word label (`PingFang SC` / rounded marker style or crisp Chinese/English lettering), never full subtitle sentences—the voiceover carries the full sentence while the board shows the visual anchor.
- **Resolution**: `1920x1080` (`16:9`) default; `1080x1920` (`9:16`) optional for vertical explainers.
