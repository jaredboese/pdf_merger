# PDF Watermark Tool

This tool allows you to add a watermark to PDF files using a custom font.

## Prerequisites

- Python 3.x
- `pip`  (Python package installer, pip3 also fine)

## Installation

1. After cloning, Install the required dependencies:

    ```bash
    pip install -r requirements.txt
    ```

## Usage (If you want to run the script from terminal)

1. Run the script:

    ```bash
    python pdf.py
    ```

2. Select the PDF files you want to watermark. (Can Select multipe files via shift+click)
3. Choose Templates which will decide where the text is written (Currently have Amazon and Kindle)
4. Choose the output file name and location.

## Building an Executable with PyInstaller (If you want to have it as an executable)

To create a standalone executable:

1. Run PyInstaller with the spec file:

    ```bash
    pyinstaller pdf.spec
    ```

2. The executable will be created in the `dist` directory.
