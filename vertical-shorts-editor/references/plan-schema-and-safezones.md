# `plan.json` Blueprint & 9:16 Safe-Zone Specification

Read this specification before generating or modifying `plan.json` for a vertical short.

---

## 1. Universal 9:16 Safe-Zone Map (`1080 x 1920`)

Short-form platforms (TikTok, Instagram Reels, YouTube Shorts, 抖音, 视频号) overlay persistent UI chrome on top of the video canvas. `validate_plan.py` enforces these exact pixel boundaries:

```text
+---------------------------------------+ (0, 0)
|        TOP UI CHROME (y < 180)        |  <- Search bar, Live/Following tabs
+---------------------------------------+ y = 180
|   UPPER GRAPHIC SAFE ZONE (180..420)  |  <- Ideal for Hook Banner / Stat Cards
+---------------------------------------+ y = 420
|                                 | R   |
|     SPEAKER FACE BOX            | A   |  <- Default face box: x=300..780, y=420..940
|     (Avoid covering eyes/mouth) | I   |  <- Right rail (x > 900, y = 820..1620):
|                                 | L   |     Avatar, Like, Comment, Share, Music disc
+---------------------------------+     | y = 1240
|   CAPTION SAFE ZONE             |     |  <- Ideal x=90..890, y=1260..1540
|   (x: 80..895, y: 1240..1580)   |     |
+---------------------------------------+ y = 1580
|      BOTTOM UI CHROME (y > 1580)      |  <- Handle, description, audio marquee, scrub bar
+---------------------------------------+ (1080, 1920)
```

---

## 2. Complete `plan.json` Schema

```json
{
  "title": "Why 90% of Shorts Lose Viewers at Second 2",
  "canvas": { "width": 1080, "height": 1920, "fps": 30 },
  "duration": 18.0,
  "brand": {
    "primary": "#FF5500",
    "text": "#FFFFFF",
    "highlight": "#FACC15",
    "bg_pill": "#111114"
  },
  "speakerFaceBox": { "x": 300, "y": 420, "w": 480, "h": 520 },
  "hook": {
    "start": 0.0,
    "end": 2.8,
    "kicker": "RETENTION RULE #1",
    "headline": "Stop Wasting Frame Zero",
    "box": { "x": 90, "y": 220, "w": 800, "h": 170 }
  },
  "cuts": [
    { "start": 0.0, "end": 3.6, "zoom": 1.08, "focusY": 0.42 },
    { "start": 3.6, "end": 7.8, "zoom": 1.00, "focusY": 0.45 },
    { "start": 7.8, "end": 12.4, "zoom": 1.14, "focusY": 0.40 },
    { "start": 12.4, "end": 18.0, "zoom": 1.00, "focusY": 0.45 }
  ],
  "broll": [
    { "start": 5.2, "end": 7.6, "path": "./assets/analytics_scroll.mp4", "label": "Retention graph drop-off" }
  ],
  "cards": [
    {
      "id": "card_stat",
      "type": "metric-badge",
      "start": 8.0,
      "end": 11.5,
      "title": "+42% Watch Time",
      "subtitle": "When hook lands < 1.8s",
      "box": { "x": 90, "y": 230, "w": 780, "h": 160 }
    }
  ],
  "captions": [
    {
      "start": 0.05,
      "end": 1.85,
      "text": "Most creators lose viewers",
      "highlightWord": "lose",
      "box": { "x": 90, "y": 1340, "w": 800, "h": 150 },
      "words": [
        { "word": "Most", "start": 0.05, "end": 0.40 },
        { "word": "creators", "start": 0.40, "end": 0.95 },
        { "word": "lose", "start": 0.95, "end": 1.35 },
        { "word": "viewers", "start": 1.35, "end": 1.85 }
      ]
    }
  ]
}
```

---

## 3. Pacing & Rhythm Heuristics

- **Hook Density**: `hook.start` MUST be `<= 0.2s` and `hook.end` between `1.8s` and `3.5s`.
- **Cut Cadence**: Aim for a visual state change (zoom cut, B-roll cutaway, or scene card entrance) every **`2.8s – 5.5s`**. Flag any static uncut stretch `> 7.5s`.
- **Zoom Restraint**: Keep talking-head punch-ins between `1.08x` and `1.18x`—larger digital crops degrade facial sharpness and feel jarring.
