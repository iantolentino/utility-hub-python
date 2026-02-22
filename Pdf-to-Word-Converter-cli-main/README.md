# PDF to DOCX Converter

## Overview

A graphical application that converts PDF files to DOCX format, supporting both text extraction and image-based conversion methods.

## Features

- Convert single PDF files to DOCX format 
- Preserve text content from PDF documents
- Handle scanned PDFs through image-based conversion
- Simple graphical user interface
- Selectable output directory

## Requirements

### Python Packages

Install the required packages using pip:

```
pip install python-docx pillow pytesseract PyMuPDF pdf2docx
```

### System Dependencies

- **Tesseract OCR**: Required for text recognition in image-based conversion
  - Windows: Download from [GitHub Tesseract releases](https://github.com/UB-Mannheim/tesseract/wiki)
  - Linux: `sudo apt-get install tesseract-ocr`
  - macOS: `brew install tesseract`

## Installation

1. Install Python 3.7 or higher
2. Install the required packages listed above
3. Install Tesseract OCR for your operating system
4. Run the application: `python pdf_to_docx_converter.py`

## Usage

### Starting the Application

Launch the application by running the Python script:

```
python pdf_to_docx_converter.py
```

### Conversion Process

1. Click "Browse File" to select a PDF file
2. Select an output location (default: Documents/Converted_Files)
3. Click "Start Conversion"
4. Wait for the conversion to complete
5. Find the converted DOCX file in the output directory

### Conversion Methods

The application uses two conversion methods:

1. **Primary Method**: Uses pdf2docx library for better layout preservation
2. **Fallback Method**: Uses PyMuPDF (fitz) for text extraction with image embedding

## Output

Converted files are saved with the same name as the input PDF, but with a `.docx` extension. The default output location is `Documents/Converted_Files` in your user directory.

## Limitations

- Complex PDF layouts may not be perfectly preserved
- Password-protected PDFs are not supported
- Very large PDF files may take considerable time to process
- Text recognition accuracy depends on PDF quality and Tesseract configuration

## Troubleshooting

### Common Issues

1. **Missing Tesseract**:
   - Error: `TesseractNotFoundError`
   - Solution: Install Tesseract OCR and ensure it's in your system PATH

2. **Permission Errors**:
   - Ensure you have write permissions for the output directory

3. **Large File Processing**:
   - Conversion may be slow for PDFs with many pages or high-resolution images

4. **Formatting Issues**:
   - Complex tables or multi-column layouts may not convert perfectly

### Logs

The application prints conversion status and errors to the console. Check the console output for detailed error messages if conversion fails.

## Development

### Code Structure

- `PDFtoDocxConverter` class: Main application class
- `convert_with_pdf2docx()`: Primary conversion method using pdf2docx
- `convert_with_fitz()`: Fallback conversion method using PyMuPDF
- `setup_ui()`: GUI initialization

### Adding Features

To extend functionality:

1. Modify `convert_with_pdf2docx()` for improved layout handling
2. Adjust image extraction parameters in `convert_with_fitz()` for different PDF types
3. Add batch processing by modifying the file selection interface

## License

This application uses several open-source libraries. Refer to their respective licenses for usage terms.

## Support

For issues or questions, check the console output for error details and ensure all dependencies are correctly installed.
