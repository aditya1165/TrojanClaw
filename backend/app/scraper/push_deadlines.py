import os
import openai
import psycopg2
from dotenv import load_dotenv

# Ensure we can import from app
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

load_dotenv()

# =========================================================================
# MANUAL DATA ENTRY
# Add, modify, or remove deadlines here. When you run this script,
# they will be directly embedded and pushed into the AI Agent's RAG brain!
# =========================================================================
MANUAL_DEADLINES = [
    {
        "course": "DSCI 552", 
        "deadline": "April 10th, 2026 at 11:59PM", 
        "title": "Machine Learning for Data Science - HW4",
        "description": "Implement K-Means Clustering and PCA from scratch. Submit code to Vocareum and written report to Gradescope."
    },
    {
        "course": "DSCI 552", 
        "deadline": "April 24th, 2026", 
        "title": "Final Project Report",
        "description": "Final Kaggle competition submission and 10-page IEEE formatted report on model architectures."
    },
    {
        "course": "CSCI 544", 
        "deadline": "April 12th, 2026", 
        "title": "Applied NLP - HW3",
        "description": "Build an HMM-based Part-of-Speech Tagger and evaluate on the provided test corpus."
    },
    {
        "course": "CSCI 544", 
        "deadline": "May 2nd, 2026", 
        "title": "Final Project Presentation",
        "description": "Video presentation of your neural machine translation system."
    }
]

def get_openai_embedding(text: str, model="text-embedding-3-small") -> list[float]:
    """Generates an embedding vector for the text using OpenAI."""
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = client.embeddings.create(
        input=text,
        model=model
    )
    return response.data[0].embedding

def push_manual_deadlines_to_db():
    if not os.getenv("OPENAI_API_KEY"):
        raise ValueError("OPENAI_API_KEY is not set.")
    
    supabase_url = os.getenv("SUPABASE_URL", "")
    if not supabase_url.startswith("postgres"):
        raise ValueError("SUPABASE_URL must be a postgres connection string.")
        
    print("Connecting to Postgres database...")
    conn = psycopg2.connect(supabase_url)
    cur = conn.cursor()

    total_inserted = 0

    print("Pushing Manual Deadlines to TrojanAI RAG Database...")
    
    for idx, item in enumerate(MANUAL_DEADLINES):
        # Format the text so the AI can easily read it when retrieved
        chunk_text = (
            f"DEADLINE ALERT: {item['title']}\n"
            f"Course: {item['course']}\n"
            f"Due Date: {item['deadline']}\n"
            f"Details: {item['description']}"
        )
        
        print(f"\nProcessing Deadline: {item['title']}...")
        
        try:
            # Generate embedding
            embedding = get_openai_embedding(chunk_text)
            
            # Upsert to Supabase
            vec_str = "[" + ",".join(map(str, embedding)) + "]"
            
            cur.execute(
                """
                INSERT INTO documents (source_url, page_title, data_type, campus, chunk_text, embedding)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    "manual-entry", 
                    f"Deadline: {item['title']}", 
                    "deadline", 
                    "USC", 
                    chunk_text, 
                    vec_str
                )
            )
            conn.commit()
            total_inserted += 1
            print(f"  -> Successfully injected into RAG DB!")
        except Exception as e:
            print(f"  -> Error inserting deadline: {e}")
            conn.rollback()
                
    cur.close()
    conn.close()
    print(f"\nPipeline finished. Total deadlines inserted: {total_inserted}")

if __name__ == "__main__":
    push_manual_deadlines_to_db()
