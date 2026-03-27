# File Converter CLI

A simple command-line tool to convert, merge, split, and compress files.

## Setup

**Requirements:** Python 3.8+ and Microsoft Office (for DOCX/PPTX conversions on Windows).

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Install the CLI tool
pip install -e .

# 3. Verify it works
fileconverter --help
```

> **Note:** For PDF-to-image conversions, you also need [Poppler](https://github.com/osber/poppler-windows/releases). Download it and add the `bin/` folder to your system PATH.

## Changelog

### v1.1.0
- **Output now saves to the same folder as the input file by default** (previously always saved to `./output/`). Use `--output-dir` / `-o` to override.

---

## Commands

### Convert files

Convert a single file or batch of files to another format.

```bash
# DOCX to PDF
fileconverter convert report.docx --to pdf

# PDF to DOCX
fileconverter convert report.pdf --to docx

# PPTX to PDF
fileconverter convert slides.pptx --to pdf

# PNG to JPG
fileconverter convert photo.png --to jpg

# Batch convert all DOCX files to PDF
fileconverter convert *.docx --to pdf

# Excel to CSV
fileconverter convert data.xlsx --to csv

# CSV to Excel
fileconverter convert data.csv --to xlsx

# Markdown to HTML
fileconverter convert notes.md --to html

# Specify output directory
fileconverter convert report.docx --to pdf --output-dir ./my_pdfs
```

### Merge PDFs

Combine multiple PDF files into one.

```bash
# Merge specific files
fileconverter merge file1.pdf file2.pdf file3.pdf

# Merge with custom output name
fileconverter merge file1.pdf file2.pdf -o combined.pdf

# Merge all PDFs in current folder
fileconverter merge *.pdf
```

### Split PDFs

Extract specific pages or split every page into its own file.

```bash
# Extract pages 1-3 and page 5
fileconverter split report.pdf --pages 1-3,5

# Extract a single page
fileconverter split report.pdf --pages 7

# Split every page into its own file
fileconverter split report.pdf --each

# Specify output directory
fileconverter split report.pdf --each -o ./split_pages
```

### Compress images

Reduce file size of PNG, JPG, and WEBP images.

```bash
# Compress a single image (default quality: 80)
fileconverter compress photo.jpg

# Set custom quality (lower = smaller file)
fileconverter compress photo.jpg --quality 60

# Compress and resize
fileconverter compress photo.jpg -q 70 --resize 1920x1080

# Batch compress all JPGs
fileconverter compress *.jpg -q 70

# Specify output directory
fileconverter compress *.png -o ./compressed
```

### Show supported formats

```bash
fileconverter formats
```

---

## Supported Conversions

| From | To |
|------|----|
| DOCX | PDF |
| PDF | DOCX |
| PPTX | PDF |
| PDF | PPTX |
| PNG, JPG, BMP, TIFF, WEBP, GIF | Any other image format |
| Images | PDF |
| PDF | PNG, JPG |
| XLSX | CSV |
| CSV | XLSX |
| Markdown | HTML |

---

## Project Structure

```
fileconverter/
├── README.md               # This file
├── requirements.txt        # Python dependencies
├── setup.py                # Package installer
├── input/                  # Place input files here (optional)
├── output/                 # Optional: use --output-dir to send files here
└── converter/
    ├── cli.py              # CLI commands
    ├── core/
    │   ├── documents.py    # DOCX <-> PDF
    │   ├── presentations.py # PPTX <-> PDF
    │   ├── pdf_tools.py    # PDF merge & split
    │   ├── images.py       # Image conversions
    │   ├── spreadsheets.py # Excel <-> CSV
    │   └── compressor.py   # Image compression
    └── utils/
        └── helpers.py      # Shared utilities
```

---

## Tips

- All commands default to saving output in the **same folder as the input file**
- Use `--output-dir` / `-o` to save to a different location instead
- DOCX/PPTX to PDF requires Microsoft Office installed on Windows
- PDF to images requires Poppler installed and on PATH
- Use `fileconverter <command> --help` for detailed options on any command
