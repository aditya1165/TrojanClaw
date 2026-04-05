import httpx
from bs4 import BeautifulSoup
import re

def fetch_html(url: str) -> str:
    """
    Fetches the raw HTML content from a URL.
    Uses a standard user-agent to avoid basic blocks.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }
    try:
        response = httpx.get(url, headers=headers, follow_redirects=True, timeout=15.0)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return ""

def clean_html(html_content: str) -> str:
    """
    Strips out <script>, <style>, and extracts visible text.
    Replaces multiple whitespace chars with a single space.
    """
    if not html_content:
        return ""
        
    soup = BeautifulSoup(html_content, "html.parser")
    
    # Remove script and style elements
    for script_or_style in soup(["script", "style", "noscript", "header", "footer", "nav"]):
        script_or_style.extract()
        
    # Get text
    text = soup.get_text(separator=" ", strip=True)
    
    # Collapse multiple spaces and newlines
    clean_text = re.sub(r'\s+', ' ', text)
    return clean_text.strip()

def chunk_text(text: str, metadata: dict, chunk_size: int = 400, overlap: int = 50) -> list[dict]:
    """
    Splits the text into chunks of approx `chunk_size` words, 
    with an overlap of `overlap` words.
    Prepends metadata to the chunk text so the embedding model gets context.
    Returns a list of dicts representing the document chunks.
    """
    if not text:
        return []
        
    words = text.split()
    chunks = []
    
    # Prepend metadata string to be embedded alongside the raw text
    source_url = metadata.get("url", "")
    page_title = metadata.get("page_title", "")
    data_type = metadata.get("data_type", "")
    campus = metadata.get("campus", "")
    
    meta_header = f"[Source: {source_url}]\n[Title: {page_title}]\n[Type: {data_type}]\n[Campus: {campus}]\n---\n"
    
    step = max(1, chunk_size - overlap)
    
    chunk_index = 0
    for i in range(0, len(words), step):
        chunk_words = words[i:i + chunk_size]
        chunk_body = " ".join(chunk_words)
        
        full_chunk_text = meta_header + chunk_body
        
        chunks.append({
            "chunk_text": full_chunk_text,
            "source_url": source_url,
            "page_title": page_title,
            "data_type": data_type,
            "campus": campus,
            "chunk_index": chunk_index,
        })
        chunk_index += 1
        
        # If we reached the end of the text, construct final chunk and break
        if i + chunk_size >= len(words):
            break
            
    return chunks
