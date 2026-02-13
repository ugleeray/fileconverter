"""Image compression for PNG, JPG/JPEG, and WEBP files."""

import os
from pathlib import Path

from converter.utils.helpers import ensure_output_dir, validate_input_file, format_file_size


def compress_image(
    input_path: str,
    quality: int = 80,
    resize: str | None = None,
    output_dir: str | None = None,
) -> tuple[Path, int, int]:
    """Compress an image file.

    Args:
        input_path: Path to the input image.
        quality: Compression quality (1-100). Lower = smaller file.
        resize: Optional resize dimensions as "WIDTHxHEIGHT" (e.g., "1920x1080").
        output_dir: Output directory.

    Returns:
        Tuple of (output_path, original_size_bytes, compressed_size_bytes).
    """
    from PIL import Image

    input_file = validate_input_file(input_path)
    out_dir = ensure_output_dir(output_dir)
    ext = input_file.suffix.lower()

    original_size = os.path.getsize(input_file)

    img = Image.open(str(input_file))

    # Resize if requested
    if resize:
        width, height = _parse_resize(resize)
        img.thumbnail((width, height), Image.LANCZOS)

    output_path = out_dir / f"{input_file.stem}_compressed{ext}"

    # Save with compression settings based on format
    if ext in (".jpg", ".jpeg"):
        if img.mode == "RGBA":
            img = img.convert("RGB")
        img.save(str(output_path), "JPEG", quality=quality, optimize=True)
    elif ext == ".png":
        img.save(str(output_path), "PNG", optimize=True)
    elif ext == ".webp":
        img.save(str(output_path), "WEBP", quality=quality)
    else:
        # Fallback for other image formats
        img.save(str(output_path), optimize=True, quality=quality)

    compressed_size = os.path.getsize(output_path)
    return output_path, original_size, compressed_size


def _parse_resize(resize_str: str) -> tuple[int, int]:
    """Parse a resize string like '1920x1080' into (width, height)."""
    parts = resize_str.lower().split("x")
    if len(parts) != 2:
        raise ValueError(f"Invalid resize format: '{resize_str}'. Use WIDTHxHEIGHT (e.g., 1920x1080).")
    return int(parts[0]), int(parts[1])
