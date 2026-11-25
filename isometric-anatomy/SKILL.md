---
name: isometric-anatomy
description: >-
  Explain abstract algorithms, system architectures, protocols, and mathematical
  models by building interactive isometric mechanical machine illustrations in
  standalone HTML/SVG/JS (with optional WebGL shader layers) rather than flat
  flowcharts. Use when the user wants an anatomical technical diagram, interactive
  mechanical metaphor, isometric architecture explainer, or visual mental model
  for how a system works under the hood.
---

# Isometric Anatomy

## Overview

Translate invisible software concepts, mathematical formulas, and distributed protocols into **tactile, working isometric machines**. Instead of generic rectangles and arrows, build precision instruments—brass manifolds, glass sight tubes, escapement ratchets, counterweight scales, gantry carriages, and analog gauges—driven by a real mathematical simulation in standalone HTML/SVG/JS.

Use this skill for technical blog figures, interactive system architecture explainers, algorithm visualizations, protocol state machines, and educational engineering plates.

## Workflow

1. **Model the Math First**: Before drawing a single polygon, write down the exact state variables, equations, invariants, and failure modes of the concept (e.g., arrival rate $\lambda$, capacity $C$, token level $b(t)$, drop threshold).
2. **Map Variables to Hardware**: Read `references/mechanical-metaphors.md` and assign every software state variable to a physical mechanism and readout (e.g., queue depth -> vertical glass sight cylinder; rate limit -> rotary needle valve; quorum -> weighted balance beam).
3. **Draft Isometric Geometry**: Read `references/isometric-spec.md` for true `30°` isometric projection, 4-tone surface lighting, and back-to-front painter's depth sorting. Use `scripts/iso_kit.py` to compile a declarative 3D JSON parts spec (`plate`, `box`, `cylinder`, `pipe`, `gauge`, `callout`) into an accurately projected, depth-sorted SVG or interactive HTML scaffold, then refine fine linkage details.
4. **Wire Live Simulation & Readouts**: Connect interactive controls (sliders, burst triggers, pause/step buttons) to a deterministic `requestAnimationFrame` physics/math loop that updates both the moving SVG groups (`transform="translate(...)"`) and framed tabular numeric readouts.
5. **Run Geometry & Layout Audit**: Execute `scripts/audit_figure.py` against the generated `.html` or `.svg` file to catch unclosed polygons, out-of-viewBox coordinates, colliding `<text>` callouts, or unwired controls.
6. **Verify Mechanical Honesty**: Inspect that no component floats unsupported in mid-air without a baseplate, stanchion, bracket, or shaft, and that motion direction matches causal flow.

## Hard Drafting Rules

- **Ban Box-and-Arrow Flowcharts**: Never draw flat rectangles labeled `Client -> API -> DB`. Every subsystem must have physical volume, mount points, and mechanical affordance.
- **Strict 4-Tone Isometric Lighting**: Light comes from top-left-front:
  - Top face (`z+`): lightest highlight (`+14%` luminance)
  - Left-front face (`y+`): base lit midtone (`0%`)
  - Right-front face (`x+`): core shadow (`-20%` luminance)
  - Cast shadow on baseplate (`z=0`): translucent dark grounding polygon
- **Painter's Depth Order**: Render baseplates and cast shadows first, then sort 3D solids strictly back-to-front by `(x + y)` and `z` so foreground mechanisms cleanly occlude rear housings.
- **Framed Engineering Plate Presentation**: Wrap every figure in an archival card (`#F5F1E8` warm vellum or `#0D131C` dark instrument slate) with title block, figure number (`FIG. 01`), live telemetry readouts, and interactive parameter sliders.

## Tooling & Validation

Compile a 3D isometric machine spec JSON into standalone interactive HTML or pure SVG:

```bash
python3 isometric-anatomy/scripts/iso_kit.py \
  --spec /path/to/machine-spec.json \
  --output /path/to/figure.html \
  --format html
```

Audit any generated HTML/SVG figure for geometric integrity and label collisions:

```bash
python3 isometric-anatomy/scripts/audit_figure.py \
  --input /path/to/figure.html
```

## Final QA

Accept the figure only when:

- `audit_figure.py` passes with zero degenerate polygons, viewBox overflows, or label overlaps.
- Adjusting any slider visibly changes the mechanical state (fluid height, piston stroke, valve angle, packet droplets, gauge needle) in real time according to the true underlying math.
- Every moving part is visibly mounted on a baseplate, rail, axle, or manifold—zero floating parts.
- Callout leader lines terminate cleanly on their target parts without crossing through unrelated text.
