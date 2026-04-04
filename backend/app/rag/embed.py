import os
import openai
from dotenv import load_dotenv

load_dotenv()

def get_query_embedding(query: str, model: str = "text-embedding-3-small") -> list[float]:
    """Generates an embedding vector for the user query."""
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = client.embeddings.create(
        input=query,
        model=model
    )
    return response.data[0].embedding
