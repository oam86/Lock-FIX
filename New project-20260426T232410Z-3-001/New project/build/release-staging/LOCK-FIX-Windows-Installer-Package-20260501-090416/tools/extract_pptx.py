from __future__ import annotations

import re
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


NS = {
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
}


def slide_key(name: str) -> int:
    match = re.search(r"slide(\d+)\.xml$", name)
    return int(match.group(1)) if match else 0


def extract_text(xml: bytes) -> list[str]:
    root = ET.fromstring(xml)
    chunks: list[str] = []
    for shape in root.findall(".//p:sp", NS):
        texts = [node.text or "" for node in shape.findall(".//a:t", NS)]
        text = "".join(texts).strip()
        if text:
            chunks.append(text)
    return chunks


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: extract_pptx.py input.pptx output.md", file=sys.stderr)
        return 2

    source = Path(sys.argv[1])
    target = Path(sys.argv[2])

    with zipfile.ZipFile(source) as deck:
        slide_names = sorted(
            (name for name in deck.namelist() if re.match(r"ppt/slides/slide\d+\.xml$", name)),
            key=slide_key,
        )
        media_names = sorted(name for name in deck.namelist() if name.startswith("ppt/media/"))

        lines: list[str] = [
            f"# PPT Requirements Extract",
            "",
            f"- Source: `{source}`",
            f"- Slides: {len(slide_names)}",
            f"- Media files: {len(media_names)}",
            "",
        ]

        for index, slide_name in enumerate(slide_names, start=1):
            lines.append(f"## Slide {index}")
            chunks = extract_text(deck.read(slide_name))
            if chunks:
                lines.extend(f"- {chunk}" for chunk in chunks)
            else:
                lines.append("- (no text)")
            lines.append("")

    target.write_text("\n".join(lines), encoding="utf-8")
    print(target)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
