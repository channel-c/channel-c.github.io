"""Utilities for invoking the Marker CLI to convert PDFs into Markdown."""
from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Tuple


def run_marker(input_pdf: str, output_dir: str, marker_cmd: str = "marker") -> Tuple[Path, Path]:
    """Run the Marker CLI and return the generated markdown file and image dir."""
    input_path = Path(input_pdf)
    if not input_path.exists():
        raise FileNotFoundError(f"Input PDF does not exist: {input_pdf}")

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    cmd = [marker_cmd, str(input_path), "-o", str(output_path)]

    subprocess.run(cmd, check=True)

    md_file = output_path / "book.md"
    images_dir = output_path / "images"

    if not md_file.exists():
        raise FileNotFoundError(f"Marker did not produce expected markdown file: {md_file}")

    images_dir.mkdir(exist_ok=True)

    return md_file, images_dir
