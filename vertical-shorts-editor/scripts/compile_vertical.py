#!/usr/bin/env python3
"""Compile a validated 9:16 plan.json into H.264 MP4 + .ass karaoke captions via FFmpeg, or scaffold a Remotion project."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


def find_bin(name: str) -> str | None:
    found = shutil.which(name)
    if found:
        return found
    for prefix in ("/opt/homebrew/bin", "/usr/local/bin"):
        candidate = Path(prefix) / name
        if candidate.exists():
            return str(candidate)
    return None


def ffmpeg_has_filter(ffmpeg: str, filter_name: str) -> bool:
    out = subprocess.check_output([ffmpeg, "-hide_banner", "-filters"], text=True, stderr=subprocess.STDOUT)
    for line in out.splitlines():
        parts = line.split()
        if len(parts) >= 2 and parts[1] == filter_name:
            return True
    return False


def ass_color(hex_rgb: str, alpha: str = "00") -> str:
    h = hex_rgb.strip().lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    rr, gg, bb = h[0:2].upper(), h[2:4].upper(), h[4:6].upper()
    return f"&H{alpha}{bb}{gg}{rr}"


def fmt_ass_time(sec: float) -> str:
    cs_total = max(0, int(round(sec * 100)))
    cs = cs_total % 100
    s_total = cs_total // 100
    s = s_total % 60
    m_total = s_total // 60
    m = m_total % 60
    h = m_total // 60
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def build_ass_subtitles(plan: dict) -> str:
    canvas = plan.get("canvas", {})
    w = int(canvas.get("width", 1080))
    h = int(canvas.get("height", 1920))
    brand = plan.get("brand", {})
    txt_c = ass_color(brand.get("text", "#FFFFFF"))
    hi_c = ass_color(brand.get("highlight", "#FACC15"))
    pri_c = ass_color(brand.get("primary", "#FF5500"))
    bg_c = ass_color(brand.get("bg_pill", "#111114"), alpha="28")

    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {w}
PlayResY: {h}
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: KaraokePop,PingFang SC,64,{txt_c},{hi_c},&H00000000,&H64000000,-1,0,0,0,100,100,1,0,1,5,3,5,80,190,420,1
Style: HookBanner,PingFang SC,58,{txt_c},{pri_c},{bg_c},{bg_c},-1,0,0,0,100,100,1,0,3,18,0,8,80,190,240,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    events: list[str] = []
    hook = plan.get("hook")
    if hook:
        hst = fmt_ass_time(float(hook.get("start", 0.0)))
        hen = fmt_ass_time(float(hook.get("end", 2.8)))
        headline = str(hook.get("headline", "")).replace("\n", "\\N")
        kicker = str(hook.get("kicker", "")).strip()
        prefix = f"{{\\fs34\\c{hi_c}}}{kicker}\\N{{\\fs58\\c{txt_c}}}" if kicker else ""
        events.append(f"Dialogue: 2,{hst},{hen},HookBanner,,0,0,0,,{{\\fad(120,160)}}{prefix}{headline}")

    for cap in plan.get("captions", []):
        words = cap.get("words", [])
        box = cap.get("box", {"x": 90, "y": 1340, "w": 800, "h": 150})
        cx = int(float(box["x"]) + float(box["w"]) * 0.5)
        cy = int(float(box["y"]) + float(box["h"]) * 0.5)

        if words:
            for active_idx, w_item in enumerate(words):
                wst = fmt_ass_time(float(w_item["start"]))
                wen = fmt_ass_time(float(w_item["end"]))
                parts = []
                for j, token in enumerate(words):
                    w_str = str(token["word"])
                    if j == active_idx:
                        parts.append(f"{{\\c{hi_c}\\fscx112\\fscy112}}{w_str}{{\\c{txt_c}\\fscx100\\fscy100}}")
                    else:
                        parts.append(w_str)
                joined = " ".join(parts)
                events.append(f"Dialogue: 1,{wst},{wen},KaraokePop,,0,0,0,,{{\\pos({cx},{cy})}}{joined}")
        else:
            st = fmt_ass_time(float(cap["start"]))
            en = fmt_ass_time(float(cap["end"]))
            txt = str(cap.get("text", ""))
            hi_word = str(cap.get("highlightWord", "")).strip()
            if hi_word and hi_word in txt:
                txt = txt.replace(
                    hi_word,
                    f"{{\\c{hi_c}\\fscx112\\fscy112}}{hi_word}{{\\c{txt_c}\\fscx100\\fscy100}}",
                    1,
                )
            events.append(f"Dialogue: 1,{st},{en},KaraokePop,,0,0,0,,{{\\pos({cx},{cy})\\fad(80,80)}}{txt}")

    return header + "\n".join(events) + "\n"


def render_overlay_plates_macos(plates: list[dict], temp_dir: Path) -> bool:
    """Use macOS AppKit/CoreGraphics via /usr/bin/swift to rasterize crisp RGBA caption/hook PNG plates when libass is absent."""
    swift_bin = find_bin("swift")
    if not swift_bin or not plates:
        return False

    manifest_path = temp_dir / "plates_manifest.json"
    manifest_path.write_text(json.dumps(plates, ensure_ascii=False), encoding="utf-8")

    swift_code = """
