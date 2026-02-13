from setuptools import setup, find_packages

setup(
    name="fileconverter",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "click>=8.0",
        "pypdf>=3.0",
        "docx2pdf>=0.1.8",
        "pdf2docx>=0.5.6",
        "python-pptx>=0.6.21",
        "pdf2image>=1.16",
        "Pillow>=10.0",
        "openpyxl>=3.1",
        "rich>=13.0",
        "markdown>=3.4",
    ],
    entry_points={
        "console_scripts": [
            "fileconverter=converter.cli:cli",
        ],
    },
    python_requires=">=3.8",
)
