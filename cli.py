"""Command line entry-point for the PDF → Markdown enrichment workflow."""
from __future__ import annotations

import argparse
import os

from extractor.marker_wrapper import run_marker
from merger.md_merger import merge_descriptions
from utils.file_utils import ensure_directory, load_config
from vlm.vlm_client import batch_describe_images


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build enriched markdown from a PDF.")
    parser.add_argument("pdf", help="Path to the input PDF file")
    parser.add_argument("--config", default="config.yaml", help="Path to YAML configuration")
    parser.add_argument("--api-key", dest="api_key", default=os.getenv("VLM_API_KEY"), help="API key for the VLM service")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not args.api_key:
        raise SystemExit("An API key must be provided via --api-key or the VLM_API_KEY environment variable.")

    config = load_config(args.config)
    output_dir = ensure_directory(config.get("output_dir", "output"))

    marker_cmd = config.get("marker", {}).get("command", "marker")
    vlm_endpoint = config.get("vlm", {}).get("endpoint")
    if not vlm_endpoint:
        raise SystemExit("VLM endpoint must be specified in the configuration file.")

    enriched_name = config.get("enriched_filename", "book_enriched.md")
    desc_json_name = config.get("image_descriptions_json", "images_desc.json")

    print("阶段1：运行 Marker...")
    md_file, images_dir = run_marker(args.pdf, str(output_dir), marker_cmd=marker_cmd)

    print("阶段2：调用 VLM 描述所有图像...")
    desc_json = batch_describe_images(images_dir, args.api_key, vlm_endpoint, output_dir / desc_json_name)

    print("阶段3：合并为 enriched markdown...")
    final_md = merge_descriptions(md_file, desc_json, output_dir / enriched_name)

    print("完成！输出文件：", final_md)


if __name__ == "__main__":
    main()
