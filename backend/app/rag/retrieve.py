import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

STOPWORDS = {
    "the", "and", "for", "with", "that", "this", "from", "into", "about",
    "what", "where", "when", "which", "how", "can", "should", "would", "could",
    "i", "we", "you", "our", "your", "are", "is", "to", "of", "in", "on", "at",
}


def _infer_data_types(query_text: str) -> list[str]:
    q = query_text.lower()
    inferred: set[str] = set()

    if any(k in q for k in ["exam", "schedule", "calendar", "registration", "course", "class"]):
        inferred.add("schedule")
    if any(k in q for k in ["orientation", "new student", "first year", "onboarding"]):
        inferred.add("orientation")
    if any(k in q for k in ["map", "building", "where is", "location", "directions"]):
        inferred.add("map")
    if any(k in q for k in ["library", "study room", "leavey", "book a room"]):
        inferred.add("library")
    if any(k in q for k in ["service", "resource", "office", "support", "international", "graduate", "grad"]):
        inferred.add("services")
    if any(k in q for k in ["health", "appointment", "engemann", "clinic", "medical"]):
        inferred.add("health")
    if any(k in q for k in ["housing", "dorm", "residence", "apartment"]):
        inferred.add("housing")

    return list(inferred)


def _keyword_terms(query_text: str) -> list[str]:
    terms = re.findall(r"[a-zA-Z]{4,}", query_text.lower())
    return [t for t in terms if t not in STOPWORDS]


def _search_candidates(cur, vec_str: str, inferred_types: list[str], limit: int):
    base_sql = (
        """
        SELECT chunk_text, source_url, page_title, data_type, campus,
               (embedding <=> %s::vector) AS distance
        FROM documents
        """
    )

    if inferred_types:
        cur.execute(
            base_sql +
            """
            WHERE data_type = ANY(%s)
            ORDER BY distance
            LIMIT %s
            """,
            (vec_str, inferred_types, limit),
        )
        rows = cur.fetchall()
        if len(rows) >= max(6, limit // 3):
            return rows

    cur.execute(
        base_sql +
        """
        ORDER BY distance
        LIMIT %s
        """,
        (vec_str, limit),
    )
    return cur.fetchall()


def retrieve_context(query_embedding: list[float], query_text: str = "", top_k: int = 5) -> list[dict]:
    """
    Searches the docs table for the closest matching chunks using pgvector.
    Uses the SUPABASE_URL connection string locally configured.
    """
    supabase_url = os.getenv("SUPABASE_URL", "")
    if not supabase_url.startswith("postgres"):
        raise ValueError("SUPABASE_URL must be a postgres connection string.")
        
    vec_str = "[" + ",".join(map(str, query_embedding)) + "]"
    inferred_types = _infer_data_types(query_text)
    terms = _keyword_terms(query_text)
    
    conn = psycopg2.connect(supabase_url)
    cur = conn.cursor()
    
    try:
        candidate_rows = _search_candidates(cur, vec_str, inferred_types, limit=max(20, top_k * 8))

        reranked = []
        for row in candidate_rows:
            chunk_text, source_url, page_title, data_type, campus, distance = row
            title_l = (page_title or "").lower()
            body_l = (chunk_text or "").lower()

            title_hits = sum(1 for t in terms if t in title_l)
            body_hits = sum(1 for t in terms if t in body_l)
            type_bonus = 0.2 if data_type in inferred_types else 0.0

            score = (-float(distance)) + (0.12 * title_hits) + (0.03 * body_hits) + type_bonus

            reranked.append({
                "chunk_text": chunk_text,
                "source_url": source_url,
                "page_title": page_title,
                "data_type": data_type,
                "campus": campus,
                "_score": score,
            })

        reranked.sort(key=lambda item: item["_score"], reverse=True)

        # Keep variety so one source does not dominate the context window.
        per_source_count: dict[str, int] = {}
        results = []
        for item in reranked:
            source = item.get("source_url") or "unknown"
            if per_source_count.get(source, 0) >= 2:
                continue

            per_source_count[source] = per_source_count.get(source, 0) + 1
            item.pop("_score", None)
            results.append(item)

            if len(results) >= top_k:
                break

        return results
    except Exception as e:
        print("Error during retrieval:", e)
        return []
    finally:
        cur.close()
        conn.close()
