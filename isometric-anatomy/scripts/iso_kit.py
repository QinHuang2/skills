#!/usr/bin/env python3
"""Compile declarative 3D isometric machine specifications into depth-sorted 4-tone SVG or standalone interactive HTML."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from xml.sax.saxutils import escape

COS30 = math.cos(math.radians(30.0))
SIN30 = 0.5
SQRT_3_2 = math.sqrt(1.5)
SQRT_1_2 = math.sqrt(0.5)

THEMES = {
    "vellum": {
        "bg": "#F5F1E8",
        "card": "#FAF7F0",
        "ink": "#1C1917",
        "muted": "#6B645C",
        "accent": "#C95B3C",
        "border": "#D6CEBF",
        "shadow": "rgba(28, 25, 23, 0.12)",
    },
    "lab": {
        "bg": "#F1F5F9",
        "card": "#FFFFFF",
        "ink": "#0F172A",
        "muted": "#64748B",
        "accent": "#2563EB",
        "border": "#CBD5E1",
        "shadow": "rgba(15, 23, 42, 0.12)",
    },
    "dark": {
        "bg": "#0B1017",
        "card": "#111827",
        "ink": "#F8FAFC",
        "muted": "#94A3B8",
        "accent": "#22D3EE",
        "border": "#1E293B",
        "shadow": "rgba(0, 0, 0, 0.38)",
    },
}


def adjust_hex(hex_color: str, factor: float) -> str:
    h = hex_color.strip().lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    if factor >= 0:
        r = int(r + (255 - r) * factor)
        g = int(g + (255 - g) * factor)
        b = int(b + (255 - b) * factor)
    else:
        r = int(r * (1.0 + factor))
        g = int(g * (1.0 + factor))
        b = int(b * (1.0 + factor))
    return f"#{max(0,min(255,r)):02X}{max(0,min(255,g)):02X}{max(0,min(255,b)):02X}"


def iso_pt(x: float, y: float, z: float, ox: float, oy: float, scale: float) -> tuple[float, float]:
    sx = ox + (x - y) * COS30 * scale
    sy = oy + (x + y) * SIN30 * scale - z * scale
    return round(sx, 2), round(sy, 2)


def fmt_pts(pts: list[tuple[float, float]]) -> str:
    return " ".join(f"{x},{y}" for x, y in pts)


def part_depth(part: dict) -> float:
    ptype = part.get("type", "box")
    if ptype in ("plate", "box"):
        cx = float(part["x"]) + float(part["dx"]) * 0.5
        cy = float(part["y"]) + float(part["dy"]) * 0.5
        cz = float(part["z"]) + float(part["dz"]) * 0.5
        if ptype == "plate":
            return -1000.0 + cz
        return cx + cy + cz * 0.02
    if ptype in ("cylinder", "gauge"):
        return float(part["x"]) + float(part["y"]) + float(part["z"]) * 0.02
    if ptype == "pipe":
        p0, p1 = part["from"], part["to"]
        return ((p0[0] + p1[0]) + (p0[1] + p1[1])) * 0.5 + ((p0[2] + p1[2]) * 0.01)
    return 0.0


def render_box(part: dict, ox: float, oy: float, scale: float, stroke: str) -> str:
    x, y, z = float(part["x"]), float(part["y"]), float(part["z"])
    dx, dy, dz = float(part["dx"]), float(part["dy"]), float(part["dz"])
    base = part.get("color", "#8A8178")
    opacity = float(part.get("opacity", 1.0))
    pid = escape(str(part.get("id", "box")))

    top_c = adjust_hex(base, 0.16)
    left_c = base
    right_c = adjust_hex(base, -0.22)

    # Top face (z + dz)
    t0 = iso_pt(x, y, z + dz, ox, oy, scale)
    t1 = iso_pt(x + dx, y, z + dz, ox, oy, scale)
    t2 = iso_pt(x + dx, y + dy, z + dz, ox, oy, scale)
    t3 = iso_pt(x, y + dy, z + dz, ox, oy, scale)

    # Bottom front-visible vertices (z)
    b1 = iso_pt(x + dx, y, z, ox, oy, scale)
    b2 = iso_pt(x + dx, y + dy, z, ox, oy, scale)
    b3 = iso_pt(x, y + dy, z, ox, oy, scale)

    op_attr = f' opacity="{opacity}"' if opacity < 1.0 else ""
    return (
        f'<g id="part-{pid}" data-part="{pid}"{op_attr} stroke="{stroke}" stroke-width="1.15" stroke-linejoin="round">'
        f'<polygon points="{fmt_pts([t3, t2, b2, b3])}" fill="{left_c}"/>'
        f'<polygon points="{fmt_pts([t2, t1, b1, b2])}" fill="{right_c}"/>'
        f'<polygon points="{fmt_pts([t0, t1, t2, t3])}" fill="{top_c}"/>'
        f"</g>"
    )


def render_cylinder(part: dict, ox: float, oy: float, scale: float, stroke: str) -> str:
    x, y, z = float(part["x"]), float(part["y"]), float(part["z"])
    r = float(part.get("r", 1.5))
    dz = float(part.get("dz", 4.0))
    base = part.get("color", "#93C5FD")
    opacity = float(part.get("opacity", 1.0))
    pid = escape(str(part.get("id", "cyl")))

    rx = round(r * scale * SQRT_3_2, 2)
    ry = round(r * scale * SQRT_1_2, 2)
    bot_cx, bot_cy = iso_pt(x, y, z, ox, oy, scale)
    top_cx, top_cy = iso_pt(x, y, z + dz, ox, oy, scale)

    top_c = adjust_hex(base, 0.18)
    body_c = adjust_hex(base, -0.08)
    op_attr = f' opacity="{opacity}"' if opacity < 1.0 else ""

    path_d = (
        f"M {top_cx - rx},{top_cy} "
        f"L {bot_cx - rx},{bot_cy} "
        f"A {rx},{ry} 0 0 0 {bot_cx + rx},{bot_cy} "
        f"L {top_cx + rx},{top_cy} "
        f"A {rx},{ry} 0 0 1 {top_cx - rx},{top_cy} Z"
    )
    return (
        f'<g id="part-{pid}" data-part="{pid}"{op_attr} stroke="{stroke}" stroke-width="1.15" stroke-linejoin="round">'
        f'<path d="{path_d}" fill="{body_c}"/>'
        f'<ellipse cx="{top_cx}" cy="{top_cy}" rx="{rx}" ry="{ry}" fill="{top_c}"/>'
        f"</g>"
    )


def render_pipe(part: dict, ox: float, oy: float, scale: float, stroke: str) -> str:
    p0, p1 = part["from"], part["to"]
    r = float(part.get("r", 0.4))
    base = part.get("color", "#C9963E")
    pid = escape(str(part.get("id", "pipe")))
    s0 = iso_pt(float(p0[0]), float(p0[1]), float(p0[2]), ox, oy, scale)
    s1 = iso_pt(float(p1[0]), float(p1[1]), float(p1[2]), ox, oy, scale)
    w = max(3.0, round(r * scale * 1.8, 2))
    hi = adjust_hex(base, 0.25)
    return (
        f'<g id="part-{pid}" data-part="{pid}" stroke-linecap="round">'
        f'<line x1="{s0[0]}" y1="{s0[1]}" x2="{s1[0]}" y2="{s1[1]}" stroke="{stroke}" stroke-width="{w + 2.4}"/>'
        f'<line x1="{s0[0]}" y1="{s0[1]}" x2="{s1[0]}" y2="{s1[1]}" stroke="{base}" stroke-width="{w}"/>'
        f'<line x1="{s0[0]}" y1="{s0[1] - w*0.18:.2f}" x2="{s1[0]}" y2="{s1[1] - w*0.18:.2f}" stroke="{hi}" stroke-width="{max(1.2, w*0.25):.2f}"/>'
        f"</g>"
    )


def render_gauge(part: dict, ox: float, oy: float, scale: float, stroke: str, accent: str) -> str:
    x, y, z = float(part["x"]), float(part["y"]), float(part["z"])
    r = float(part.get("r", 1.3))
    face = part.get("color", "#FAF8F5")
    pid = escape(str(part.get("id", "gauge")))
    cx, cy = iso_pt(x, y, z, ox, oy, scale)
    pr = round(r * scale, 2)
    nx = round(cx + pr * 0.48, 2)
    ny = round(cy - pr * 0.42, 2)
    return (
        f'<g id="part-{pid}" data-part="{pid}">'
        f'<circle cx="{cx}" cy="{cy}" r="{pr + 2.5}" fill="#57534E" stroke="{stroke}" stroke-width="1.2"/>'
        f'<circle cx="{cx}" cy="{cy}" r="{pr}" fill="{face}" stroke="{stroke}" stroke-width="1.0"/>'
        f'<line id="needle-{pid}" x1="{cx}" y1="{cy}" x2="{nx}" y2="{ny}" stroke="{accent}" stroke-width="2.2" stroke-linecap="round"/>'
        f'<circle cx="{cx}" cy="{cy}" r="2.6" fill="{stroke}"/>'
        f"</g>"
    )


def render_callout(c: dict, ox: float, oy: float, scale: float, theme: dict, idx: int) -> str:
    tx, ty, tz = [float(v) for v in c["target"]]
    px, py = iso_pt(tx, ty, tz, ox, oy, scale)
    lx, ly = [float(v) for v in c["label_pos"]]
    elbow_x = round(lx + (18 if lx > px else -18), 2)
    align = "start" if lx >= px else "end"
    title = escape(str(c.get("title", f"Part {idx}")))
    detail = escape(str(c.get("detail", "")))
    return (
        f'<g class="callout" data-callout="{idx}">'
        f'<polyline points="{px},{py} {elbow_x},{ly} {lx},{ly}" fill="none" stroke="{theme["ink"]}" stroke-width="1.1" stroke-dasharray="3,2"/>'
        f'<circle cx="{px}" cy="{py}" r="3.2" fill="{theme["accent"]}" stroke="{theme["card"]}" stroke-width="1.2"/>'
        f'<text x="{lx}" y="{ly - 6}" text-anchor="{align}" fill="{theme["ink"]}" font-size="13" font-weight="700">{title}</text>'
        f'<text x="{lx}" y="{ly + 12}" text-anchor="{align}" fill="{theme["muted"]}" font-size="11.5">{detail}</text>'
        f"</g>"
    )


def build_svg(spec: dict) -> str:
    theme_name = spec.get("theme", "vellum")
    theme = THEMES.get(theme_name, THEMES["vellum"])
    canvas = spec.get("canvas", {})
    w = int(canvas.get("width", 1120))
    h = int(canvas.get("height", 680))
    ox = float(canvas.get("origin_x", w * 0.5))
    oy = float(canvas.get("origin_y", h * 0.30))
    scale = float(canvas.get("scale", 18.0))
    stroke = theme["ink"] if theme_name != "dark" else "#475569"

    parts = sorted(spec.get("parts", []), key=part_depth)
    base_elems: list[str] = []
    solid_elems: list[str] = []

    for p in parts:
        ptype = p.get("type", "box")
        if ptype == "plate":
            base_elems.append(render_box(p, ox, oy, scale, stroke))
        elif ptype == "box":
            solid_elems.append(render_box(p, ox, oy, scale, stroke))
        elif ptype == "cylinder":
            solid_elems.append(render_cylinder(p, ox, oy, scale, stroke))
        elif ptype == "pipe":
            solid_elems.append(render_pipe(p, ox, oy, scale, stroke))
        elif ptype == "gauge":
            solid_elems.append(render_gauge(p, ox, oy, scale, stroke, theme["accent"]))

    callout_elems = [
        render_callout(c, ox, oy, scale, theme, i + 1)
        for i, c in enumerate(spec.get("callouts", []))
    ]

    return (
        f'<svg id="anatomy-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">'
        f'<rect width="{w}" height="{h}" fill="{theme["card"]}" rx="12"/>'
        f'<g id="layer-base">{"".join(base_elems)}</g>'
        f'<g id="layer-solids">{"".join(solid_elems)}</g>'
        f'<g id="layer-annotations">{"".join(callout_elems)}</g>'
        f"</svg>"
    )


def build_html(spec: dict, svg_markup: str) -> str:
    theme = THEMES.get(spec.get("theme", "vellum"), THEMES["vellum"])
    title = escape(spec.get("title", "Isometric Mechanical Anatomy"))
    fig_code = escape(spec.get("figure_code", "FIG. 01 — SYSTEM MECHANISM"))

    controls_html = []
    for ctrl in spec.get("controls", []):
        cid = escape(ctrl["id"])
        lbl = escape(ctrl["label"])
        mn, mx, val, st = ctrl.get("min", 0), ctrl.get("max", 100), ctrl.get("value", 50), ctrl.get("step", 1)
        controls_html.append(
            f'<label class="ctrl"><span>{lbl}: <strong id="val-{cid}">{val}</strong></span>'
            f'<input type="range" id="ctrl-{cid}" data-target="val-{cid}" min="{mn}" max="{mx}" value="{val}" step="{st}"/></label>'
        )

    readouts_html = []
    for ro in spec.get("readouts", []):
        rid = escape(ro["id"])
        lbl = escape(ro["label"])
        val = escape(str(ro["value"]))
        readouts_html.append(
            f'<div class="readout"><span class="ro-label">{lbl}</span><strong class="ro-val" id="ro-{rid}">{val}</strong></div>'
        )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{title}</title>
  <style>
    :root {{
      --bg: {theme["bg"]};
      --card: {theme["card"]};
      --ink: {theme["ink"]};
      --muted: {theme["muted"]};
      --accent: {theme["accent"]};
      --border: {theme["border"]};
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      background: var(--bg); color: var(--ink);
      font-family: "Plus Jakarta Sans", -apple-system, BlinkMacSystemFont, "PingFang SC", sans-serif;
      padding: 32px; display: flex; justify-content: center;
    }}
    .plate {{
      max-width: 1180px; width: 100%; background: var(--card);
      border: 1px solid var(--border); border-radius: 16px; padding: 28px 32px;
      box-shadow: 0 20px 60px rgba(0, 0, 0, 0.08);
    }}
    header {{
      display: flex; justify-content: space-between; align-items: flex-end;
      border-bottom: 1px solid var(--border); padding-bottom: 18px; margin-bottom: 20px; gap: 20px;
    }}
    .fig-code {{ font-size: 12px; letter-spacing: 0.14em; color: var(--accent); font-weight: 700; margin-bottom: 6px; }}
    h1 {{ font-size: 28px; letter-spacing: -0.02em; }}
    .readouts {{ display: flex; gap: 16px; flex-wrap: wrap; }}
    .readout {{
      border: 1px solid var(--border); border-radius: 8px; padding: 8px 14px; min-width: 130px;
      font-variant-numeric: tabular-nums;
    }}
    .ro-label {{ display: block; font-size: 10px; letter-spacing: 0.12em; color: var(--muted); }}
    .ro-val {{ font-size: 18px; color: var(--ink); }}
    .viewport {{ width: 100%; overflow: hidden; display: flex; justify-content: center; }}
    #anatomy-svg {{ width: 100%; height: auto; display: block; }}
    .controls {{
      margin-top: 20px; padding-top: 18px; border-top: 1px solid var(--border);
      display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 18px;
    }}
    .ctrl {{ display: flex; flex-direction: column; gap: 6px; font-size: 13px; color: var(--muted); }}
    .ctrl strong {{ color: var(--ink); font-variant-numeric: tabular-nums; }}
    input[type="range"] {{ accent-color: var(--accent); width: 100%; }}
  </style>
</head>
<body>
  <article class="plate">
    <header>
      <div>
        <div class="fig-code">{fig_code}</div>
        <h1>{title}</h1>
      </div>
      <div class="readouts">{"".join(readouts_html)}</div>
    </header>
    <div class="viewport">{svg_markup}</div>
    <section class="controls">{"".join(controls_html)}</section>
  </article>
  <script>
    document.querySelectorAll('input[type="range"]').forEach((slider) => {{
      slider.addEventListener('input', () => {{
        const target = document.getElementById(slider.dataset.target);
        if (target) target.textContent = slider.value;
      }});
    }});
  </script>
</body>
</html>
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Compile 3D isometric machine spec JSON into SVG or HTML.")
    parser.add_argument("--spec", type=Path, required=True, help="Input machine-spec.json")
    parser.add_argument("--output", type=Path, required=True, help="Output .html or .svg file")
    parser.add_argument("--format", choices=("html", "svg"), default="html")
    args = parser.parse_args()

    spec = json.loads(args.spec.read_text(encoding="utf-8"))
    svg = build_svg(spec)
    args.output.parent.mkdir(parents=True, exist_ok=True)

    if args.format == "svg" or args.output.suffix.lower() == ".svg":
        args.output.write_text(svg, encoding="utf-8")
    else:
        args.output.write_text(build_html(spec, svg), encoding="utf-8")

    print(
        json.dumps(
            {
                "output": str(args.output),
                "parts_rendered": len(spec.get("parts", [])),
                "callouts_rendered": len(spec.get("callouts", [])),
                "controls_wired": len(spec.get("controls", [])),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
