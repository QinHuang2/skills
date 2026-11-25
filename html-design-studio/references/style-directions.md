# HTML-Native Style Directions Catalog

Select **three genuinely divergent directions** from different families below whenever exploring visual direction for a user request. Adapt colors and typography to the subject matter rather than copying hex values blindly.

---

## Family A: Editorial & Print Systems

### 1. Swiss International Grid
- **Mood**: Rational, authoritative, architectural clarity.
- **Palette**: Warm alabaster `#F6F5F0`, carbon ink `#141413`, signal vermilion `#E03C28`, hairline `#D8D6CE`.
- **Typography**: Tight neo-grotesque headlines (`-0.03em` tracking) + crisp tabular numbers + exposed 12-column hairline rules.
- **Best For**: Architecture portfolios, B2B flagship landing pages, annual reports, keynote decks.

### 2. Broadsheet Literary Editorial
- **Mood**: Intellectual, unhurried, magazine-feature gravitas.
- **Palette**: Newsprint cream `#F3EFE6`, deep espresso `#1C1917`, burgundy accent `#8C2D19`, muted stone `#78716C`.
- **Typography**: High-contrast serif display (e.g., `Playfair Display` / `Noto Serif SC`) paired with compact sans-serif captions and drop caps.
- **Best For**: Essays, cultural exhibitions, research summaries, Xiaohongshu deep-read carousels.

### 3. Risograph Two-Tone Print
- **Mood**: Tactile, indie-studio, graphic poster punch.
- **Palette**: Uncoated paper `#FAF6EE`, cobalt ink `#1D4ED8`, fluorescent coral `#FF5A36` (multiply blend accents).
- **Typography**: Heavy condensed display + monospaced catalog indices (`[01]`, `[02]`) + subtle SVG noise grain.
- **Best For**: Event posters, creator launches, music/podcast visuals, bold social cards.

### 4. East-Asian Poetic Blank Space (留白宋韵)
- **Mood**: Contemplative, refined, museum-catalog serenity.
- **Palette**: Xuan rice paper `#F7F4EC`, pine soot `#22201E`, cinnabar seal `#B83B2A`, celadon mist `#94A39B`.
- **Typography**: Sculpted Songti/Mincho display (`Noto Serif SC` / `Songti SC`), vertical index callouts (`writing-mode: vertical-rl`), >= 45% negative space.
- **Best For**: Tea/craft/luxury branding, cultural decks, minimalist book/topic breakdowns.

---

## Family B: Technical & Precision Instruments

### 5. Teenage-Engineering Tactile Hardware
- **Mood**: Playful industrial precision, physical module clarity.
- **Palette**: Anodized light gray `#EAEAE6`, matte charcoal `#1A1A1A`, safety orange `#FF5500`, LED mint `#10B981`, recessed bezel `#D4D4CE`.
- **Typography**: Technical geometric sans + strict monospace parameter labels (`11px` uppercase, `0.08em` tracking) + chamfered or `4px`-radius module bays.
- **Best For**: Developer tools, AI products, audio/creative apps, interactive control prototypes.

### 6. Dark Observatory / Telemetry Console
- **Mood**: High-density mission control, zero-glare analytical focus.
- **Palette**: Obsidian `#0B0E14`, slate panel `#131822`, crisp ice `#E6EDF3`, amber alert `#F59E0B`, cyan trace `#22D3EE`, border `#232B3A`.
- **Typography**: Monospace metrics (`JetBrains Mono` / `SF Mono`) + geometric sans headers + crisp `1px` coordinate crosshairs.
- **Best For**: FinTech dashboards, observability tools, benchmark infographics, technical architecture decks.

### 7. Blueprint Schematic Specification
- **Mood**: Engineering patent sheet, transparent structural honesty.
- **Palette**: Prussian blueprint `#0F2942` (or drafting vellum `#F2F6FA`), drafting white `#F8FAFC` (or `#0F2942`), dimension cyan `#38BDF8`, callout gold `#FBBF24`.
- **Typography**: Technical monospace + numbered dimension callouts, leader lines, scale bars, and title block metadata in the bottom-right corner.
- **Best For**: System explainers, hardware specs, API flows, product teardown infographics.

