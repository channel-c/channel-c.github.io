# PDF → Markdown Enrichment Pipeline

This repository contains a small, plugin-style workflow that turns a PDF into an enriched Markdown document with AI-generated image descriptions. It wraps three existing capabilities—Marker extraction, a Visual Language Model (VLM), and a Markdown merger—behind a single command-line interface so you can reproduce the "one-click" pipeline described in the project brief.

## Repository layout
```
project/
├── cli.py                 # Command-line orchestrator
├── config.yaml            # Default configuration
├── extractor/marker_wrapper.py
├── vlm/vlm_client.py
├── merger/md_merger.py
├── utils/file_utils.py
├── requirements.txt
└── README.md
```

## Prerequisites
1. **Python 3.9+** and `pip`.
2. **Marker CLI** installed and available on the `PATH` (or update `config.yaml` with the path to the binary).
3. **VLM API access** (e.g., DeepSeek-VL) and an API key that can be passed via `--api-key` or the `VLM_API_KEY` environment variable.
4. The Python dependencies listed in `requirements.txt` (`requests`, `PyYAML`). Install them with:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration
All runtime options live in `config.yaml`:

```yaml
output_dir: output              # Where intermediate + final files go
marker:
  command: marker               # The Marker CLI command to execute
vlm:
  endpoint: https://api.deepseek.com/vl/v1
enriched_filename: book_enriched.md
image_descriptions_json: images_desc.json
```

Adjust the Marker command or VLM endpoint to match your environment, and change the filenames/output folder if desired. `cli.py` automatically loads this configuration at runtime.

## Usage plan
The end-to-end workflow consists of three automated stages. You only run a single command:

1. **Marker extraction** – `cli.py` calls `extractor/marker_wrapper.py`, which invokes the Marker CLI (compatible with `-o`, `--output-dir`, or positional output arguments) to generate `book.md` plus an `images/` folder.
2. **VLM image descriptions** – `vlm/vlm_client.py` uploads every extracted image to the configured VLM endpoint using your API key, saving the responses to `images_desc.json`.
3. **Markdown merge** – `merger/md_merger.py` scans `book.md`, finds Markdown image references, and injects the AI-generated captions underneath each figure, producing `book_enriched.md`.

To execute the entire pipeline:
```bash
python cli.py path/to/input.pdf --api-key=<YOUR_VLM_KEY>
```
Optional flags:
- `--config`: point to a different YAML configuration.
- `--api-key`: override the environment variable.

The CLI prints progress for each stage and leaves the final file (and any generated JSON/images) inside the configured `output_dir`.

## Packaging (optional)
- **As a pip package** – create a simple `setup.py` or `pyproject.toml`, then `pip install .` to get a `myRAGbuilder` entry point.
- **As a standalone binary** – run `pyinstaller --onefile cli.py` to distribute an executable for users without Python.

## Troubleshooting tips
- If `cli.py` exits complaining about the API key, re-run with `--api-key` or set `export VLM_API_KEY=...` beforehand.
- If Marker fails, confirm the `marker` command works on its own and that Ghostscript/PDF dependencies are installed.
- If the VLM step raises HTTP errors, verify the endpoint URL, API key scope, and that your firewall permits outbound HTTPS traffic.

With these pieces in place, you can repeatedly transform any PDF into a richly annotated Markdown document with a single command.
