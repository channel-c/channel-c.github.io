"""Client helpers for sending images to a Visual Language Model service."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict

import requests

PROMPT_TEMPLATE = (
    "You are an expert technical writer. Describe the visual content in detail, "
    "including axes, legends, and any notable patterns or anomalies."
)


def describe_image(api_key: str, image_path: Path, endpoint: str) -> str:
    """Send a single image to the VLM endpoint and return the textual description."""
    headers = {"Authorization": f"Bearer {api_key}"}

    with image_path.open("rb") as fh:
        files = {"image": fh}
        data = {"prompt": PROMPT_TEMPLATE}
        response = requests.post(endpoint, headers=headers, files=files, data=data, timeout=60)

    response.raise_for_status()
    payload = response.json()
    return payload.get("text", "")


def batch_describe_images(image_folder: Path, api_key: str, endpoint: str, output_json: Path) -> Path:
    """Describe every image inside ``image_folder`` and persist the results as JSON."""
    results: Dict[str, str] = {}

    for image_path in sorted(image_folder.glob("*")):
        if not image_path.is_file():
            continue
        description = describe_image(api_key, image_path, endpoint)
        results[image_path.name] = description

    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    return output_json
