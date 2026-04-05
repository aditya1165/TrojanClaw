import os
import openai
from dotenv import load_dotenv

# Ensure we can import from app
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from app.scraper.usc_pages import USC_PAGES
from app.scraper.chunker import fetch_html, clean_html, chunk_text
from app.scraper.piazza_ingest import sync_piazza_course_documents
from app.scraper.db_schema import ensure_documents_schema
import psycopg2

load_dotenv()

def get_openai_embedding(text: str, model="text-embedding-3-small") -> list[float]:
    """Generates an embedding vector for the text using OpenAI."""
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = client.embeddings.create(
        input=text,
        model=model
    )
    return response.data[0].embedding

def run_scraper_pipeline():
    # 1. Validate environment
    if not os.getenv("OPENAI_API_KEY"):
        raise ValueError("OPENAI_API_KEY is not set in environment or .env file.")
    
    supabase_url = os.getenv("SUPABASE_URL", "")
    if not supabase_url.startswith("postgres"):
        raise ValueError("SUPABASE_URL must be a postgres connection string.")
        
    print("Connecting to Postgres database...")
    conn = psycopg2.connect(supabase_url)
    cur = conn.cursor()

    ensure_documents_schema(cur)
    conn.commit()

    
    total_inserted = 0

    print("Starting TrojanAI scraper pipeline...")
    
    # 2. Iterate through each configured USC page
    for page in USC_PAGES:
        url = page["url"]
        print(f"\nProcessing {url} ...")
        
        # Fetch & Clean
        raw_html = fetch_html(url)
        if not raw_html:
            print(f"  -> Skipped (Failed to fetch HTML)")
            continue
            
        clean_txt = clean_html(raw_html)
        if not clean_txt:
            print(f"  -> Skipped (No text extracted)")
            continue
            
        # Chunk
        chunks = chunk_text(clean_txt, metadata=page, chunk_size=400, overlap=50)
        print(f"  -> Extracted {len(chunks)} chunks.")
        
        # 3. Embed & Insert
        for idx, chunk_data in enumerate(chunks):
            try:
                # Generate embedding
                embedding = get_openai_embedding(chunk_data["chunk_text"])
                chunk_data["embedding"] = embedding
                
                # Upsert to Supabase
                # Convert the float list to a string formatted as a Postgres array or pgvector literal
                vec_str = "[" + ",".join(map(str, embedding)) + "]"
                
                cur.execute(
                    """
                    INSERT INTO documents (
                        source_url,
                        page_title,
                        data_type,
                        campus,
                        chunk_text,
                        embedding,
                        chunk_index,
                        last_scraped
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
                    ON CONFLICT (source_url, chunk_index)
                    DO UPDATE SET
                        page_title = EXCLUDED.page_title,
                        data_type = EXCLUDED.data_type,
                        campus = EXCLUDED.campus,
                        chunk_text = EXCLUDED.chunk_text,
                        embedding = EXCLUDED.embedding,
                        last_scraped = NOW()
                    """,
                    (
                        chunk_data["source_url"],
                        chunk_data["page_title"],
                        chunk_data["data_type"],
                        chunk_data["campus"],
                        chunk_data["chunk_text"],
                        vec_str,
                        chunk_data.get("chunk_index", idx),
                    )
                )
                conn.commit()
                total_inserted += 1
                print(f"    - Inserted chunk {idx+1}/{len(chunks)}")
            except Exception as e:
                print(f"    - Error inserting chunk {idx+1}: {e}")
                conn.rollback()
                
    cur.close()
    conn.close()

    # 4. Optional Piazza ingestion
    include_piazza = os.getenv("INGEST_PIAZZA", "false").lower() in {"1", "true", "yes"}
    piazza_course = os.getenv("DEFAULT_COURSE_ID", "").strip() or None
    if include_piazza:
        try:
            piazza_inserted = sync_piazza_course_documents(course_id=piazza_course, max_posts=250)
            print(f"Piazza ingestion complete. Inserted chunks: {piazza_inserted}")
            total_inserted += piazza_inserted
        except Exception as exc:
            print(f"Piazza ingestion failed: {exc}")

    print(f"\nPipeline finished. Total chunks inserted: {total_inserted}")

if __name__ == "__main__":
    run_scraper_pipeline()
