import unittest
from unittest.mock import patch, MagicMock
import numpy as np
from ai_engine.tools.ocr import EasyOcrProcessor

class TestEasyOcrProcessor(unittest.TestCase):
    @patch('ai_engine.tools.ocr.easyocr.Reader')
    def test_recognize_text_from_image_numpy(self, MockReader):
        # Mock kết quả trả về của easyocr
        mock_reader_instance = MockReader.return_value
        mock_reader_instance.readtext.return_value = [
            (None, 'Hello', None),
            (None, 'World', None)
        ]
        processor = EasyOcrProcessor(languages=['en'])
        # Tạo ảnh giả dạng numpy array
        img = np.zeros((10, 10, 3), dtype=np.uint8)
        text = processor.recognize_text_from_image(img)
        self.assertEqual(text, 'Hello\nWorld')

if __name__ == '__main__':
    unittest.main() 