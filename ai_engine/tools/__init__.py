from ai_engine.tools.ocr import OcrProcessor
from ai_engine.tools.oneke import KnowledgeExtractorProcessor

knowledge_extractor = KnowledgeExtractorProcessor()

__all__ = ["OcrProcessor", "knowledge_extractor"]