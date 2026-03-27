"""File Converter CLI - main entry point."""

import sys

import click
from rich.console import Console
from rich.table import Table

from converter.utils.helpers import (
    get_file_extension,
    format_file_size,
    resolve_files,
    IMAGE_FORMATS,
)

console = Console()


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """A simple file converter CLI.

    Convert between file formats, merge/split PDFs, and compress images.
    """
    pass


# ── Convert command ──────────────────────────────────────────────────────────


@cli.command()
@click.argument("files", nargs=-1, required=True)
@click.option("--to", "target", required=True, help="Target format (e.g., pdf, docx, png, csv).")
@click.option("--output-dir", "-o", default=None, help="Output directory (default: same folder as input file).")
def convert(files, target, output_dir):
    """Convert files to another format.

    Examples:

        fileconverter convert report.docx --to pdf

        fileconverter convert *.png --to jpg

        fileconverter convert data.xlsx --to csv
    """
    target = target.lower()

    try:
        resolved = resolve_files(files)
    except FileNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)

    console.print(f"Converting {len(resolved)} file(s) to [bold]{target}[/bold]...\n")

    for filepath in resolved:
        ext = get_file_extension(str(filepath))
        try:
            result = _do_convert(str(filepath), ext, target, output_dir)
            console.print(f"  [green]OK[/green]  {filepath.name} -> {result.name}")
        except Exception as e:
            err_msg = str(e) or type(e).__name__
            console.print(f"  [red]FAIL[/red]  {filepath.name}: {err_msg}")

    console.print("\n[bold]Done![/bold]")


def _do_convert(input_path: str, source_format: str, target_format: str, output_dir: str | None):
    """Route a conversion to the appropriate handler."""
    # DOCX conversions
    if source_format == "docx" and target_format == "pdf":
        from converter.core.documents import docx_to_pdf
        return docx_to_pdf(input_path, output_dir)

    if source_format == "pdf" and target_format == "docx":
        from converter.core.documents import pdf_to_docx
        return pdf_to_docx(input_path, output_dir)

    # PPTX conversions
    if source_format == "pptx" and target_format == "pdf":
        from converter.core.presentations import pptx_to_pdf
        return pptx_to_pdf(input_path, output_dir)

    if source_format == "pdf" and target_format == "pptx":
        from converter.core.presentations import pdf_to_pptx
        return pdf_to_pptx(input_path, output_dir)

    # Image conversions
    if source_format in IMAGE_FORMATS and target_format in IMAGE_FORMATS:
        from converter.core.images import convert_image
        return convert_image(input_path, target_format, output_dir)

    if source_format in IMAGE_FORMATS and target_format == "pdf":
        from converter.core.images import images_to_pdf
        return images_to_pdf([input_path], output_dir=output_dir)

    if source_format == "pdf" and target_format in IMAGE_FORMATS:
        from converter.core.images import pdf_to_images
        results = pdf_to_images(input_path, target_format, output_dir)
        return results[0] if results else None

    # Spreadsheet conversions
    if source_format == "xlsx" and target_format == "csv":
        from converter.core.spreadsheets import xlsx_to_csv
        return xlsx_to_csv(input_path, output_dir)

    if source_format == "csv" and target_format == "xlsx":
        from converter.core.spreadsheets import csv_to_xlsx
        return csv_to_xlsx(input_path, output_dir)

    # Markdown to HTML
    if source_format == "md" and target_format == "html":
        return _md_to_html(input_path, output_dir)

    raise ValueError(f"Unsupported conversion: {source_format} -> {target_format}")


def _md_to_html(input_path: str, output_dir: str | None):
    """Convert Markdown to HTML."""
    import markdown as md_lib
    from converter.utils.helpers import get_output_path, validate_input_file

    input_file = validate_input_file(input_path)
    output_path = get_output_path(input_path, "html", output_dir)

    text = input_file.read_text(encoding="utf-8")
    html = md_lib.markdown(text, extensions=["tables", "fenced_code"])

    html_doc = f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><title>{input_file.stem}</title></head>
