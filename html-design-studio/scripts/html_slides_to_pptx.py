#!/usr/bin/env python3
"""Compile structured HTML slide decks (<section data-slide>) into native editable .pptx files using pure Python stdlib."""

from __future__ import annotations

import argparse
from html.parser import HTMLParser
import json
import re
from pathlib import Path
from xml.sax.saxutils import escape
import zipfile

# 16:9 Widescreen in EMUs (13.333 in x 7.5 in; 1 inch = 914400 EMU)
SLIDE_W = 12192000
SLIDE_H = 6858000


def clean_hex(color: str | None, fallback: str) -> str:
    if not color:
        return fallback
    m = re.search(r"#?([0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b", color.strip())
    if not m:
        return fallback
    raw = m.group(1)
    if len(raw) == 3:
        raw = "".join(ch * 2 for ch in raw)
    return raw.upper()


class SlideDeckHTMLParser(HTMLParser):
    """Extract structured slides from <section data-slide> blocks."""

    def __init__(self) -> None:
        super().__init__()
        self.slides: list[dict] = []
        self._current: dict | None = None
        self._section_depth = 0
        self._active_role: str | None = None
        self._buf: list[str] = []
        self._metric: dict | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_map = {k.lower(): (v or "") for k, v in attrs}
        t = tag.lower()

        if t == "section" and ("data-slide" in attr_map or self._section_depth > 0):
            if self._section_depth == 0:
                self._current = {
                    "bg": clean_hex(attr_map.get("data-bg"), "F6F5F0"),
                    "ink": clean_hex(attr_map.get("data-ink"), "141413"),
                    "accent": clean_hex(attr_map.get("data-accent"), "E03C28"),
                    "kicker": "",
                    "title": "",
                    "lead": "",
                    "bullets": [],
                    "metrics": [],
                    "footnote": "",
                }
            self._section_depth += 1
            return

        if self._current is None:
            return

        if "data-metric" in attr_map:
            self._metric = {"value": "", "label": ""}
        elif self._metric is not None and "data-value" in attr_map:
            self._active_role = "metric_value"
            self._buf = []
        elif self._metric is not None and "data-label" in attr_map:
            self._active_role = "metric_label"
            self._buf = []
        elif "data-kicker" in attr_map:
            self._active_role = "kicker"
            self._buf = []
        elif t in ("h1", "h2") and not self._current["title"]:
            self._active_role = "title"
            self._buf = []
        elif "data-lead" in attr_map or (t == "p" and not self._current["lead"] and self._active_role is None):
            self._active_role = "lead"
            self._buf = []
        elif t == "li":
            self._active_role = "bullet"
            self._buf = []
        elif "data-footnote" in attr_map or t == "footer":
            self._active_role = "footnote"
            self._buf = []

    def handle_data(self, data: str) -> None:
        if self._current is not None and self._active_role is not None:
            self._buf.append(data)

    def handle_endtag(self, tag: str) -> None:
        t = tag.lower()
        if self._current is None:
            return

        if t == "section" and self._section_depth > 0:
            self._section_depth -= 1
            if self._section_depth == 0:
                self.slides.append(self._current)
                self._current = None
                self._active_role = None
                self._metric = None
            return

        text = re.sub(r"\s+", " ", "".join(self._buf)).strip()
        if self._active_role == "metric_value" and self._metric is not None:
            self._metric["value"] = text
            self._active_role = None
        elif self._active_role == "metric_label" and self._metric is not None:
            self._metric["label"] = text
            self._active_role = None
        elif t in ("div", "article") and self._metric is not None and (self._metric["value"] or self._metric["label"]):
            self._current["metrics"].append(self._metric)
            self._metric = None
        elif self._active_role == "kicker" and t in ("span", "div", "p"):
            self._current["kicker"] = text
            self._active_role = None
        elif self._active_role == "title" and t in ("h1", "h2"):
            self._current["title"] = text
            self._active_role = None
        elif self._active_role == "lead" and t in ("p", "div"):
            self._current["lead"] = text
            self._active_role = None
        elif self._active_role == "bullet" and t == "li":
            if text:
                self._current["bullets"].append(text)
            self._active_role = None
        elif self._active_role == "footnote" and t in ("footer", "div", "p", "span"):
            self._current["footnote"] = text
            self._active_role = None


