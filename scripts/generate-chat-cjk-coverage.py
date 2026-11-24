# /// script
# requires-python = ">=3.11"
# dependencies = ["fonttools==4.60.1"]
# ///
"""Run with `nix develop -c uv run scripts/generate-chat-cjk-coverage.py`."""

import hashlib
import json
from pathlib import Path

from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "assets/terminal-fonts/NotoSansMonoCJKsc-Regular.otf"
SOURCE_SHA256 = "ec04cc376b34887cedbdf84074e2e226ed2761eeabdcb9173fc1dd7bfd153ef7"
SOURCE_URL = (
    "https://raw.githubusercontent.com/notofonts/noto-cjk/Sans2.004/"
    "Sans/Mono/NotoSansMonoCJKsc-Regular.otf"
)
OUTPUT = ROOT / "assets/gui-fonts/WhipChatCJK"
# CJK radicals, punctuation, kana, bopomofo, ideographs, compatibility and
# fullwidth forms. Keep Latin, Hangul and unsupported glyphs on the normal fallback path.
CJK_RANGES = (
    (0x2E80, 0x2FFF),
    (0x3000, 0x31FF),
    (0x3400, 0x4DBF),
    (0x4E00, 0x9FFF),
    (0xF900, 0xFAFF),
    (0xFE10, 0xFE1F),
    (0xFE30, 0xFE4F),
    (0xFF00, 0xFFEF),
    (0x20000, 0x323AF),
)


def main() -> None:
    source_hash = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    if source_hash != SOURCE_SHA256:
        raise ValueError("Noto Sans Mono CJK SC does not match the pinned upstream font")
    font = TTFont(SOURCE)
    cmap = font.getBestCmap()
    assert font["name"].getDebugName(6) == "NotoSansMonoCJKsc-Regular"
    codepoints = {cp for cp in cmap if any(start <= cp <= end for start, end in CJK_RANGES)}

    # Paint.hasGlyph also considers system fallback. Use actual font coverage
    # for native spans, leaving unsupported characters and Latin untouched.
    coverage = bytearray(0x110000 // 8)
    for cp in codepoints:
        coverage[cp // 8] |= 1 << (cp % 8)
    ranges: list[list[int]] = []
    for cp in sorted(codepoints):
        if ranges and ranges[-1][1] + 1 == cp:
            ranges[-1][1] = cp
        else:
            ranges.append([cp, cp])

    assert all(ord(char) in codepoints for char in "中文简體日本語，。𠮷")
    assert all(ord(char) not in codepoints for char in "ABCabc123😀한국어")
    assert {cp for cp in range(0x110000) if coverage[cp // 8] & (1 << (cp % 8))} == codepoints
    OUTPUT.with_suffix(".bin").write_bytes(coverage)
    OUTPUT.with_suffix(".ranges.json").write_text(json.dumps(ranges, separators=(",", ":")) + "\n")
    OUTPUT.with_suffix(".source.json").write_text(json.dumps({
        "fontPath": str(SOURCE.relative_to(ROOT)),
        "fontSha256": source_hash,
        "sourceUrl": SOURCE_URL,
        "postScriptName": font["name"].getDebugName(6),
        "familyName": font["name"].getDebugName(1),
        "version": font["name"].getDebugName(5),
        "glyphMappings": len(cmap),
        "cjkCharacters": len(codepoints),
    }, indent=2) + "\n")
    print(f"Generated Noto Sans Mono CJK SC coverage for {len(codepoints)} CJK characters")


if __name__ == "__main__":
    main()