import AppKit
import Foundation

struct PlateSpec: Decodable {
    let output: String
    let width: Int
    let height: Int
    let text: String
    let subtext: String?
    let bgHex: String
    let fgHex: String
    let accentHex: String
    let fontSize: Double
    let pill: Bool
}

func colorFromHex(_ hex: String, alpha: CGFloat = 1.0) -> NSColor {
    let h = hex.trimmingCharacters(in: CharacterSet.alphanumerics.inverted)
    var int: UInt64 = 0
    Scanner(string: h).scanHexInt64(&int)
    let r = CGFloat((int >> 16) & 0xFF) / 255.0
    let g = CGFloat((int >> 8) & 0xFF) / 255.0
    let b = CGFloat(int & 0xFF) / 255.0
    return NSColor(srgbRed: r, green: g, blue: b, alpha: alpha)
}

let url = URL(fileURLWithPath: CommandLine.arguments[1])
let data = try Data(contentsOf: url)
let specs = try JSONDecoder().decode([PlateSpec].self, from: data)

for sp in specs {
    let rep = NSBitmapImageRep(
        bitmapDataPlanes: nil,
        pixelsWide: sp.width,
        pixelsHigh: sp.height,
        bitsPerSample: 8,
        samplesPerPixel: 4,
        hasAlpha: true,
        isPlanar: false,
        colorSpaceName: .deviceRGB,
        bytesPerRow: 0,
        bitsPerPixel: 0
    )!
    NSGraphicsContext.saveGraphicsState()
    NSGraphicsContext.current = NSGraphicsContext(bitmapImageRep: rep)

    let rect = NSRect(x: 0, y: 0, width: sp.width, height: sp.height)
    NSColor.clear.setFill()
    rect.fill()

    if sp.pill {
        let inset = rect.insetBy(dx: 6, dy: 6)
        let path = NSBezierPath(roundedRect: inset, xRadius: 22, yRadius: 22)
        colorFromHex(sp.bgHex, alpha: 0.90).setFill()
        path.fill()
        colorFromHex(sp.accentHex, alpha: 0.95).setStroke()
        path.lineWidth = 3.0
        path.stroke()
    }

    let style = NSMutableParagraphStyle()
    style.alignment = .center
    style.lineBreakMode = .byWordWrapping

    let font = NSFont(name: "PingFangSC-Semibold", size: CGFloat(sp.fontSize))
        ?? NSFont.boldSystemFont(ofSize: CGFloat(sp.fontSize))
    let shadow = NSShadow()
    shadow.shadowColor = NSColor(calibratedWhite: 0.0, alpha: 0.85)
    shadow.shadowBlurRadius = 6.0
    shadow.shadowOffset = NSSize(width: 0, height: -2)

    let attrs: [NSAttributedString.Key: Any] = [
        .font: font,
        .foregroundColor: colorFromHex(sp.fgHex),
        .paragraphStyle: style,
        .shadow: shadow
    ]

    var fullText = sp.text
    if let sub = sp.subtext, !sub.isEmpty {
        fullText = sub + "\\n" + sp.text
    }
    let attrStr = NSAttributedString(string: fullText, attributes: attrs)
    let bounds = attrStr.boundingRect(with: NSSize(width: CGFloat(sp.width - 40), height: CGFloat(sp.height - 20)),
                                      options: [.usesLineFragmentOrigin, .usesFontLeading])
    let drawRect = NSRect(
        x: 20,
        y: (CGFloat(sp.height) - bounds.height) / 2.0,
        width: CGFloat(sp.width - 40),
        height: bounds.height + 6
    )
    attrStr.draw(in: drawRect)

    NSGraphicsContext.restoreGraphicsState()
    if let png = rep.representation(using: .png, properties: [:]) {
        try png.write(to: URL(fileURLWithPath: sp.output))
    }
}
"""
    script_path = temp_dir / "render_plates.swift"
    script_path.write_text(swift_code, encoding="utf-8")
    res = subprocess.run([swift_bin, str(script_path), str(manifest_path)], capture_output=True, text=True)
    return res.returncode == 0


def cmd_render(args: argparse.Namespace) -> None:
    ffmpeg = find_bin("ffmpeg")
    if not ffmpeg:
        raise SystemExit("ffmpeg binary not found in PATH or /opt/homebrew/bin.")
    if not args.video.exists():
        raise SystemExit(f"Input video not found: {args.video}")

    plan = json.loads(args.plan.read_text(encoding="utf-8"))
    canvas = plan.get("canvas", {})
    w = int(canvas.get("width", 1080))
    h = int(canvas.get("height", 1920))
    fps = int(canvas.get("fps", 30))
    dur = float(plan.get("duration", 10.0))
    brand = plan.get("brand", {})

    args.output.parent.mkdir(parents=True, exist_ok=True)
    ass_path = args.output.with_suffix(".ass")
    ass_path.write_text(build_ass_subtitles(plan), encoding="utf-8")

    has_ass = ffmpeg_has_filter(ffmpeg, "ass")

    # Build base 9:16 cover-scale + scheduled punch-in zoom segments
    cuts = sorted(plan.get("cuts", []), key=lambda c: float(c.get("start", 0.0)))
    if not cuts:
        cuts = [{"start": 0.0, "end": dur, "zoom": 1.0}]

    filter_parts: list[str] = []
    seg_labels: list[str] = []
    for idx, c in enumerate(cuts):
        st = round(float(c["start"]), 3)
        en = round(float(c["end"]), 3)
        zm = max(1.0, float(c.get("zoom", 1.0)))
        sw = int(round(w * zm))
        sh = int(round(h * zm))
        sw += sw % 2
        sh += sh % 2
        cx = max(0, (sw - w) // 2)
        focus_y = float(c.get("focusY", 0.45))
        cy = max(0, min(sh - h, int(round((sh - h) * focus_y))))
        lbl = f"vseg{idx}"
        filter_parts.append(
            f"[0:v]trim=start={st}:end={en},setpts=PTS-STARTPTS,"
            f"scale={sw}:{sh}:force_original_aspect_ratio=increase,"
            f"crop={w}:{h}:{cx}:{cy},fps={fps}[{lbl}]"
        )
        seg_labels.append(f"[{lbl}]")

    if len(seg_labels) == 1:
        cur_v = seg_labels[0].strip("[]")
    else:
        filter_parts.append(f"{''.join(seg_labels)}concat=n={len(seg_labels)}:v=1:a=0[v_cut]")
        cur_v = "v_cut"

    extra_inputs: list[str] = []
    with tempfile.TemporaryDirectory() as td_str:
        td = Path(td_str)
        next_input_idx = 1

        # Optional B-roll overlays
        for b_idx, br in enumerate(plan.get("broll", [])):
            b_path = (args.plan.parent / br["path"]).resolve() if not Path(br["path"]).is_absolute() else Path(br["path"])
            if b_path.exists():
                bst = round(float(br["start"]), 3)
                ben = round(float(br["end"]), 3)
                extra_inputs.extend(["-itsoffset", str(bst), "-i", str(b_path)])
                blbl = f"broll{b_idx}"
                out_lbl = f"vb{b_idx}"
                filter_parts.append(
                    f"[{next_input_idx}:v]scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h}[{blbl}]"
                )
                filter_parts.append(
                    f"[{cur_v}][{blbl}]overlay=0:0:enable='between(t,{bst},{ben})'[{out_lbl}]"
                )
                cur_v = out_lbl
                next_input_idx += 1

        overlay_method = "ass"
        if has_ass:
            escaped_ass = str(ass_path.resolve()).replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")
            filter_parts.append(f"[{cur_v}]ass='{escaped_ass}'[v_sub]")
            cur_v = "v_sub"
        else:
            # Render RGBA PNG plates via macOS CoreText/Swift (or drawbox fallback)
            plates: list[dict] = []
            plate_sched: list[tuple[Path, int, int, float, float]] = []

            hook = plan.get("hook")
            if hook and "box" in hook:
                hb = hook["box"]
                hp = td / "hook.png"
                plates.append(
                    {
                        "output": str(hp),
                        "width": int(hb["w"]),
                        "height": int(hb["h"]),
                        "text": str(hook.get("headline", "")),
                        "subtext": str(hook.get("kicker", "")),
                        "bgHex": brand.get("bg_pill", "#111114"),
                        "fgHex": brand.get("text", "#FFFFFF"),
                        "accentHex": brand.get("primary", "#FF5500"),
                        "fontSize": 42.0,
                        "pill": True,
                    }
                )
                plate_sched.append((hp, int(hb["x"]), int(hb["y"]), float(hook["start"]), float(hook["end"])))

            for c_idx, card in enumerate(plan.get("cards", [])):
                if "box" not in card:
                    continue
                cb = card["box"]
                cp = td / f"card_{c_idx}.png"
                plates.append(
                    {
                        "output": str(cp),
                        "width": int(cb["w"]),
                        "height": int(cb["h"]),
                        "text": str(card.get("title", "")),
                        "subtext": str(card.get("subtitle", "")),
                        "bgHex": brand.get("bg_pill", "#111114"),
                        "fgHex": brand.get("highlight", "#FACC15"),
                        "accentHex": brand.get("primary", "#FF5500"),
                        "fontSize": 40.0,
                        "pill": True,
                    }
                )
                plate_sched.append((cp, int(cb["x"]), int(cb["y"]), float(card["start"]), float(card["end"])))

            for k_idx, cap in enumerate(plan.get("captions", [])):
                cb = cap.get("box", {"x": 90, "y": 1340, "w": 800, "h": 150})
                kp = td / f"cap_{k_idx}.png"
                plates.append(
                    {
                        "output": str(kp),
                        "width": int(cb["w"]),
                        "height": int(cb["h"]),
                        "text": str(cap.get("text", "")),
                        "subtext": None,
                        "bgHex": brand.get("bg_pill", "#111114"),
                        "fgHex": brand.get("highlight", "#FACC15") if cap.get("highlightWord") else brand.get("text", "#FFFFFF"),
                        "accentHex": brand.get("primary", "#FF5500"),
                        "fontSize": 52.0,
                        "pill": False,
                    }
                )
                plate_sched.append((kp, int(cb["x"]), int(cb["y"]), float(cap["start"]), float(cap["end"])))

            if render_overlay_plates_macos(plates, td):
                overlay_method = "macos-coretext-rgba-plates"
                for p_idx, (png_p, px, py, pst, pen) in enumerate(plate_sched):
                    if not png_p.exists():
                        continue
                    extra_inputs.extend(["-i", str(png_p)])
                    out_lbl = f"vp{p_idx}"
                    filter_parts.append(
                        f"[{cur_v}][{next_input_idx}:v]overlay={px}:{py}:enable='between(t,{pst:.3f},{pen:.3f})'[{out_lbl}]"
                    )
                    cur_v = out_lbl
                    next_input_idx += 1
            else:
                overlay_method = "ass-sidecar-only"

        filter_parts.append(f"[{cur_v}]format=yuv420p[vout]")
        cmd = [ffmpeg, "-y", "-i", str(args.video), *extra_inputs, "-filter_complex", ";".join(filter_parts)]
        cmd.extend(["-map", "[vout]", "-map", "0:a?", "-t", str(dur), "-c:v", "libx264", "-crf", "19", "-preset", "fast", "-c:a", "aac", "-b:a", "192k", str(args.output)])
        subprocess.run(cmd, check=True, capture_output=True)

    print(
        json.dumps(
            {
                "output": str(args.output),
                "ass_subtitles": str(ass_path),
                "overlay_engine": overlay_method,
                "resolution": f"{w}x{h}",
                "duration_sec": dur,
                "size_bytes": args.output.stat().st_size,
            },
            indent=2,
            ensure_ascii=False,
        )
    )


REMOTION_COMPOSITION_TSX = """import React from "react";
import { AbsoluteFill, OffthreadVideo, Sequence, staticFile, useCurrentFrame, useVideoConfig, spring } from "remotion";
import plan from "./plan.json";

