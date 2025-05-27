import os
import tempfile
from pathlib import Path
from argparse import ArgumentParser

import fitz  
import numpy as np
from PIL import Image
from tqdm import tqdm
import easyocr
from llama_index.readers.file import PDFReader
from ai_engine.utils.logging import logger
from ai_engine.utils import is_text_pdf


class OcrProcessor:
    """A class for performing OCR (Optical Character Recognition) on images and PDFs using EasyOCR.

    This class provides functionality to:
    - Extract text from images in various formats (file path, numpy array, PIL Image)
    - Process both text-based and scanned PDFs
    - Handle multiple languages (defaults to Vietnamese)

    Attributes:
        languages (list): List of language codes for OCR. Defaults to ['vi'] (Vietnamese)
        reader (easyocr.Reader): EasyOCR reader instance

    Example:
        >>> processor = EasyOcrProcessor(languages=['vi', 'en'])
        >>> text = processor.recognize_text_from_image('image.png')
        >>> pdf_text = processor.extract_text_from_pdf('document.pdf')
    """
    def __init__(self, languages=None):
        self.languages = languages or ['vi']
        self.reader = easyocr.Reader(self.languages, gpu=False)
        logger.info("EasyOCR engine initialized.")

    def recognize_text_from_image(self, image_input):
        """Extract text from an image using OCR.

        Args:
            image_input: The input image in one of these formats:
                - str: Path to image file
                - numpy.ndarray: Image as numpy array
                - PIL.Image: PIL Image object

        Returns:
            str: Extracted text from the image, with line breaks between text blocks

        Raises:
            ValueError: If the input image format is not valid
            FileNotFoundError: If the image file path doesn't exist
        """
        if isinstance(image_input, str):
            image_path = image_input
            cleanup = False
        else:
            image_path, cleanup = self._save_temp_image(image_input)

        try:
            results = self.reader.readtext(image_path)
            return "\n".join([line[1] for line in results])
        finally:
            if cleanup and os.path.exists(image_path):
                os.remove(image_path)

    def extract_text_from_pdf(self, pdf_file_path):
        """Extract text from a PDF file, handling both text-based and scanned PDFs.

        For text-based PDFs, directly extracts text content.
        For scanned PDFs, performs OCR on each page.

        Args:
            pdf_file_path (str): Path to the PDF file

        Returns:
            str: Extracted text from the PDF, with double line breaks between pages

        Raises:
            FileNotFoundError: If the PDF file doesn't exist
        """
        if not os.path.exists(pdf_file_path):
            raise FileNotFoundError(f"File not found: {pdf_file_path}")

        if is_text_pdf(pdf_file_path):
            return self._extract_text_pdf_content(pdf_file_path)
        else:
            return self._process_scanned_pdf(pdf_file_path)

    def _extract_text_pdf_content(self, pdf_path):
        documents = PDFReader().load_data(file=Path(pdf_path))
        return "\n\n".join([doc.get_content() for doc in documents])

    def _process_scanned_pdf(self, pdf_path):
        image_paths = self._convert_pdf_to_images(pdf_path)
        full_text = [self.recognize_text_from_image(img) for img in tqdm(image_paths, desc="OCR", ncols=80)]
        return "\n\n".join(full_text)

    def _convert_pdf_to_images(self, pdf_path):
        doc = fitz.open(pdf_path)
        temp_dir = tempfile.mkdtemp(prefix="easyocr_pdf_")
        saved_images = []

        for i in tqdm(range(doc.page_count), desc="Rendering", ncols=80):
            page = doc[i]
            matrix = fitz.Matrix(2, 2)
            pix = page.get_pixmap(matrix=matrix, alpha=False)
            img_file = os.path.join(temp_dir, f"page_{i + 1}.png")
            pix.save(img_file)
            saved_images.append(img_file)

        return saved_images

    def _save_temp_image(self, image_data):
        if isinstance(image_data, np.ndarray):
            image_data = Image.fromarray(image_data)

        if not isinstance(image_data, Image.Image):
            raise ValueError("Input image is not valid.")

        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_file:
            image_data.save(tmp_file.name)
            return tmp_file.name, True


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--pdf", help="Path to PDF file")
    parser.add_argument("--img", help="Path to image file")
    args = parser.parse_args()

    processor = OcrProcessor()

    if args.pdf:
        output_text = processor.extract_text_from_pdf(args.pdf)
    elif args.img:
        output_text = processor.recognize_text_from_image(args.img)
    else:
        raise ValueError("--pdf or --img is required")

    print(output_text)
