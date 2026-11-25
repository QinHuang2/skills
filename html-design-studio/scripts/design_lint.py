#!/usr/bin/env python3
"""Audit HTML design deliverables for WCAG contrast, brand-lock compliance, and AI-slop tells."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

TOKEN_RE = re.compile(r"(--[a-zA-Z0-9_-]+)\s*:\s*([^;}\n]+)")
HEX_RE = re.compile(r"#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})\b")
EMOJI_CRUTCH_RE = re.compile(r"[🚀✨💡🔥🎯⚡🌟💎🎉]")
PLACEHOLDER_RE = re.compile(
    r"(lorem ipsum|via\.placeholder\.com|placehold\.co|feature 1\b|john doe)",
    re.IGNORECASE,
)


def expand_hex(raw: str) -> str:
    h = raw.lstrip("#")
    if len(h) == 3:
        h = "".join(ch * 2 for ch in h)
    return f"#{h.upper()}"


def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    h = expand_hex(hex_color).lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def relative_luminance(rgb: tuple[int, int, int]) -> float:
    channels = []
    for c in rgb:
        v = c / 255.0
        channels.append(v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4)
    return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2]


def contrast_ratio(hex_a: str, hex_b: str) -> float:
    l1 = relative_luminance(hex_to_rgb(hex_a))
    l2 = relative_luminance(hex_to_rgb(hex_b))
    bright, dark = max(l1, l2), min(l1, l2)
    return round((bright + 0.05) / (dark + 0.05), 2)


def extract_css_tokens(html_text: str) -> dict[str, str]:
    tokens: dict[str, str] = {}
    for name, value in TOKEN_RE.findall(html_text):
        m = HEX_RE.search(value.strip())
        if m:
            tokens[name] = expand_hex(m.group(0))
        else:
            tokens[name] = value.strip()
    return tokens


def audit_html(html_path: Path, brand_lock_path: Path | None) -> dict:
    text = html_path.read_text(encoding="utf-8")
    errors: list[str] = []
    warnings: list[str] = []
    tokens = extract_css_tokens(text)

    if "<meta name=\"viewport\"" not in text.lower() and "data-slide" not in text.lower():
        warnings.append("Missing <meta name=\"viewport\"> tag for responsive web artifact.")

    for required in ("--bg", "--ink", "--accent"):
        if required not in tokens:
            warnings.append(f"Recommended CSS token '{required}' not found in stylesheet.")

    bg = tokens.get("--bg")
    ink = tokens.get("--ink")
    muted = tokens.get("--muted")
    surface = tokens.get("--surface")

    contrast_checks: dict[str, float] = {}
    if bg and ink and bg.startswith("#") and ink.startswith("#"):
        ratio = contrast_ratio(bg, ink)
        contrast_checks["bg_vs_ink"] = ratio
        if ratio < 4.5:
            errors.append(f"Primary text contrast (--bg {bg} vs --ink {ink}) is {ratio}:1 (< 4.5:1 WCAG AA).")

    if surface and ink and surface.startswith("#") and ink.startswith("#"):
        ratio = contrast_ratio(surface, ink)
        contrast_checks["surface_vs_ink"] = ratio
        if ratio < 4.5:
            errors.append(f"Surface text contrast (--surface {surface} vs --ink {ink}) is {ratio}:1 (< 4.5:1 WCAG AA).")

    if bg and muted and bg.startswith("#") and muted.startswith("#"):
        ratio = contrast_ratio(bg, muted)
        contrast_checks["bg_vs_muted"] = ratio
        if ratio < 3.0:
            warnings.append(f"Muted text contrast (--bg {bg} vs --muted {muted}) is low at {ratio}:1 (< 3.0:1).")

    placeholders = PLACEHOLDER_RE.findall(text)
    if placeholders:
        errors.append(f"Placeholder copy/URLs detected: {sorted(set(p.lower() for p in placeholders))}")

    emojis = EMOJI_CRUTCH_RE.findall(text)
    if len(emojis) >= 3:
        warnings.append(f"Detected {len(emojis)} generic AI-slop emojis ({''.join(sorted(set(emojis)))}); prefer inline SVG or typographic markers.")

    lowered = text.lower()
    if ("#6366f1" in lowered or "#8b5cf6" in lowered) and not brand_lock_path:
        warnings.append("Default indigo/violet SaaS palette (#6366F1/#8B5CF6) detected without brand lock; verify intentionality.")

    if brand_lock_path:
        lock = json.loads(brand_lock_path.read_text(encoding="utf-8"))
        locked_tokens = lock.get("tokens", {})
        for k, expected in locked_tokens.items():
            expected_norm = expand_hex(expected) if expected.startswith("#") else expected
            actual = tokens.get(k)
            if actual is None:
                errors.append(f"Brand lock token '{k}' missing from HTML CSS variables.")
            elif actual != expected_norm:
                errors.append(f"Brand lock mismatch for '{k}': expected {expected_norm}, found {actual}.")

    slide_count = len(re.findall(r"<section\b[^>]*\bdata-slide\b", text, re.IGNORECASE))

    return {
        "file": str(html_path),
        "passed": len(errors) == 0,
        "slide_count": slide_count,
        "tokens_found": len(tokens),
        "contrast": contrast_checks,
        "errors": errors,
        "warnings": warnings,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Lint HTML design files for contrast, brand tokens, and anti-slop rules.")
    parser.add_argument("--input", type=Path, required=True, help="Path to HTML file to audit")
    parser.add_argument("--brand-lock", type=Path, default=None, help="Optional path to brand-lock.json")
    args = parser.parse_args()

    if not args.input.exists():
        raise SystemExit(f"Input file not found: {args.input}")
    if args.brand_lock and not args.brand_lock.exists():
        raise SystemExit(f"Brand lock file not found: {args.brand_lock}")

    report = audit_html(args.input, args.brand_lock)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    sys.exit(0 if report["passed"] else 1)


if __name__ == "__main__":
    main()
