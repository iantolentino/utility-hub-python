# Universal PDF Converter

A desktop application for converting PDF files to various formats including DOCX, images (PNG/JPG), and text files.

## Features

- **Multiple Conversion Formats**: DOCX, PNG, JPG, TXT, PDF copy
- **Flexible Conversion Modes**: Single file, batch files, or entire folders
- **Two DOCX Methods**: Image-based (scanned PDFs) and text extraction
- **Quality Options**: High DPI conversion and experimental OCR
- **Library Management**: Auto-detects and installs missing dependencies

## Installation

1. **Install Python 3.6+** from [python.org](https://python.org)

2. **Run the application**:
   ```bash
   python pdf_converter.py
   ```

The app will automatically check for and install required libraries.

## Required Libraries

- `PyMuPDF` (fitz) - PDF text/image extraction
- `python-docx` - Word document creation  
- `pdf2image` - PDF to image conversion
- `Pillow` - Image processing
- `PyPDF2` - Alternative PDF text extraction

## Usage

1. **Select conversion format** (DOCX, PNG, JPG, TXT)
2. **Choose conversion mode** (Single/Batch/Folder)
3. **Select input files/folder**
4. **Set output location**
5. **Click "Start Conversion"**

## Output

Converted files are saved to the specified output folder with original filenames preserved.

## Notes

- For complex PDFs with tables/layouts, consider online converters like SmallPDF or iLovePDF
- Image-based DOCX conversion works best for scanned PDFs
- Text extraction works for text-based PDFs

---

**Platform**: Windows/macOS/Linux  
**License**: Open Source
