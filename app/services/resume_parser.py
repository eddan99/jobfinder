import re
from pathlib import Path

import fitz
import docx


class ResumeParser:
    _BLOCK_TYPE_TEXT: int = 0

    def parse(self, file_path: Path) -> str:
        if not file_path.is_file():
            raise FileNotFoundError(f"File not found: {file_path}")

        if file_path.suffix.lower() == ".pdf":
            raw_text = self._parse_pdf(file_path)
        elif file_path.suffix.lower() == ".docx":
            raw_text = self._parse_docx(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_path.suffix}")

        return self._clean_text(raw_text)

    def _parse_pdf(self, file_path: Path) -> str:
        pages_text = []
        with fitz.open(file_path) as document:
            for page in document:
                blocks = [
                    (y0, text)
                    for _, y0, _, _, text, _, block_type in page.get_text("blocks")
                    if block_type == self._BLOCK_TYPE_TEXT
                ]
                blocks.sort(key=lambda b: b[0])
                pages_text.append("\n".join(text for _, text in blocks))
        return "\n".join(pages_text)

    def _parse_docx(self, file_path: Path) -> str:
        document = docx.Document(file_path)
        return "\n".join(paragraph.text for paragraph in document.paragraphs)

    def _clean_text(self, raw_text: str) -> str:
        return re.sub(r"[^a-zA-ZåäöÅÄÖ0-9 \n]", "", raw_text)
