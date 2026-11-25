# Brand Lock & Design Critique Protocol

Read this file whenever working with an established brand identity or performing final quality review before delivering an HTML artifact.

---

## 1. Five-Step Brand Asset Lock Protocol

When the user specifies a brand, company, website, or existing design palette, never improvise approximate colors across files. Lock them first:

1. **Identify**: Extract exact primary background, surface background, primary text, muted text, primary accent, secondary accent, border color, and font stack from user-supplied specs or assets.
2. **Verify Contrast**: Confirm primary text against background achieves **>= 4.5:1** contrast ratio (WCAG AA) and primary accent or display text achieves **>= 3.0:1**. If an accent fails text contrast on a light background, assign it to fills/rules and derive a darker text-safe shade.
3. **Tokenize**: Map all colors and spacing into CSS `:root` custom properties:
   - `--bg`, `--surface`, `--ink`, `--muted`, `--accent`, `--border`
4. **Freeze `brand-lock.json`**: Save a machine-readable lock file in the working folder:
   ```json
   {
     "brand_name": "Acme Studio",
     "tokens": {
       "--bg": "#F6F5F0",
       "--surface": "#FFFFFF",
       "--ink": "#141413",
       "--muted": "#5E5D59",
       "--accent": "#E03C28",
       "--border": "#D8D6CE"
     },
     "heading_font": "'Instrument Serif', 'Noto Serif SC', serif",
     "body_font": "'Plus Jakarta Sans', 'PingFang SC', sans-serif"
   }
   ```
5. **Enforce via Linter**: Pass `--brand-lock brand-lock.json` to `scripts/design_lint.py` so every deliverable is automatically checked against the frozen tokens.

---

## 2. Anti-AI-Slop Checklist (What Never to Ship)

Reject and redesign immediately if any of these patterns appear:

- **Purple-Indigo SaaS Haze**: `#6366F1` / `#8B5CF6` glowing radial blobs over `#0F172A` unless explicitly mandated by brand lock.
- **Symmetric 3-Box Echo**: Three identical rounded cards in a row, each starting with a colored circle icon, a 3-word bold title, and two lines of centered gray text.
- **Placeholder Laziness**: `Lorem ipsum`, `Feature 1 / Feature 2`, `John Doe`, `$99/mo` generic dummy copy, or broken `https://via.placeholder.com` image tags.
- **Emoji-as-Icon Crutch**: Sprinkling `🚀 ✨ 💡 🔥 🎯` inside UI cards, buttons, or slide headers instead of clean inline SVG icons, typographic numerals (`01`, `02`), or geometric markers.
- **Unbounded Line Length**: Body paragraphs wider than `68ch` stretching edge-to-edge across `1440px` viewports.
- **Flat Hierarchy**: Headlines (`28px`) barely larger than subheads (`20px`) and body (`16px`). Aim for a decisive scale ratio (e.g., `64px` display / `20px` lead / `15px` body / `12px` tracked label).

---

## 3. HTML Slide Deck Authoring Spec (`<section data-slide>`)

When building presentations so that both browser viewing and `scripts/html_slides_to_pptx.py` export work cleanly:

- Wrap each slide in `<section data-slide data-layout="hero|split|metrics|bullets" data-bg="#F6F5F0" data-ink="#141413" data-accent="#E03C28">`.
- Inside each `<section data-slide>`, use semantic markers:
  - `<span data-kicker>` for section index / eyebrow tag (e.g. `01 / MARKET SHIFT`)
  - `<h1>` or `<h2>` for the single slide headline
  - `<p data-lead>` for the key summary statement
  - `<ul><li>...</li></ul>` for structured points (keep to <= 4 concise items per slide)
  - `<div data-metric><strong data-value>94.2%</strong><span data-label>Retention at Day 30</span></div>` for KPI callout tiles
  - `<footer data-footnote>` for source attribution or slide footer
- Include keyboard navigation (`ArrowRight` / `ArrowLeft` / `Space`) in the HTML stage so the HTML file doubles as an instant live presentation deck.

---

## 4. Pre-Handoff Critique Rubric

Score the artifact across 5 axes before returning it to the user:

1. **Squint Test**: At 25% zoom, is there one unmistakable focal anchor per viewport/slide?
2. **Whitespace Discipline**: Does negative space actively frame the content (>= 30% open canvas)?
3. **Alignment Spine**: Do kickers, headlines, body blocks, and footers lock onto shared vertical grid lines?
4. **CJK / Multilingual Polish**: For Chinese copy, is `line-height` set to `1.65–1.8` for body, `1.15–1.28` for headlines, with proper punctuation spacing and no single-character widow lines?
5. **Technical Cleanliness**: Zero broken external image URLs, valid inline SVGs, clean `design_lint.py` pass.