export const VerticalShortComposition: React.FC<{ videoSrc?: string }> = ({ videoSrc = "input.mp4" }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;

  const activeCut = plan.cuts.find((c) => t >= c.start && t < c.end) || { zoom: 1.0 };
  const activeCaption = plan.captions.find((c) => t >= c.start && t <= c.end);
  const hookVisible = plan.hook && t >= plan.hook.start && t <= plan.hook.end;

  return (
    <AbsoluteFill style={{ backgroundColor: "#09090B", overflow: "hidden" }}>
      <AbsoluteFill style={{ transform: `scale(${activeCut.zoom})` }}>
        <OffthreadVideo src={staticFile(videoSrc)} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
      </AbsoluteFill>

      {hookVisible && plan.hook && (
        <div
          style={{
            position: "absolute",
            left: plan.hook.box.x,
            top: plan.hook.box.y,
            width: plan.hook.box.w,
            padding: "24px 32px",
            borderRadius: 24,
            background: plan.brand.bg_pill,
            border: `3px solid ${plan.brand.primary}`,
            color: plan.brand.text,
            fontFamily: "Plus Jakarta Sans, PingFang SC, sans-serif",
            transform: `scale(${spring({ frame, fps, config: { damping: 14 } })})`,
          }}
        >
          <div style={{ fontSize: 22, fontWeight: 700, color: plan.brand.highlight, letterSpacing: "0.1em" }}>
            {plan.hook.kicker}
          </div>
          <div style={{ fontSize: 44, fontWeight: 800, marginTop: 6 }}>{plan.hook.headline}</div>
        </div>
      )}

      {activeCaption && (
        <div
          style={{
            position: "absolute",
            left: activeCaption.box.x,
            top: activeCaption.box.y,
            width: activeCaption.box.w,
            textAlign: "center",
            fontSize: 60,
            fontWeight: 800,
            color: plan.brand.text,
            textShadow: "0 4px 18px rgba(0,0,0,0.85)",
            fontFamily: "Plus Jakarta Sans, PingFang SC, sans-serif",
          }}
        >
          {activeCaption.text}
        </div>
      )}
    </AbsoluteFill>
  );
};
"""


def cmd_scaffold_remotion(args: argparse.Namespace) -> None:
    plan = json.loads(args.plan.read_text(encoding="utf-8"))
    out = args.out_dir.resolve()
    src = out / "src"
    src.mkdir(parents=True, exist_ok=True)
    (out / "public").mkdir(exist_ok=True)

    shutil.copy2(args.plan, src / "plan.json")
    (src / "VerticalShort.tsx").write_text(REMOTION_COMPOSITION_TSX, encoding="utf-8")

    fps = int(plan.get("canvas", {}).get("fps", 30))
    frames = max(30, int(round(float(plan.get("duration", 15.0)) * fps)))
    root_tsx = f"""import React from "react";
