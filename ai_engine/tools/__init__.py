from ai_engine.tools.ocr import OCRPlugin
from ai_engine.tools.oneke import KnowledgeExtractorProcessor

ocr = OCRPlugin()
knowledge_extractor = KnowledgeExtractorProcessor()

__all__ = ["ocr", "knowledge_extractor"]