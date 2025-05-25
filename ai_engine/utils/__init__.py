import time
import random
import os
from ai_engine.utils.logging import logger

def is_text_pdf(pdf_path):
    import fitz
    doc = fitz.open(pdf_path)
    total_pages = len(doc)
    if total_pages == 0:
        return False
        
    text_pages = 0
    for page_num in range(total_pages):
        page = doc.load_page(page_num)
        text = page.get_text()
        if text.strip():  
            text_pages += 1
    
    text_ratio = text_pages / total_pages
    return text_ratio > 0.5

def hashstr(input_string, length=8, with_salt=False):
    import hashlib
    # Add timestamp as noise
    if with_salt:
        input_string += str(time.time() + random.random())

    hash = hashlib.md5(str(input_string).encode()).hexdigest()
    return hash[:length]


def get_docker_safe_url(base_url):
    if os.getenv("RUNNING_IN_DOCKER") == "true":
       # Replace all possible local address forms
        base_url = base_url.replace("http://localhost", "http://host.docker.internal")
        base_url = base_url.replace("http://127.0.0.1", "http://host.docker.internal")
        logger.info(f"Running in docker, using {base_url} as base url")
    return base_url