<body>
{html}
</body>
</html>"""

    output_path.write_text(html_doc, encoding="utf-8")
    return output_path


# ── Merge command ────────────────────────────────────────────────────────────


@cli.command()
@click.argument("files", nargs=-1, required=True)
@click.option("--output", "-o", default=None, help="Output file path (default: ./output/merged.pdf).")
@click.option("--output-dir", default=None, help="Output directory (default: same folder as first input file).")
def merge(files, output, output_dir):
    """Merge multiple PDF files into one.

    Examples:

        fileconverter merge file1.pdf file2.pdf file3.pdf

        fileconverter merge *.pdf -o combined.pdf
    """
    try:
        resolved = resolve_files(files)
    except FileNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)

    # Validate all are PDFs
    non_pdfs = [f for f in resolved if get_file_extension(str(f)) != "pdf"]
    if non_pdfs:
        console.print(f"[red]Error:[/red] Non-PDF files found: {', '.join(str(f) for f in non_pdfs)}")
        sys.exit(1)

    console.print(f"Merging {len(resolved)} PDF files...\n")
    for f in resolved:
        console.print(f"  + {f.name}")

    try:
        from converter.core.pdf_tools import merge_pdfs
        result = merge_pdfs([str(f) for f in resolved], output_path=output, output_dir=output_dir)
        console.print(f"\n[green]Merged into:[/green] {result}")
    except Exception as e:
        console.print(f"\n[red]Error:[/red] {e}")
        sys.exit(1)


# ── Split command ────────────────────────────────────────────────────────────


@cli.command()
@click.argument("file", required=True)
@click.option("--pages", "-p", default=None, help="Page ranges to extract (e.g., '1-3,5,8-10').")
@click.option("--each", is_flag=True, default=False, help="Split every page into its own PDF.")
@click.option("--output-dir", "-o", default=None, help="Output directory (default: same folder as input file).")
def split(file, pages, each, output_dir):
    """Split a PDF into separate files.

    Examples:

        fileconverter split report.pdf --pages 1-3,5

        fileconverter split report.pdf --each
    """
    if not pages and not each:
        console.print("[red]Error:[/red] Specify either --pages or --each.")
        sys.exit(1)

    try:
        from converter.core.pdf_tools import split_pdf_pages, split_pdf_each

        if each:
            console.print(f"Splitting every page of [bold]{file}[/bold]...\n")
            results = split_pdf_each(file, output_dir)
        else:
            console.print(f"Extracting pages [bold]{pages}[/bold] from [bold]{file}[/bold]...\n")
            results = split_pdf_pages(file, pages, output_dir)

        for r in results:
            console.print(f"  [green]Created:[/green] {r.name}")

        console.print(f"\n[bold]Done![/bold] {len(results)} file(s) created.")

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


# ── Compress command ─────────────────────────────────────────────────────────


@cli.command()
@click.argument("files", nargs=-1, required=True)
@click.option("--quality", "-q", default=80, type=int, help="Compression quality 1-100 (default: 80).")
@click.option("--resize", "-r", default=None, help="Resize to WIDTHxHEIGHT (e.g., 1920x1080).")
@click.option("--output-dir", "-o", default=None, help="Output directory (default: same folder as input file).")
def compress(files, quality, resize, output_dir):
    """Compress image files (PNG, JPG, WEBP) to reduce file size.

    Examples:

        fileconverter compress photo.jpg --quality 70

        fileconverter compress *.png -q 60 --resize 1920x1080
    """
    try:
        resolved = resolve_files(files)
    except FileNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)

    console.print(f"Compressing {len(resolved)} file(s) at quality={quality}...\n")

    table = Table(show_header=True)
    table.add_column("File", style="cyan")
    table.add_column("Original", justify="right")
    table.add_column("Compressed", justify="right")
    table.add_column("Saved", justify="right", style="green")

    total_original = 0
    total_compressed = 0

    from converter.core.compressor import compress_image

    for filepath in resolved:
        try:
            result_path, orig_size, comp_size = compress_image(
                str(filepath), quality=quality, resize=resize, output_dir=output_dir
            )
            saved = orig_size - comp_size
            pct = (saved / orig_size * 100) if orig_size > 0 else 0
            total_original += orig_size
            total_compressed += comp_size

            table.add_row(
                filepath.name,
                format_file_size(orig_size),
                format_file_size(comp_size),
                f"-{pct:.1f}%",
            )
        except Exception as e:
            table.add_row(filepath.name, "-", "-", f"[red]Error: {e}[/red]")

    console.print(table)

    if total_original > 0:
        total_saved = total_original - total_compressed
        total_pct = (total_saved / total_original * 100)
        console.print(
            f"\n[bold]Total:[/bold] {format_file_size(total_original)} -> "
            f"{format_file_size(total_compressed)} "
            f"([green]-{total_pct:.1f}%[/green])"
        )


# ── Supported formats command ───────────────────────────────────────────────


@cli.command(name="formats")
def show_formats():
    """Show all supported conversion formats."""
    table = Table(title="Supported Conversions", show_header=True)
    table.add_column("From", style="cyan")
    table.add_column("To", style="green")

    conversions = [
        ("DOCX", "PDF"),
        ("PDF", "DOCX"),
        ("PPTX", "PDF"),
        ("PDF", "PPTX"),
        ("PNG/JPG/BMP/TIFF/WEBP/GIF", "Any other image format"),
        ("Images", "PDF"),
        ("PDF", "PNG/JPG"),
        ("XLSX", "CSV"),
        ("CSV", "XLSX"),
        ("Markdown (.md)", "HTML"),
    ]

    for src, dst in conversions:
        table.add_row(src, dst)

    console.print(table)
    console.print("\n[bold]Other features:[/bold] PDF merge, PDF split, Image compression")


if __name__ == "__main__":
    cli()

