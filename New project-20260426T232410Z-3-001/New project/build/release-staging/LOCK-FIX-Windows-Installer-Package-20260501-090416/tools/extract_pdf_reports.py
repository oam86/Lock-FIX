from __future__ import annotations

import sys
from pathlib import Path

from pypdf import PdfReader


def extract_pdf(path: Path) -> tuple[int, list[str]]:
    reader = PdfReader(str(path))
    pages: list[str] = []
    for index, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        normalized = "\n".join(line.strip() for line in text.splitlines() if line.strip())
        pages.append(f"## {path.name} / Page {index}\n\n{normalized}\n")
    return len(reader.pages), pages


def main() -> int:
    if len(sys.argv) < 4:
        print("usage: extract_pdf_reports.py output.md input1.pdf input2.pdf ...", file=sys.stderr)
        return 2

    output = Path(sys.argv[1])
    inputs = [Path(arg) for arg in sys.argv[2:]]

    lines = ["# Integrated PDF Requirements", ""]
    for pdf in inputs:
        count, pages = extract_pdf(pdf)
        lines.append(f"# Source: {pdf}")
        lines.append(f"- Pages: {count}")
        lines.append("")
        lines.extend(pages)
        lines.append("")

    output.write_text("\n".join(lines), encoding="utf-8")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
