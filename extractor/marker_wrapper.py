"""Utilities for invoking the Marker CLI to convert PDFs into Markdown."""
from __future__ import annotations

import subprocess
from pathlib import Path
from typing import List, Sequence, Tuple


def _run_candidate_command(cmd: Sequence[str]) -> Tuple[bool, str]:
    """Execute a candidate Marker CLI command and return its success + stderr."""
    completed = subprocess.run(cmd, capture_output=True, text=True)
    success = completed.returncode == 0
    stderr = (completed.stderr or "").strip()
    stdout = (completed.stdout or "").strip()
    details = "\n".join(filter(None, [stderr, stdout]))
    return success, details


def run_marker(input_pdf: str, output_dir: str, marker_cmd: str = "marker") -> Tuple[Path, Path]:
    """Run the Marker CLI and return the generated markdown file and image dir."""
    input_path = Path(input_pdf)
    if not input_path.exists():
        raise FileNotFoundError(f"Input PDF does not exist: {input_pdf}")

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    attempts: List[List[str]] = [
        [marker_cmd, str(input_path), "-o", str(output_path)],
        [marker_cmd, str(input_path), "--output-dir", str(output_path)],
        [marker_cmd, str(input_path), str(output_path)],
    ]

    errors = []
    for cmd in attempts:
        success, details = _run_candidate_command(cmd)
        if success:
            break
        errors.append((cmd, details))
    else:
        rendered_errors = "\n".join(
            f"  {' '.join(c)}\n    {d or 'No stderr captured.'}" for c, d in errors
        )
        raise RuntimeError(
            "Marker CLI failed to run with the supported argument patterns:\n" + rendered_errors
        )

    md_file = output_path / "book.md"
    images_dir = output_path / "images"

    if not md_file.exists():
        raise FileNotFoundError(f"Marker did not produce expected markdown file: {md_file}")

    images_dir.mkdir(exist_ok=True)

    return md_file, images_dir