def shape_textbox(
    shape_id: int,
    name: str,
    x: int,
    y: int,
    cx: int,
    cy: int,
    paragraphs: list[tuple[str, int, str, bool]],
    fill_hex: str | None = None,
    border_hex: str | None = None,
) -> str:
    """Build a PresentationML p:sp shape with styled paragraphs: (text, pt_x100, rgb_hex, bold)."""
    sp_pr_fill = (
        f"<a:solidFill><a:srgbClr val=\"{fill_hex}\"/></a:solidFill>" if fill_hex else "<a:noFill/>"
    )
    sp_pr_ln = (
        f"<a:ln w=\"12700\"><a:solidFill><a:srgbClr val=\"{border_hex}\"/></a:solidFill></a:ln>"
        if border_hex
        else ""
    )
    paras_xml = []
    for text, sz, color, bold in paragraphs:
        b_attr = ' b="1"' if bold else ""
        paras_xml.append(
            f"<a:p><a:pPr algn=\"l\"/>"
            f"<a:r><a:rPr lang=\"zh-CN\" altLang=\"en-US\" sz=\"{sz}\"{b_attr} dirty=\"0\">"
            f"<a:solidFill><a:srgbClr val=\"{color}\"/></a:solidFill>"
            f"<a:latin typeface=\"Plus Jakarta Sans\"/><a:ea typeface=\"PingFang SC\"/>"
            f"</a:rPr><a:t>{escape(text)}</a:t></a:r></a:p>"
        )
    if not paras_xml:
        paras_xml.append("<a:p><a:endParaRPr lang=\"en-US\"/></a:p>")

    return (
        f"<p:sp>"
        f"<p:nvSpPr><p:cNvPr id=\"{shape_id}\" name=\"{escape(name)}\"/><p:cNvSpPr txBox=\"1\"/><p:nvPr/></p:nvSpPr>"
        f"<p:spPr><a:xfrm><a:off x=\"{x}\" y=\"{y}\"/><a:ext cx=\"{cx}\" cy=\"{cy}\"/></a:xfrm>"
        f"<a:prstGeom prst=\"rect\"><a:avLst/></a:prstGeom>{sp_pr_fill}{sp_pr_ln}</p:spPr>"
        f"<p:txBody><a:bodyPr wrap=\"square\" lIns=\"137160\" tIns=\"91440\" rIns=\"137160\" bIns=\"91440\"/>"
        f"<a:lstStyle/>{''.join(paras_xml)}</p:txBody>"
        f"</p:sp>"
    )


def build_slide_xml(slide: dict, idx: int) -> str:
    bg = slide["bg"]
    ink = slide["ink"]
    accent = slide["accent"]
    shapes: list[str] = []
    sid = 2

    # Accent top rule
    shapes.append(
        shape_textbox(sid, "AccentBar", 731520, 480000, 1097280, 45720, [("", 800, accent, False)], fill_hex=accent)
    )
    sid += 1

    if slide["kicker"]:
        shapes.append(
            shape_textbox(sid, "Kicker", 731520, 580000, 10728960, 420000, [(slide["kicker"].upper(), 1300, accent, True)])
        )
        sid += 1

    if slide["title"]:
        shapes.append(
            shape_textbox(sid, "Title", 731520, 1020000, 10728960, 1450000, [(slide["title"], 4000, ink, True)])
        )
        sid += 1

    body_y = 2520000
    if slide["lead"]:
        shapes.append(
            shape_textbox(sid, "Lead", 731520, body_y, 10200000, 960000, [(slide["lead"], 2000, ink, False)])
        )
        sid += 1
        body_y += 1020000

    if slide["metrics"]:
        count = min(len(slide["metrics"]), 4)
        gap = 228600
        card_w = (10728960 - gap * (count - 1)) // count
        for i, m in enumerate(slide["metrics"][:count]):
            mx = 731520 + i * (card_w + gap)
            shapes.append(
                shape_textbox(
                    sid,
                    f"Metric_{i+1}",
                    mx,
                    body_y,
                    card_w,
                    1650000,
                    [
                        (m["value"], 3600, accent, True),
                        (m["label"], 1400, ink, False),
                    ],
                    border_hex=accent,
                )
            )
            sid += 1
        body_y += 1820000

    if slide["bullets"]:
        bullet_paras = [(f"•  {b}", 1800, ink, False) for b in slide["bullets"][:6]]
        shapes.append(
            shape_textbox(sid, "Bullets", 731520, body_y, 10200000, max(900000, 6200000 - body_y), bullet_paras)
        )
        sid += 1

    footer_text = slide["footnote"] or f"Slide {idx:02d}"
    shapes.append(
        shape_textbox(sid, "Footer", 731520, 6250000, 10728960, 380000, [(footer_text, 1100, ink, False)])
    )

    return (
        "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>"
        "<p:sld xmlns:a=\"http://schemas.openxmlformats.org/drawingml/2006/main\" "
        "xmlns:r=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships\" "
        "xmlns:p=\"http://schemas.openxmlformats.org/presentationml/2006/main\">"
        "<p:cSld>"
        f"<p:bg><p:bgPr><a:solidFill><a:srgbClr val=\"{bg}\"/></a:solidFill><a:effectLst/></p:bgPr></p:bg>"
        "<p:spTree>"
        "<p:nvGrpSpPr><p:cNvPr id=\"1\" name=\"\"/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>"
        "<p:grpSpPr><a:xfrm><a:off x=\"0\" y=\"0\"/><a:ext cx=\"0\" cy=\"0\"/>"
        "<a:chOff x=\"0\" y=\"0\"/><a:chExt cx=\"0\" cy=\"0\"/></a:xfrm></p:grpSpPr>"
        f"{''.join(shapes)}"
        "</p:spTree></p:cSld>"
        "<p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr>"
        "</p:sld>"
    )