### 8. Monochrome Linear Minimalist
- **Mood**: Whisper-quiet luxury software, razor-sharp hierarchy.
- **Palette**: Pure obsidian `#09090B`, zinc surface `#121215`, zinc border `#27272A`, pure white `#FAFAFA`, muted zinc `#A1A1AA`, single restrained ice accent `#E4E4E7`.
- **Typography**: Tight display tracking, generous vertical rhythm (`96px+` section padding), hairline borders with subtle top-edge specular highlight.
- **Best For**: Flagship software launches, developer CLI/SDK pages, executive pitch decks.

---

## Family C: Expressive, Consumer & Mobile Showcases

### 9. Warm Clay & Organic Botanical
- **Mood**: Human-centric, approachable, wellness & lifestyle warmth.
- **Palette**: Oat milk `#F8F3EB`, terracotta `#C85A32`, olive leaf `#3F523A`, warm walnut `#2C221E`, sand card `#EFE7DA`.
- **Typography**: Soft humanist serif + rounded geometric sans + generous pill tags and soft `24px` radii.
- **Best For**: Health/wellness apps, consumer lifestyle products, community platforms, App Store story cards.

### 10. Neo-Brutalist High-Contrast Poster
- **Mood**: Unapologetic, kinetic, street-poster immediacy.
- **Palette**: Acid yellow `#F4FF52` or stark white `#FFFFFF`, pure black `#000000`, electric cobalt `#2563EB`, hard `2px solid #000` borders and `4px 4px 0 #000` offset shadows.
- **Typography**: Extra-bold grotesque headlines, sticker callouts, stark tabular comparison matrices.
- **Best For**: Gen-Z campaigns, hackathons, viral social infographics, bold pricing/feature comparisons.

### 11. Editorial Bento Showcase
- **Mood**: Apple-keynote summary clarity, modular scannability.
- **Palette**: Soft studio gray `#F5F5F7`, pure white tiles `#FFFFFF`, carbon `#1D1D1F`, cobalt `#0066CC`, subtle tile border `#E5E5EA`.
- **Typography**: Clean display grotesque (`SF Pro Display` / `Plus Jakarta Sans`), hero metric numbers (`64px–96px`), asymmetric `4x3` bento spans (never equal-sized boxes).
- **Best For**: Product feature summaries, release notes, slide summary plates, App Store feature overviews.

### 12. Luxury Maison Atelier
- **Mood**: High-fashion lookbook, restrained ceremonial elegance.
- **Palette**: Ivory parchment `#FAF8F5`, obsidian `#111111`, champagne brass `#B08D57`, warm taupe `#8A8178`.
- **Typography**: Tall hairline serif display, wide-tracked uppercase micro-labels (`0.18em`), thin vertical dividers, abundant margin framing.
- **Best For**: Jewelry/fashion/hospitality brands, premium invitations, flagship brand books.

---

## Canvas & Aspect-Ratio Matrix

| Deliverable Type | Standard Canvas | Layout Grid & Rules |
| :--- | :--- | :--- |
| **Responsive Web / Landing** | Fluid (`max-width: 1280px` container) | 12-column CSS grid, mobile breakpoint at `768px`, generous `80px–140px` vertical section rhythm. |
| **Slide Deck (`deck-16x9`)** | `1920x1080` per `<section data-slide>` | Max 1 core takeaway per slide, min `28px` body text, `56px–96px` headlines, `80px` safe outer padding. |
| **Social / Xiaohongshu (`social-3x4`)** | `1080x1440` per card | Cover card has >= 50% headline/focal weight; inner cards cap at 3 bullet blocks with bold visual anchors. |
| **App Store Plate (`appstore-9x19.5`)** | `1290x2796` (`430x932` @ 3x) | Top 32% bold benefit headline (`72px+` equivalent), bottom 68% angled or centered device bezel framing real UI. |
| **Vertical Infographic** | `1200px` wide x variable height | Numbered narrative spine, alternating chart/diagram modules, footer source/methodology bar. |
