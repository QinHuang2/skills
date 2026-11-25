# Isometric Projection, Shading & Interactive Specification

Read this file before drafting SVG coordinates or writing `machine-spec.json` files for `scripts/iso_kit.py`.

---

## 1. True Isometric Projection Math

World coordinates use right-handed engineering axes `(x, y, z)` in millimeters/grid units:
- **`+x`**: Forward-right axis (`30°` down-right on screen)
- **`+y`**: Forward-left axis (`30°` down-left on screen)
- **`+z`**: Vertical upward axis (`straight up` on screen)

Screen projection `(sx, sy)` with origin `(ox, oy)` and unit scale `S` (`cos 30° ≈ 0.8660254`, `sin 30° = 0.5`):

```text
sx = ox + (x - y) * 0.8660254 * S
sy = oy + (x + y) * 0.5 * S - z * S
```

### Isometric Ellipses (Vertical Cylinders & Sight Tubes)
A horizontal circle of radius `R` at height `z` projects to an axis-aligned SVG `<ellipse>`:
- `rx = R * 0.8660254 * sqrt(2) ≈ R * 1.2247 * S` (or standard isometric top-face inscribed circle: `rx = R * 0.8660254 * S * sqrt(2)` -> exact isometric circle has major radius `R * S * 1.2247`? Wait—let's verify exact math: on standard un-foreshortened isometric where unit step along x projects to length `S` (`dx = S*cos30, dy = S*sin30`, length = `S`), a circle of radius `R` in the XY plane has major axis `rx = R * S * 1.224745` (`sqrt(3/2)`) and minor axis `ry = R * S * 0.707107` (`sqrt(1/2)`), maintaining exact `rx / ry = sqrt(3) ≈ 1.73205`!).
- **Golden Rule**: Every horizontal isometric ellipse MUST have `rx : ry = √3 : 1` (`1.732 : 1`).

---

## 2. Painter's Depth-Sorting Key

To prevent Escher-like overlap bugs in SVG (which has no z-buffer):
1. Render the **baseplate (`z <= 0`)** and **cast ground shadows** in `<g id="layer-base">`.
2. Sort all static & dynamic 3D solids ascending by depth key:
   ```text
   depth_key = (part.x_min + part.y_min + part.x_max + part.y_max) * 0.5 + part.z_center * 0.01
   ```
   (Smaller `x + y` is further away toward top-center; larger `x + y` is closer toward bottom-center.)
3. Render **callout leader lines and labels** last in `<g id="layer-annotations">` so typography is never occluded by machine parts.

---

## 3. Declarative `machine-spec.json` Schema (`scripts/iso_kit.py`)

`iso_kit.py` compiles this schema directly into depth-sorted SVG or standalone interactive HTML:

```json
{
  "title": "Token Bucket Rate Limiter",
  "figure_code": "FIG. 01 — ESCAPEMENT & SIGHT RESERVOIR",
  "theme": "vellum",
  "canvas": { "width": 1120, "height": 720, "origin_x": 560, "origin_y": 210, "scale": 18 },
  "controls": [
    { "id": "refill_rate", "label": "Refill Rate (tokens/s)", "min": 1, "max": 20, "value": 6, "step": 1 },
    { "id": "capacity", "label": "Bucket Capacity", "min": 5, "max": 30, "value": 15, "step": 1 }
  ],
  "readouts": [
    { "id": "tokens_now", "label": "RESERVOIR", "value": "15.0 tk" },
    { "id": "gate_state", "label": "ESCAPEMENT", "value": "OPEN" }
  ],
  "parts": [
    { "id": "base", "type": "plate", "x": 0, "y": 0, "z": -1.2, "dx": 16, "dy": 14, "dz": 1.2, "color": "#D6CEBF" },
    { "id": "manifold", "type": "box", "x": 2, "y": 2, "z": 0, "dx": 5, "dy": 5, "dz": 2, "color": "#57534E" },
    { "id": "tank", "type": "cylinder", "x": 4.5, "y": 4.5, "z": 2, "r": 2.0, "dz": 8, "color": "#93C5FD", "opacity": 0.65 },
    { "id": "out_pipe", "type": "pipe", "from": [7, 4.5, 1.0], "to": [13, 4.5, 1.0], "r": 0.45, "color": "#C9963E" },
    { "id": "pressure_dial", "type": "gauge", "x": 9.5, "y": 2.5, "z": 3.5, "r": 1.4, "color": "#FAF8F5" }
  ],
  "callouts": [
    { "target": [4.5, 4.5, 8.5], "label_pos": [180, 150], "title": "Sight Cylinder", "detail": "Holds up to C tokens" },
    { "target": [11.5, 4.5, 1.0], "label_pos": [860, 420], "title": "Discharge Pipe", "detail": "Admitted traffic" }
  ]
}
```

---

## 4. Optional WebGL Shader Overlay Mode

When visualizing continuous media (steam, plasma, fluid turbulence, thermal heatmaps):
- Keep structural housings, shafts, gauges, and callouts in crisp vector `<svg>` on top.
- Mount an aligned transparent `<canvas id="shader-layer">` using the exact same `width`/`height` and `isoProject(x, y, z)` matrix directly behind translucent glass windows.
