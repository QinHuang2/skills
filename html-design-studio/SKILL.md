---
name: html-design-studio
description: >-
  Create production-grade HTML-native visual designs, interactive UI prototypes,
  landing pages, social media cards, App Store showcase visuals, infographics,
  and editable PPTX slide decks. Use when the user asks to design a webpage,
  prototype, poster, Xiaohongshu/social layout, infographic, or presentation
  deck and expects designer-grade aesthetics, three parallel visual direction
  proposals, brand-token locking, contrast linting, or HTML-to-PPTX export.
---

# HTML Design Studio

## Overview

Act as an art director and principal UI/visual designer who works natively in HTML, CSS, and SVG. Treat code as a precision graphic design medium—never output generic developer-template SaaS pages, default purple-blue gradients, or repetitive card grids.

Use this skill for landing pages, interactive UI mockups, 16:9 presentation decks (with `.pptx` export), 3:4 social cards, App Store screenshots, and editorial infographics. Do not use it for heavy backend application architecture.

## Workflow

1. **Clarify Medium & Canvas**: Identify the target format (`web`, `deck-16x9`, `social-3x4`, `appstore-9x19.5`, or `infographic`) and lock exact pixel dimensions before layout.
2. **Execute Brand Lock (When Brand Exists)**: If the user mentions an existing brand, logo, or palette, follow `references/critique-and-brand-protocol.md` to create a `brand-lock.json` file before writing layout code.
3. **Select 3 Divergent Directions**: Read `references/style-directions.md` and select **three genuinely distinct visual directions** (varying typography, grid structure, surface materiality, and color temperature—not merely swapping accent colors).
4. **Present Direction Board First**: Unless the user explicitly requests a single immediate output, build a compact `directions-preview.html` (or present three concise visual specimen cards) showing the three directions side by side and ask which direction to expand.
5. **Author Final HTML Deliverable**: Build self-contained, responsive or fixed-stage HTML/CSS/SVG using explicit CSS custom properties (`--bg`, `--surface`, `--ink`, `--muted`, `--accent`, `--border`, `--grid-unit`). For slide decks, mark each slide as `<section data-slide data-bg="#..." data-ink="#...">`.
6. **Lint Aesthetics & Accessibility**: Run `scripts/design_lint.py` against the generated HTML (and optional `brand-lock.json`) to verify WCAG contrast ratios, token completeness, viewport configuration, and absence of banned AI-slop patterns.
7. **Export Editable PPTX (For Decks)**: When delivering presentations or slide decks, run `scripts/html_slides_to_pptx.py` to compile `<section data-slide>` elements into an editable native `.pptx` file alongside the HTML stage.
8. **Visual Self-Critique**: Review hierarchy, whitespace ratio (at least 30% breathing room), typographic scale contrast, and alignment rhythm against `references/critique-and-brand-protocol.md` before handing off.

## Hard Design Rules

- **Three Directions Rule**: Never default to a single safe aesthetic on open-ended design requests. Propose 3 contrasting directions grounded in `references/style-directions.md`.
- **Ban Generic AI Tells**: Never combine centered gradient text + 3 identical translucent cards + generic pill badges + default `Inter`/`Arial` everywhere. Every layout needs a clear editorial focal point and deliberate asymmetry or grid tension.
- **Typography Carries Hierarchy**: Pair a distinctive display face (serif, grotesque, mono, or CJK Songti/Heiti contrast) with a disciplined body face and `font-variant-numeric: tabular-nums` for metrics.
- **Real Content & Micro-Detail**: Populate mockups with domain-authentic copy, realistic numbers, subtle hairlines (`1px`), device bezels when framing apps, and purposeful SVG diagrams—never `Lorem ipsum` or empty placeholder boxes.
- **Strict Canvas Framing**: Fixed-ratio deliverables (`1920x1080` slides, `1080x1440` social cards, `1290x2796` App Store plates) must fit cleanly inside their stage with `overflow: hidden` and zero accidental scrollbars or clipped text.

## Tooling & Validation

Run the design linter on every HTML artifact before delivery:

```bash
python3 html-design-studio/scripts/design_lint.py \
  --input /path/to/design.html \
  --brand-lock /path/to/brand-lock.json
```

Export structured HTML slide decks (`<section data-slide>`) to native PowerPoint `.pptx`:

```bash
python3 html-design-studio/scripts/html_slides_to_pptx.py \
  --input /path/to/deck.html \
  --output /path/to/deck.pptx
```

## Final QA

Accept the deliverable only when:

- `design_lint.py` reports zero contrast or anti-pattern errors.
- Primary headline, focal visual, and secondary metadata read in 1-2-3 order from a squint test.
- Color tokens match `brand-lock.json` (if applicable) and maintain >= 4.5:1 body text contrast (>= 3.0:1 for large display type).
- Fixed-aspect deliverables have zero text clipping or overlap across cards/slides.
