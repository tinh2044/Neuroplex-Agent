"""Provides prompt templates and generation functions for various AI tasks."""
from datetime import datetime

def generate_time_prompt():
    """
    Generates a system prompt with the current timestamp.
    """
    return f"Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"


QA_PROMPT_WITH_KNOWLEDGE = """
Please use the retrieved information to answer the question. When answering, avoid excessive use of bullet points.

<Reference Material>:
{external}
</Reference Material>

<Question>
{query}
</Question>
"""

KNOWBASE_QA_TEMPLATE = """
You are a knowledgeable assistant helping to answer questions based on the provided knowledge base content.
Please provide accurate and relevant answers based on the given context.

<Context>
{context}
</Context>

<Question>
{query}
</Question>

Answer the question based on the context above. If the context doesn't contain enough information to answer the question, say so.
Be concise but informative. Use natural language and avoid technical jargon unless necessary.
"""

QUERY_REWRITE_PROMPT_STRICT = """
<Instruction>Based on the provided historical information, refine and rewrite the question. The rewritten question must strictly follow the content and formatting requirements. No prohibited content is allowed.<Instruction>
<Prohibited>1. Do not invent unrelated content. If no rewrite is needed, return the original question.
2. Return only the question, no other text.
3. Rewrite only, do not answer.<Prohibited>
<Content Requirements>1. Clarity: Ensure the question is clear and precise.
2. Keywords: Use relevant keywords to improve understanding.
3. Conciseness: Use brief phrases.
4. Question form: Maintain interrogative form.
5. Relevance: Use only context that directly supports the question.
6. No fabrication.<Content Requirements>
<Format Requirements>Return only the rewritten question. No instructions or metadata.<Format Requirements>
<Historical Information>{history}</Historical Information>
<Question>{query}</Question>
"""

QUERY_REWRITE_PROMPT_FLEXIBLE = """
You are an assistant helping with query rewriting. Based on the previous conversation and the latest question, rewrite multiple relevant questions to match reference materials from the knowledge base.

<Historical Information>{history}</Historical Information>
<Question>{query}</Question>
"""

NER_PROMPT_TEMPLATE = """
<Instruction>Perform named entity recognition (NER) on the following text. Return only the entities and their types.<Instruction>
<Prohibited>1. Do not fabricate content. If no entities exist, return an empty string.
2. This is strictly for entity extraction, do not answer.<Prohibited>
<Content Requirements>1. List all named entities.
2. No explanations.
3. Return only entities.
4. Separate entities with commas.<Content Requirements>
<Text>{text}</Text>
"""

KEYWORD_EXTRACTION_PROMPT = """
You are an assistant that extracts keywords for knowledge graph queries. From the input text, identify meaningful keywords for retrieval.

Return the keywords joined with <->. For example: keyword1<->keyword2<->keyword3
Do not translate keywords; keep their original language.
<Text>{text}</Text>
"""

HYDE_GENERATION_PROMPT = (
    "Please write a passage to answer the question.\n"
    "Include as many important details as possible.\n\n"
    "{context_str}\n\n"
    "{query}\n\n"
    "Passage:\n"
)
