"""Extract searchable, page-linked text from PDFs in data/raw."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pypdf import PdfReader

DATA_DIR = Path(__file__).resolve().parent
RAW_DIR = DATA_DIR / "raw"
EXTRACTED_DIR = DATA_DIR / "extracted"


def extract_pdf(pdf_path: Path) -> dict[str, Any]:
    reader = PdfReader(pdf_path)
    pages = [
        {"page_number": page_number, "text": page.extract_text() or ""}
        for page_number, page in enumerate(reader.pages, start=1)
    ]
    return {
        "source_file": pdf_path.name,
        "page_count": len(pages),
        "pages_without_extractable_text": [
            page["page_number"] for page in pages if not page["text"].strip()
        ],
        "pages": pages,
    }


def main() -> None:
    pdf_paths = sorted(RAW_DIR.glob("*.pdf"))
    if not pdf_paths:
        raise SystemExit(f"No PDF files found in {RAW_DIR}")

    EXTRACTED_DIR.mkdir(parents=True, exist_ok=True)
    for pdf_path in pdf_paths:
        extracted = extract_pdf(pdf_path)
        output_path = EXTRACTED_DIR / f"{pdf_path.stem}.json"
        output_path.write_text(
            json.dumps(extracted, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        text_pages = extracted["page_count"] - len(
            extracted["pages_without_extractable_text"]
        )
        print(
            f"{pdf_path.name}: extracted text from {text_pages}/"
            f"{extracted['page_count']} pages -> {output_path.name}"
        )


if __name__ == "__main__":
    main()