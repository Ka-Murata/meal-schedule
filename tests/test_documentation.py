from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MARKDOWN_LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


class DocumentationTests(unittest.TestCase):
    def test_document_links(self) -> None:
        missing: list[str] = []
        markdown_files = [ROOT / "README.md", ROOT / "AGENTS.md", ROOT / "ARCHITECTURE.md"]
        markdown_files.extend((ROOT / "docs").rglob("*.md"))
        for document in markdown_files:
            text = document.read_text(encoding="utf-8")
            for target in MARKDOWN_LINK.findall(text):
                if target.startswith(("#", "http://", "https://", "mailto:")):
                    continue
                path_text = target.split("#", 1)[0]
                if not path_text:
                    continue
                destination = (document.parent / path_text).resolve()
                if not destination.exists():
                    missing.append(f"{document.relative_to(ROOT)} -> {target}")
        self.assertEqual([], missing, "存在しない文書リンク:\n" + "\n".join(missing))


if __name__ == "__main__":
    unittest.main()
