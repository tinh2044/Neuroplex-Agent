"""
Test module for the KnowledgeExtractorProcessor class.

This module contains unit tests for the KnowledgeExtractorProcessor functionality,
testing the knowledge extraction capabilities using mocked ML models and tokenizers.
Tests cover the core extraction functionality with simulated model responses.
"""

import unittest
from unittest.mock import patch, MagicMock
from ai_engine.tools.oneke import KnowledgeExtractorProcessor


class TestKnowledgeExtractorProcessor(unittest.TestCase):
    """
    Test suite for KnowledgeExtractorProcessor class.
    
    Tests the knowledge extraction functionality using mocked versions of:
    - AutoTokenizer
    - AutoModelForCausalLM
    - GenerationConfig
    - AutoConfig
    - BitsAndBytesConfig
    
    Verifies the processor can properly initialize models and execute
    knowledge extraction tasks with the expected output format.
    """

    @patch('ai_engine.tools.oneke.AutoTokenizer')
    @patch('ai_engine.tools.oneke.AutoModelForCausalLM')
    @patch('ai_engine.tools.oneke.GenerationConfig')
    @patch('ai_engine.tools.oneke.AutoConfig')
    @patch('ai_engine.tools.oneke.BitsAndBytesConfig')
    def test_execute_knowledge_extraction(self, MockBits, MockAutoConfig, MockGenConfig, MockModel, MockTokenizer):
        """
        Test the knowledge extraction execution pipeline.
        
        Tests the complete knowledge extraction process including:
        - Model and tokenizer initialization
        - Input processing
        - Model inference
        - Output decoding and formatting
        
        Args:
            MockBits: Mock for BitsAndBytesConfig
            MockAutoConfig: Mock for AutoConfig
            MockGenConfig: Mock for GenerationConfig
            MockModel: Mock for AutoModelForCausalLM
            MockTokenizer: Mock for AutoTokenizer
            
        Verifies:
            - Proper model initialization
            - Correct tokenizer usage
            - Expected output format
            - Successful extraction result
        """
        # Mock tokenizer
        mock_tokenizer = MockTokenizer.from_pretrained.return_value
        mock_tokenizer.encode.return_value = MagicMock(size=lambda: (1, 5), to=lambda device: MagicMock(size=lambda: (1, 5)))
        mock_tokenizer.eos_token_id = 0
        mock_tokenizer.decode.return_value = '{"entity": "test"}'

        # Mock model
        mock_model = MockModel.from_pretrained.return_value
        mock_model.device = 'cpu'
        mock_model.generate.return_value = MagicMock(sequences=[[0,1,2,3,4,5,6]])
        mock_model.eval.return_value = None

        # Mock generation config
        MockGenConfig.from_pretrained.return_value = MagicMock()
        MockAutoConfig.from_pretrained.return_value = MagicMock()
        MockBits.return_value = MagicMock()

        processor = KnowledgeExtractorProcessor(model_repository="fake/repo")
        result = processor.execute_knowledge_extraction(
            content="test content",
            schema_definition={"entity": "type"},
            operation_type="entity_extraction",
            lang_code="en"
        )
        self.assertEqual(result, ['{"entity": "test"}'])


if __name__ == '__main__':
    unittest.main() 