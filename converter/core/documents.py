"""DOCX <-> PDF conversion."""

from pathlib import Path

from converter.utils.helpers import get_output_path, validate_input_file


def docx_to_pdf(input_path: str, output_dir: str | None = None) -> Path:
    """Convert a DOCX file to PDF using Microsoft Word (COM automation)."""
    from docx2pdf import convert

    input_file = validate_input_file(input_path)
    output_path = get_output_path(input_path, "pdf", output_dir)
    convert(str(input_file), str(output_path))
    return output_path


def pdf_to_docx(input_path: str, output_dir: str | None = None) -> Path:
    """Convert a PDF file to DOCX."""
    from pdf2docx import Converter

    input_file = validate_input_file(input_path)
    output_path = get_output_path(input_path, "docx", output_dir)
    cv = Converter(str(input_file))
    cv.convert(str(output_path))
    cv.close()
    return output_path
