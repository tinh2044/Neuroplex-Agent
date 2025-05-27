from ai_engine.tools.ocr import OcrProcessor
from ai_engine.tools.oneke import KnowledgeExtractorProcessor

ocr = OcrProcessor()
knowledge_extractor = KnowledgeExtractorProcessor()

__all__ = ["ocr", "knowledge_extractor"]