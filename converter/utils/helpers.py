"""Shared utilities for file conversion operations."""

import os
from pathlib import Path

# Default directories
PROJECT_ROOT = Path(__file__).parent.parent.parent
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "output"

# Supported format mappings
FORMAT_EXTENSIONS = {
    "pdf": ".pdf",
    "docx": ".docx",
    "pptx": ".pptx",
    "png": ".png",
    "jpg": ".jpg",
    "jpeg": ".jpeg",
    "bmp": ".bmp",
    "tiff": ".tiff",
    "webp": ".webp",
    "gif": ".gif",
    "csv": ".csv",
    "xlsx": ".xlsx",
    "html": ".html",
    "md": ".md",
}

IMAGE_FORMATS = {"png", "jpg", "jpeg", "bmp", "tiff", "webp", "gif"}
DOCUMENT_FORMATS = {"docx", "pdf"}
PRESENTATION_FORMATS = {"pptx", "pdf"}
SPREADSHEET_FORMATS = {"xlsx", "csv"}


def ensure_output_dir(output_dir: str | None, input_path: str | None = None) -> Path:
    """Ensure the output directory exists and return its Path.

    If output_dir is None and input_path is given, uses the input file's directory.
    Falls back to DEFAULT_OUTPUT_DIR only when neither is provided.
    """
    if output_dir:
        path = Path(output_dir)
    elif input_path:
        path = Path(input_path).parent
    else:
        path = DEFAULT_OUTPUT_DIR
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_output_path(input_path: str, target_format: str, output_dir: str | None) -> Path:
    """Generate the output file path for a conversion."""
    if output_dir:
        out_dir = ensure_output_dir(output_dir)
    else:
        out_dir = Path(input_path).parent
    input_name = Path(input_path).stem
    ext = FORMAT_EXTENSIONS.get(target_format.lower(), f".{target_format}")
    return out_dir / f"{input_name}{ext}"


def get_file_extension(filepath: str) -> str:
    """Get the lowercase extension of a file without the dot."""
    return Path(filepath).suffix.lower().lstrip(".")


def format_file_size(size_bytes: int) -> str:
    """Format a file size in bytes to a human-readable string."""
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def validate_input_file(filepath: str) -> Path:
    """Validate that an input file exists and return its Path."""
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    if not path.is_file():
        raise ValueError(f"Not a file: {filepath}")
    return path


def resolve_files(file_patterns: tuple[str, ...]) -> list[Path]:
    """Resolve file patterns (including globs) to a list of existing file paths."""
    import glob as glob_module

    files = []
    for pattern in file_patterns:
        # If it's an exact file path
        path = Path(pattern)
        if path.exists() and path.is_file():
            files.append(path)
        else:
            # Try glob expansion
            matches = glob_module.glob(pattern, recursive=True)
            for match in sorted(matches):
                p = Path(match)
                if p.is_file():
                    files.append(p)

    if not files:
        raise FileNotFoundError(f"No files found matching: {', '.join(file_patterns)}")

    return files
