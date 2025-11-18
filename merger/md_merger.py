"""Merge VLM generated descriptions into a Markdown document."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict


IMAGE_BLOCK_HEADER = "### 图表解析（AI 自动生成）"


def _load_descriptions(json_desc_file: Path) -> Dict[str, str]:
    data = json.loads(json_desc_file.read_text(encoding="utf-8"))
    return {str(key): str(value) for key, value in data.items()}


def merge_descriptions(md_file: Path, json_desc_file: Path, out_file: Path) -> Path:
    """Insert AI generated descriptions after every image reference."""
    md_text = md_file.read_text(encoding="utf-8")
    descriptions = _load_descriptions(json_desc_file)

    new_lines = []
    for line in md_text.splitlines():
        new_lines.append(line)
        stripped = line.strip()
        if stripped.startswith("![") and ")" in stripped:
            start = stripped.find("(") + 1
            end = stripped.find(")", start)
            if start > 0 and end > start:
                filename = stripped[start:end].split("/")[-1]
                if filename in descriptions:
                    new_lines.append(IMAGE_BLOCK_HEADER)
                    new_lines.append(descriptions[filename])
                    new_lines.append("")

    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
    return out_file
