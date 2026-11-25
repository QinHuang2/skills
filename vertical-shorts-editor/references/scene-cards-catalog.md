# 9:16 Motion Scene Cards Catalog

Use these modular graphic card archetypes inside `plan.json` (`cards[]`) or Remotion JSX components to punctuate spoken points without cluttering the talking head.

---

## 1. Upper-Zone Overlay Cards (Keep Speaker Visible)

Place inside `x: 80..880, y: 200..400` so the speaker's face (`y: 420..940`) and captions (`y: 1260..1540`) stay completely clear:

1. **`hook-banner`**: High-contrast pill eyebrow + bold 4–6 word punchline with rapid expo-out slide-down at `t = 0.0s`.
2. **`metric-badge`**: Tabular hero stat (`+42%`, `3.4x`, `$120K`) on the left + 2-line context label on the right.
3. **`step-pill`**: Indexed progression tracker (`STEP 02 / 03 — Validate Safe Zones`) locking structure across listicle shorts.
4. **`myth-fact`**: Red strikethrough stamp (`MYTH`) flipping at beat onset into emerald badge (`FACT`).
5. **`source-citation`**: Newspaper/paper masthead strip (`Nature, 2026` / `GitHub Benchmark`) lending instant authority to claims.
6. **`warning-callout`**: Amber/black diagonal-accent alert bar highlighting a common mistake or anti-pattern.

---

## 2. Full / Split Cutaway Scene Cards (`2.0s – 4.0s` Beats)

Use when visually replacing the talking head for a brief high-impact diagram (treat like graphic B-roll, keeping `x <= 890` and `y: 220..1220` so captions underneath continue seamlessly):

7. **`versus-split`**: Vertical two-card stack (`BEFORE` muted slate top vs `AFTER` accented bottom) with delta badge.
8. **`timeline-stepper`**: Vertical 3-node spine lighting up sequentially with spoken timestamps.
9. **`code-snippet`**: Clean dark terminal card (`6–8` lines max, `28px` monospace) highlighting a single active line.
10. **`chat-exchange`**: Two iMessage/WeChat-style bubbles popping in with `90ms` spring stagger to dramatize user/client dialogue.
11. **`bar-comparison`**: Two horizontal animated progress bars comparing baseline vs optimized performance.
12. **`checklist-stamp`**: Three concise checklist rows checking off (`[✓]`) one by one on word triggers.

---

## 3. Karaoke Caption Styling Presets

| Preset | Base Text | Active Spoken Word | Shadow / Backing | Best For |
| :--- | :--- | :--- | :--- | :--- |
| **Creator Pop** | `#FFFFFF` (`64px` Heavy) | `#FACC15` (`112%` scale pop) | `4px` `#000000` outline + drop shadow | High-energy tech, creator tips, marketing |
| **Editorial Pill** | `#FAFAFA` (`54px` Bold) | `#FFFFFF` on `#FF5500` pill | Frosted `#111114` @ 86% rounded bar | Essays, founders, finance, design breakdowns |
| **Minimal Clean** | `#F8FAFC` (`52px` SemiBold) | `#38BDF8` accent tint | Subtle `2px` dark shadow | Calm educational, documentary, interviews |
