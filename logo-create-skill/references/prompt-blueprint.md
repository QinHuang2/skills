# Typographic Logo Prompt Blueprint

Use this reference after reading `generation-spec.md`. The user may provide only raw words/phrases; infer all visual direction from the text.

## Base Prompt Structure

```text
Use case: logo-brand / typographic concept art.
Asset type: transparent PNG title/logo, final canvas 1360px wide x 560px tall unless the user asks for another size.
Primary request: Create a top-tier typographic concept image for the submitted title/word.
Text (verbatim, exact characters): "<TEXT>"

Core rule: "<TEXT>" must be the largest, strongest, first-read visual subject, occupying more than 50-60% of the image area. The text must be perfectly readable. No extra words.

Meaning and metaphor: <semantic interpretation, emotional type, deep metaphor, non-cliche symbols>.
Style: <style derived from meaning, not a fixed template>.
Composition: choose the internal composition ratio from the word's spatial metaphor, but export on a 1360x560 transparent canvas. Large custom lettering dominates; auxiliary elements must remain secondary.
Color palette: <meaning-driven colors, restrained and premium>.
Materials/textures: <meaning-driven typography material; avoid cheap 3D>.
Constraints: transparent background, exact text only, no watermark, no logo, no QR code, no extra caption, no fake characters, no misspelling, no background rectangle, no poster scene.
```

## Hard Rules

- The text is the first hierarchy. Metaphor elements are second. Atmosphere and texture are third.
- The image is not a normal poster with a title on top; it is a custom typography asset.
- Do not add unrelated objects, slogans, signatures, UI labels, or credits.
- Do not let people, buildings, props, scenery, lighting, or background overpower the word.
- Use visual metaphor through the letterform itself: compression, stretching, fracture, negative space, growth, orbit, restraint, release, erosion, engraving, transparency, or rhythm.
- Keep the text readable even when it is stylized.

## Chinese Text Rules

- Preserve each Chinese character exactly.
- Require no fake Chinese, no missing strokes, no extra strokes, no garbled pseudo-characters.
- Let custom structure affect weight, rhythm, material, and negative space, but not character identity.
- If the model misspells a character, regenerate with a shorter, stricter prompt focused on exact text.

## English / Number Rules

- Preserve exact spelling, capitalization, and numerals.
- Control spacing, baseline, weight, and negative space like a premium title mark.
- Avoid adding subtitle words, random serial numbers, or decorative microtext unless the user explicitly requests it.

## Visual Direction Heuristics

- Strategic/intellectual words: grids, coordinates, probability nodes, measured cuts, restrained metallic accents.
- Comic/exclamation words: kinetic weight, elastic rhythm, controlled burst fragments, pop colors with premium restraint.
- Historical/documentary titles: archival marks, evidence codes, worn ink, brutalist numerals, solemn restraint; avoid explicit violence.
- Romantic/regret phrases: elongated rhythm, near-crossing lines, soft temporal arcs, warm ink, delicate metallic accents; avoid hearts unless requested.
- Control/order: frames, measurements, permissions, grid pressure, cold clarity.
- Freedom/escape: opened frames, expansion, loosened gravity, outward motion.
- Anxiety: compressed space, misaligned repeats, dense information, tense shadows.
- Time: ghosting, repetition, erosion, paper, delay, irreversible traces.
- Depth: nested layers, apertures, shadow gradients, internal space.

Do not hard-code these examples into outputs. They are heuristics only; every submitted text needs its own semantic pass.

## Final QA

Check:

- Exact text is readable at a glance.
- No extra text is present.
- Typography dominates the canvas.
- Metaphor elements serve the typography.
- Final PNG has alpha transparency.
- Final size matches the requested size.