import {{ Composition }} from "remotion";
import {{ VerticalShortComposition }} from "./VerticalShort";

export const RemotionRoot: React.FC = () => (
  <Composition
    id="VerticalShort"
    component={{VerticalShortComposition}}
    durationInFrames={{{frames}}}
    fps={{{fps}}}
    width={{1080}}
    height={{1920}}
  />
);
"""
    (src / "Root.tsx").write_text(root_tsx, encoding="utf-8")
    pkg = {
        "name": "vertical-short-remotion",
        "private": True,
        "scripts": {
            "studio": "remotion studio src/Root.tsx",
            "render": "remotion render src/Root.tsx VerticalShort out/short.mp4",
        },
        "dependencies": {
            "react": "^18.3.1",
            "react-dom": "^18.3.1",
            "remotion": "^4.0.0",
            "@remotion/cli": "^4.0.0",
        },
    }
    (out / "package.json").write_text(json.dumps(pkg, indent=2), encoding="utf-8")
    print(json.dumps({"remotion_dir": str(out), "duration_in_frames": frames, "fps": fps}, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description="Compile 9:16 vertical short MP4 or scaffold Remotion composition.")
    sub = parser.add_subparsers(dest="command", required=True)

    p_ren = sub.add_parser("render", help="Compile 1080x1920 MP4 + .ass karaoke captions via FFmpeg")
    p_ren.add_argument("--video", type=Path, required=True)
    p_ren.add_argument("--plan", type=Path, required=True)
    p_ren.add_argument("--output", type=Path, required=True)
    p_ren.set_defaults(func=cmd_render)

    p_rem = sub.add_parser("scaffold-remotion", help="Generate a Remotion React project driven by plan.json")
    p_rem.add_argument("--plan", type=Path, required=True)
    p_rem.add_argument("--out-dir", type=Path, required=True)
    p_rem.set_defaults(func=cmd_scaffold_remotion)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
