import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def retrieve_context(query_embedding: list[float], top_k: int = 5) -> list[dict]:
    """
    Searches the docs table for the closest matching chunks using pgvector.
    Uses the SUPABASE_URL connection string locally configured.
    """
    supabase_url = os.getenv("SUPABASE_URL", "")
    if not supabase_url.startswith("postgres"):
        raise ValueError("SUPABASE_URL must be a postgres connection string.")
        
    vec_str = "[" + ",".join(map(str, query_embedding)) + "]"
    
    conn = psycopg2.connect(supabase_url)
    cur = conn.cursor()
    
    try:
        # Distance operator <=> is cosine distance in pgvector
        cur.execute(
            """
            SELECT chunk_text, source_url, page_title, data_type, campus
            FROM documents
            ORDER BY embedding <=> %s::vector
            LIMIT %s

            """,
            (vec_str, top_k)
        )
        
        rows = cur.fetchall()
        results = []
        for row in rows:
            results.append({
                "chunk_text": row[0],
                "source_url": row[1],
                "page_title": row[2],
                "data_type": row[3],
                "campus": row[4]
            })
        return results
    except Exception as e:
        print("Error during retrieval:", e)
        return []
    finally:
        cur.close()
        conn.close()