def write_pptx(slides: list[dict], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    n = len(slides)

    slide_overrides = "".join(
        f"<Override PartName=\"/ppt/slides/slide{i}.xml\" "
        "ContentType=\"application/vnd.openxmlformats-officedocument.presentationml.slide+xml\"/>"
        for i in range(1, n + 1)
    )
    content_types = (
        "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>"
        "<Types xmlns=\"http://schemas.openxmlformats.org/package/2006/content-types\">"
        "<Default Extension=\"rels\" ContentType=\"application/vnd.openxmlformats-package.relationships+xml\"/>"
        "<Default Extension=\"xml\" ContentType=\"application/xml\"/>"
        "<Override PartName=\"/ppt/presentation.xml\" "
        "ContentType=\"application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml\"/>"
        "<Override PartName=\"/ppt/slideMasters/slideMaster1.xml\" "
        "ContentType=\"application/vnd.openxmlformats-officedocument.presentationml.slideMaster+xml\"/>"
        "<Override PartName=\"/ppt/slideLayouts/slideLayout1.xml\" "
        "ContentType=\"application/vnd.openxmlformats-officedocument.presentationml.slideLayout+xml\"/>"
        "<Override PartName=\"/ppt/theme/theme1.xml\" "
        "ContentType=\"application/vnd.openxmlformats-officedocument.theme+xml\"/>"
        f"{slide_overrides}</Types>"
    )

    root_rels = (
        "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>"
        "<Relationships xmlns=\"http://schemas.openxmlformats.org/package/2006/relationships\">"
        "<Relationship Id=\"rId1\" "
        "Type=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument\" "
        "Target=\"ppt/presentation.xml\"/></Relationships>"
    )

    pres_slide_rels = "".join(
        f"<Relationship Id=\"rId{i+2}\" "
        "Type=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide\" "
        f"Target=\"slides/slide{i}.xml\"/>"
        for i in range(1, n + 1)
    )
    pres_rels = (
        "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>"
        "<Relationships xmlns=\"http://schemas.openxmlformats.org/package/2006/relationships\">"
        "<Relationship Id=\"rId1\" "
        "Type=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster\" "
        "Target=\"slideMasters/slideMaster1.xml\"/>"
        "<Relationship Id=\"rId2\" "
        "Type=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme\" "
        "Target=\"theme/theme1.xml\"/>"
        f"{pres_slide_rels}</Relationships>"
    )

    sld_ids = "".join(f"<p:sldId id=\"{255 + i}\" r:id=\"rId{i+2}\"/>" for i in range(1, n + 1))
    presentation_xml = (
        "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>"
        "<p:presentation xmlns:a=\"http://schemas.openxmlformats.org/drawingml/2006/main\" "
        "xmlns:r=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships\" "
        "xmlns:p=\"http://schemas.openxmlformats.org/presentationml/2006/main\">"
        "<p:sldMasterIdLst><p:sldMasterId id=\"2147483648\" r:id=\"rId1\"/></p:sldMasterIdLst>"
        f"<p:sldIdLst>{sld_ids}</p:sldIdLst>"
        f"<p:sldSz cx=\"{SLIDE_W}\" cy=\"{SLIDE_H}\" type=\"custom\"/>"
        "<p:notesSz cx=\"6858000\" cy=\"9144000\"/></p:presentation>"
    )

    slide_master = (
        "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>"
        "<p:sldMaster xmlns:a=\"http://schemas.openxmlformats.org/drawingml/2006/main\" "
        "xmlns:r=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships\" "
        "xmlns:p=\"http://schemas.openxmlformats.org/presentationml/2006/main\">"
        "<p:cSld><p:spTree>"
        "<p:nvGrpSpPr><p:cNvPr id=\"1\" name=\"\"/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>"
        "<p:grpSpPr><a:xfrm><a:off x=\"0\" y=\"0\"/><a:ext cx=\"0\" cy=\"0\"/>"
        "<a:chOff x=\"0\" y=\"0\"/><a:chExt cx=\"0\" cy=\"0\"/></a:xfrm></p:grpSpPr>"
        "</p:spTree></p:cSld>"
        "<p:clrMap bg1=\"lt1\" tx1=\"dk1\" bg2=\"lt2\" tx2=\"dk2\" accent1=\"accent1\" "
        "accent2=\"accent2\" accent3=\"accent3\" accent4=\"accent4\" accent5=\"accent5\" "
        "accent6=\"accent6\" hlink=\"hlink\" folHlink=\"folHlink\"/>"
        "<p:sldLayoutIdLst><p:sldLayoutId id=\"2147483649\" r:id=\"rId1\"/></p:sldLayoutIdLst>"
        "</p:sldMaster>"
    )

    master_rels = (
        "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>"
        "<Relationships xmlns=\"http://schemas.openxmlformats.org/package/2006/relationships\">"
        "<Relationship Id=\"rId1\" "
        "Type=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout\" "
        "Target=\"../slideLayouts/slideLayout1.xml\"/>"
        "<Relationship Id=\"rId2\" "
        "Type=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme\" "
        "Target=\"../theme/theme1.xml\"/></Relationships>"
    )

    slide_layout = (
        "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>"
        "<p:sldLayout xmlns:a=\"http://schemas.openxmlformats.org/drawingml/2006/main\" "
        "xmlns:r=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships\" "
        "xmlns:p=\"http://schemas.openxmlformats.org/presentationml/2006/main\" type=\"blank\">"
        "<p:cSld name=\"Blank\"><p:spTree>"
        "<p:nvGrpSpPr><p:cNvPr id=\"1\" name=\"\"/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>"
        "<p:grpSpPr><a:xfrm><a:off x=\"0\" y=\"0\"/><a:ext cx=\"0\" cy=\"0\"/>"
        "<a:chOff x=\"0\" y=\"0\"/><a:chExt cx=\"0\" cy=\"0\"/></a:xfrm></p:grpSpPr>"
        "</p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sldLayout>"
    )

    layout_rels = (
        "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>"
        "<Relationships xmlns=\"http://schemas.openxmlformats.org/package/2006/relationships\">"
        "<Relationship Id=\"rId1\" "
        "Type=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster\" "
        "Target=\"../slideMasters/slideMaster1.xml\"/></Relationships>"
    )

    slide_rel = (
        "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>"
        "<Relationships xmlns=\"http://schemas.openxmlformats.org/package/2006/relationships\">"
        "<Relationship Id=\"rId1\" "
        "Type=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout\" "
        "Target=\"../slideLayouts/slideLayout1.xml\"/></Relationships>"
    )

    theme_xml = (
        "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>"
        "<a:theme xmlns:a=\"http://schemas.openxmlformats.org/drawingml/2006/main\" name=\"StudioTheme\">"
        "<a:themeElements>"
        "<a:clrScheme name=\"Studio\">"
        "<a:dk1><a:srgbClr val=\"141413\"/></a:dk1><a:lt1><a:srgbClr val=\"F6F5F0\"/></a:lt1>"
        "<a:dk2><a:srgbClr val=\"27272A\"/></a:dk2><a:lt2><a:srgbClr val=\"EAEAE6\"/></a:lt2>"
        "<a:accent1><a:srgbClr val=\"E03C28\"/></a:accent1><a:accent2><a:srgbClr val=\"1D4ED8\"/></a:accent2>"
        "<a:accent3><a:srgbClr val=\"10B981\"/></a:accent3><a:accent4><a:srgbClr val=\"F59E0B\"/></a:accent4>"
        "<a:accent5><a:srgbClr val=\"6366F1\"/></a:accent5><a:accent6><a:srgbClr val=\"EC4899\"/></a:accent6>"
        "<a:hlink><a:srgbClr val=\"1D4ED8\"/></a:hlink><a:folHlink><a:srgbClr val=\"5E5D59\"/></a:folHlink>"
        "</a:clrScheme>"
        "<a:fontScheme name=\"StudioFonts\">"
        "<a:majorFont><a:latin typeface=\"Plus Jakarta Sans\"/><a:ea typeface=\"PingFang SC\"/><a:cs typeface=\"Arial\"/></a:majorFont>"
        "<a:minorFont><a:latin typeface=\"Plus Jakarta Sans\"/><a:ea typeface=\"PingFang SC\"/><a:cs typeface=\"Arial\"/></a:minorFont>"
        "</a:fontScheme>"
        "<a:fmtScheme name=\"StudioFmt\">"
        "<a:fillStyleLst><a:solidFill><a:schemeClr val=\"phClr\"/></a:solidFill>"
        "<a:solidFill><a:schemeClr val=\"phClr\"/></a:solidFill>"
        "<a:solidFill><a:schemeClr val=\"phClr\"/></a:solidFill></a:fillStyleLst>"
        "<a:lnStyleLst><a:ln w=\"9525\"><a:solidFill><a:schemeClr val=\"phClr\"/></a:solidFill></a:ln>"
        "<a:ln w=\"19050\"><a:solidFill><a:schemeClr val=\"phClr\"/></a:solidFill></a:ln>"
        "<a:ln w=\"25400\"><a:solidFill><a:schemeClr val=\"phClr\"/></a:solidFill></a:ln></a:lnStyleLst>"
        "<a:effectStyleLst><a:effectStyle><a:effectLst/></a:effectStyle>"
        "<a:effectStyle><a:effectLst/></a:effectStyle>"
        "<a:effectStyle><a:effectLst/></a:effectStyle></a:effectStyleLst>"
        "<a:bgFillStyleLst><a:solidFill><a:schemeClr val=\"phClr\"/></a:solidFill>"
        "<a:solidFill><a:schemeClr val=\"phClr\"/></a:solidFill>"
        "<a:solidFill><a:schemeClr val=\"phClr\"/></a:solidFill></a:bgFillStyleLst>"
        "</a:fmtScheme></a:themeElements></a:theme>"
    )

    with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", content_types)
        zf.writestr("_rels/.rels", root_rels)
        zf.writestr("ppt/presentation.xml", presentation_xml)
        zf.writestr("ppt/_rels/presentation.xml.rels", pres_rels)
        zf.writestr("ppt/slideMasters/slideMaster1.xml", slide_master)
        zf.writestr("ppt/slideMasters/_rels/slideMaster1.xml.rels", master_rels)
        zf.writestr("ppt/slideLayouts/slideLayout1.xml", slide_layout)
        zf.writestr("ppt/slideLayouts/_rels/slideLayout1.xml.rels", layout_rels)
        zf.writestr("ppt/theme/theme1.xml", theme_xml)
        for i, slide in enumerate(slides, start=1):
            zf.writestr(f"ppt/slides/slide{i}.xml", build_slide_xml(slide, i))
            zf.writestr(f"ppt/slides/_rels/slide{i}.xml.rels", slide_rel)


def main() -> None:
    parser = argparse.ArgumentParser(description="Export <section data-slide> HTML decks to editable .pptx")
    parser.add_argument("--input", type=Path, required=True, help="Input HTML slide deck")
    parser.add_argument("--output", type=Path, required=True, help="Output .pptx file path")
    args = parser.parse_args()

    html_text = args.input.read_text(encoding="utf-8")
    deck_parser = SlideDeckHTMLParser()
    deck_parser.feed(html_text)
    if not deck_parser.slides:
        raise SystemExit("No <section data-slide> elements found in input HTML.")

    write_pptx(deck_parser.slides, args.output)
    print(
        json.dumps(
            {
                "output": str(args.output),
                "slides_exported": len(deck_parser.slides),
                "size_bytes": args.output.stat().st_size,
            },
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
