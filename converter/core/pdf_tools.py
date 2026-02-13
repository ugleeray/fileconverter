"""PDF merge and split operations."""

from pathlib import Path

from converter.utils.helpers import ensure_output_dir, validate_input_file


def merge_pdfs(input_paths: list[str], output_path: str | None = None, output_dir: str | None = None) -> Path:
    """Merge multiple PDF files into one."""
    from pypdf import PdfMerger

    if len(input_paths) < 2:
        raise ValueError("Need at least 2 PDF files to merge.")

    # Validate all inputs exist
    for path in input_paths:
        validate_input_file(path)

    # Determine output path
    if output_path:
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
    else:
        out_dir = ensure_output_dir(output_dir)
        out = out_dir / "merged.pdf"

    merger = PdfMerger()
    for path in input_paths:
        merger.append(str(path))
    merger.write(str(out))
    merger.close()

    return out


def split_pdf_pages(input_path: str, pages: str, output_dir: str | None = None) -> list[Path]:
    """Split a PDF by extracting specific pages.

    Pages format: "1-3,5,8-10" (1-indexed)
    """
    from pypdf import PdfReader, PdfWriter

    input_file = validate_input_file(input_path)
    out_dir = ensure_output_dir(output_dir)
    stem = input_file.stem

    reader = PdfReader(str(input_file))
    total_pages = len(reader.pages)

    # Parse page ranges
    page_indices = _parse_page_ranges(pages, total_pages)

    # Write selected pages to a single output file
    writer = PdfWriter()
    for idx in page_indices:
        writer.add_page(reader.pages[idx])

    output_path = out_dir / f"{stem}_pages_{pages.replace(',', '_')}.pdf"
    with open(output_path, "wb") as f:
        writer.write(f)

    return [output_path]


def split_pdf_each(input_path: str, output_dir: str | None = None) -> list[Path]:
    """Split a PDF so each page becomes its own file."""
    from pypdf import PdfReader, PdfWriter

    input_file = validate_input_file(input_path)
    out_dir = ensure_output_dir(output_dir)
    stem = input_file.stem

    reader = PdfReader(str(input_file))
    output_paths = []

    for i, page in enumerate(reader.pages, start=1):
        writer = PdfWriter()
        writer.add_page(page)
        output_path = out_dir / f"{stem}_page_{i}.pdf"
        with open(output_path, "wb") as f:
            writer.write(f)
        output_paths.append(output_path)

    return output_paths


def _parse_page_ranges(pages_str: str, total_pages: int) -> list[int]:
    """Parse a page range string like '1-3,5,8-10' into 0-indexed page numbers."""
    indices = []
    for part in pages_str.split(","):
        part = part.strip()
        if "-" in part:
            start, end = part.split("-", 1)
            start, end = int(start), int(end)
            if start < 1 or end > total_pages:
                raise ValueError(f"Page range {part} is out of bounds (1-{total_pages}).")
            indices.extend(range(start - 1, end))
        else:
            page = int(part)
            if page < 1 or page > total_pages:
                raise ValueError(f"Page {page} is out of bounds (1-{total_pages}).")
            indices.append(page - 1)
    return indices
