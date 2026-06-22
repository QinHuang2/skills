---
name: logo-create-skill
description: Create premium transparent typographic title/logo images from only user-provided words or phrases. Use when the user submits words, Chinese/English titles, program names, brand words, concept words, or short slogans and wants Codex to generate one transparent PNG per text item with the text as the dominant custom-designed visual subject, following strict typography-first rules, semantic metaphor analysis, exact text rendering, and 1360x560 output validation.
---

# Logo Create Skill

## Overview

Create one transparent PNG per requested word or phrase. The user only needs to submit the target text; infer the rest. Treat the exact text as the product: the lettering must be the largest, clearest, most memorable visual subject, with every metaphor, ornament, and material choice serving the text.

Use this skill for title-logo style assets such as TV/film program names, campaign words, concept words, Chinese title marks, English title marks, and batch wordmark generation. Do not use it for generic app UI, ordinary posters, icons, or diagrams.

## Workflow

1. Read the user's exact words and preserve spelling/characters verbatim.
2. For each word/phrase, infer its semantic type, emotional pressure, cultural associations, core metaphor, visual movement, and best composition.
3. Read `references/generation-spec.md` before building prompts unless the user explicitly asks for a quick draft. This file contains the strict visual rules adapted from the original project `spec.md`.
4. Write a separate image-generation prompt for each phrase using `references/prompt-blueprint.md`.
5. Generate one image per phrase with the built-in `image_gen` tool.
6. Inspect each result for text accuracy, dominance, composition, and whether the background is truly transparent.
7. If the generated PNG lacks alpha or contains a checkerboard/flat removable background, run `scripts/finalize_transparent_png.py` to remove the background and resize/canvas-fit the final asset.
8. Save final deliverables into the current project, preferably `生成图片/` for Chinese projects or `generated-images/` otherwise.
9. Verify final files with `sips -g pixelWidth -g pixelHeight -g hasAlpha <files>` or an equivalent image inspection command.
10. Report final paths and mention any limitation, especially if a model misspelled text or if transparency required post-processing.

## Prompt Rules

- Put the exact text in a labeled `Text (verbatim)` line.
- State that the text must occupy more than 50% of the image area and be the first-read visual subject.
- Ask for custom lettering, not a default font.
- Use only a few metaphor elements, attached to or orbiting the text.
- Require no extra captions, no watermark, no logo, no QR code, no fake text, and no extra words.
- For Chinese, explicitly require correct Chinese characters, no fake Chinese, no missing strokes, and readable structure.
- For English/numbers, explicitly require exact spelling/numerals, readable spacing, and no extra letters.
- Request a transparent PNG, but assume the built-in image tool may output a checkerboard image; post-process when needed.

## Semantic Design Pass

Before prompting, decide:

- Is the phrase emotional, conceptual, object-based, historical, romantic, comic, technological, documentary, or mythic?
- Should the word feel gentle, sharp, solemn, dangerous, poetic, absurd, rational, luxurious, chaotic, or monumental?
- What is the deep metaphor beyond the obvious cliche?
- Should space expand, compress, rise, fall, orbit, fracture, converge, dissolve, or loop?
- Which ratio and layout best reinforces the phrase while still fitting the requested final canvas?

Avoid literal cliches unless the user asks for them. For example, do not reduce freedom to birds, love to hearts, technology to blue circuits, or historical trauma to explicit violence.

## Output Standard

Default final size is `1360x560` PNG with alpha unless the user provides another size. The final image must have:

- Exact readable text as the dominant subject.
- Transparent background.
- Strong custom typography.
- Limited, accurate metaphor elements.
- No extra text or watermark.
- Professional design density: powerful from far away, detailed up close.

## Batch Naming

For multiple phrases, name each output from the submitted phrase when filesystem-safe. If a phrase contains path separators or unsafe characters, replace them with hyphens while preserving the displayed text inside the image.

## Post-Processing

Use the bundled script when an image has no alpha channel or the model baked in a checkerboard background:

```bash
python3 logo-create-skill/scripts/finalize_transparent_png.py \
  --input /path/to/source.png \
  --output /path/to/final.png \
  --width 1360 \
  --height 560 \
  --remove-checkerboard
```

For a flat chroma-key background, use:

```bash
python3 logo-create-skill/scripts/finalize_transparent_png.py \
  --input /path/to/source.png \
  --output /path/to/final.png \
  --width 1360 \
  --height 560 \
  --key-color '#00ff00'
```

After post-processing, inspect at least one result visually and verify alpha with `sips`.
