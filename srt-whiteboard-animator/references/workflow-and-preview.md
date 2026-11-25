# Annotation Schema, Overlap Protection & Preview Workflow

Read this file when binding `.srt` cues to `scene_XX.annotation.json` and validating reveals in `preview.html`.

---

## 1. `annotation.json` Schema

Coordinates (`x`, `y`, `w`, `h`) are pixel coordinates on the scene canvas (`1920x1080` default). Timestamps (`startMs`, `endMs`) are **scene-relative milliseconds** (`0` to `sceneDurationMs`):

```json
{
  "sceneId": "scene_01",
  "canvasWidth": 1920,
  "canvasHeight": 1080,
  "paperColor": "#F5EBD7",
  "fps": 30,
  "durationMs": 28500,
  "globalStartMs": 0,
  "regions": [
    {
      "id": "r1_hook",
      "sequence": 1,
      "subtitleText": "Most teams treat subtitles as an afterthought at the bottom of the frame.",
      "startMs": 200,
      "endMs": 6400,
      "x": 110,
      "y": 110,
      "w": 760,
      "h": 380,
      "sweep": "left-to-right",
      "inkRatio": 0.65,
      "protected": true
    },
    {
      "id": "r2_director",
      "sequence": 2,
      "subtitleText": "Instead, use the SRT timeline to direct every stroke on the canvas.",
      "startMs": 6600,
      "endMs": 14200,
      "x": 1020,
      "y": 110,
      "w": 780,
      "h": 380,
      "sweep": "left-to-right",
      "inkRatio": 0.65,
      "protected": true
    }
  ]
}
```

### Field Rules
- **`sweep`**: `"left-to-right"` (horizontal diagrams/text), `"top-to-bottom"` (vertical lists/trees/arrows), or `"instant-fade"` (stamps/callouts).
- **`inkRatio`** (`0.5`–`0.8`): Fraction of `[startMs, endMs]` dedicated to sketching high-contrast monochrome ink strokes before color accents wash in over the remainder.
- **`protected`** (`boolean`): When `true`, `render_whiteboard.py preview` flags an error if any *later* region (`sequence > current`) intersects this bounding box by more than `5%` of its area—preventing later blanking masks from wiping already-drawn art!

---

## 2. Five-Gate Confirmation Checklist

1. **Gate 1 — Scene Breakdown**: Confirm `storyboard.json` splits at natural narrative transitions (`25–35s` target; never mid-clause).
2. **Gate 2 — Island Spacing**: Confirm each `region` in the scene plate has clean `#F5EBD7` paper gutters around it.
3. **Gate 3 — Preview Audit**: Run `render_whiteboard.py preview` and verify `"overlap_errors": []`. Open `scene_XX_preview.html` to scrub the timeline interactively.
4. **Gate 4 — Scene Render**: Render individual `.mp4` scenes and verify smooth `ink -> color` progression at `30fps`.
5. **Gate 5 — Final Merge**: Concatenate scenes and mux voiceover audio, verifying total duration matches the `.srt` end time.
