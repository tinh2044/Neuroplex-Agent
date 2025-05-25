from datetime import datetime

def get_system_prompt():
    return (f"Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")


knowbase_qa_template = """
Please use the retrieved information to answer the question. When answering, do not overuse bullet points.

<Reference Material>:
{external}
</Reference Material>

<Question>
{query}
</Question>"
"""

rewritten_query_prompt_template = """
<Instruction>Based on the provided historical information, optimize and rewrite the question. The returned question must strictly comply with the following content and format requirements. Absolutely no prohibited content is allowed.<Instruction>
<Prohibited>1. Absolutely do not fabricate irrelevant content. If you cannot rewrite or there is no need to rewrite, just return the original question.
2. Only return the question, do not return any other content.
3. Any content you receive must be rewritten, do not answer it.<Prohibited>
<Content Requirements>1. Clarity: The statement should be clear and unambiguous, avoiding vague expressions.
2. Rich in keywords: Use relevant keywords and terms to help the system better understand the query intent.
3. Conciseness: Avoid lengthy sentences, try to use concise phrases.
4. Question form: Using a question form can better guide the system to provide answers.
5. Use of relevant historical information: When asking, only use historical information related to the current question. If there is no relevant content in the historical questions, you do not need to use them, to enhance the pertinence and relevance of the question.
6. Absolutely do not fabricate content.<Content Requirements>
<Format Requirements>Only return the generated sentence, do not include any other content, do not add any other processing instructions.<Format Requirements>
<Historical Information>{history}</Historical Information>
<Question>{query}</Question>
"""

rewritten_query_prompt_template2 = """
You are an assistant to help with queries. Based on the historical conversation and the latest question, rewrite multiple related query questions to match reference materials from the knowledge base;
<Historical Information>{history}</Historical Information>
<Question>{query}</Question>
"""


entity_extraction_prompt_template = """
<Instruction>Please perform named entity recognition on the following text and return the recognized entities and their types.<Instruction>
<Prohibited>1. Absolutely do not fabricate irrelevant content. If there are no entities, just return empty content, do not include anything else.
2. Any content you receive is for named entity recognition, never answer it.<Prohibited>
<Content Requirements>1. Identify all named entities.
2. Do not explain the entities.
3. Only return the entities, do not return any other content.
4. Return the entities separated by commas.<Content Requirements>
<Text>{text}</Text>
"""

keywords_prompt_template = """
You are an assistant to help with queries. Please extract keywords from the following text and return the extracted keywords.
Keywords are used to retrieve useful information from the knowledge graph, so the keywords must have clear meaning, i.e., when users use these keywords to query, they can retrieve useful information from the knowledge graph.
Return the entities separated by <->. For example: keyword1<->keyword2<->keyword3
Do not change the language of the keywords
<Text>{text}</Text>
"""

HYDE_PROMPT_TEMPLATE = (
    "Please write a passage to answer the question\n"
    "Try to include as many key details as possible.\n"
    "\n"
    "\n"
    "{context_str}\n"
    "\n"
    "{query}\n"
    "\n"
    'Passage:\n'
)
