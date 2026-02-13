"""Image format conversions (PNG, JPG, BMP, TIFF, WEBP, GIF) and image <-> PDF."""

from pathlib import Path

from converter.utils.helpers import get_output_path, validate_input_file, ensure_output_dir


def convert_image(input_path: str, target_format: str, output_dir: str | None = None) -> Path:
    """Convert an image from one format to another."""
    from PIL import Image

    input_file = validate_input_file(input_path)
    output_path = get_output_path(input_path, target_format, output_dir)

    img = Image.open(str(input_file))

    # Handle RGBA -> RGB for formats that don't support alpha
    if target_format.lower() in ("jpg", "jpeg", "bmp") and img.mode == "RGBA":
        background = Image.new("RGB", img.size, (255, 255, 255))
        background.paste(img, mask=img.split()[3])
        img = background
    elif img.mode == "RGBA" and target_format.lower() not in ("png", "webp", "tiff", "gif"):
        img = img.convert("RGB")

    img.save(str(output_path))
    return output_path


def images_to_pdf(input_paths: list[str], output_path: str | None = None, output_dir: str | None = None) -> Path:
    """Convert one or more images to a single PDF (each image becomes a page)."""
    from PIL import Image

    if not input_paths:
        raise ValueError("No input images provided.")

    # Determine output path
    if output_path:
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
    else:
        out_dir = ensure_output_dir(output_dir)
        stem = Path(input_paths[0]).stem
        out = out_dir / f"{stem}.pdf"

    # Open all images and convert to RGB
    images = []
    for path in input_paths:
        validate_input_file(path)
        img = Image.open(str(path))
        if img.mode == "RGBA":
            background = Image.new("RGB", img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[3])
            img = background
        elif img.mode != "RGB":
            img = img.convert("RGB")
        images.append(img)

    # Save first image with the rest appended
    first = images[0]
    if len(images) > 1:
        first.save(str(out), save_all=True, append_images=images[1:])
    else:
        first.save(str(out))

    return out


def pdf_to_images(
    input_path: str, target_format: str = "png", output_dir: str | None = None
) -> list[Path]:
    """Convert each page of a PDF to an image."""
    from pdf2image import convert_from_path

    input_file = validate_input_file(input_path)
    out_dir = ensure_output_dir(output_dir)
    stem = input_file.stem

    images = convert_from_path(str(input_file))
    output_paths = []

    for i, image in enumerate(images, start=1):
        out_path = out_dir / f"{stem}_page_{i}.{target_format}"
        image.save(str(out_path), target_format.upper())
        output_paths.append(out_path)

    return output_paths
