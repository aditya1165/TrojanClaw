import os
import re
import psycopg2
from pathlib import Path
from dotenv import load_dotenv
import re

ENV_PATH = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=ENV_PATH)

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
    # Using 'dealin' captures common typos like dealines or deadline
    if any(k in q for k in ["deadline", "dealin", "due", "assignment", "homework", "project", "midterm", "final", "test", "exam"]):
        inferred.add("deadline")

    return list(inferred)


def _is_course_query(query_text: str) -> bool:
    q = query_text.lower()
    course_terms = [
        "course",
        "class",
        "piazza",
        "syllabus",
        "assignment",
        "homework",
        "midterm",
        "final",
        "lecture",
        "ta",
        "professor",
        "office hour",
    ]
    return any(term in q for term in course_terms)


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


def _search_piazza_candidates(cur, vec_str: str, course_id: str | None, limit: int):
    if course_id:
        cur.execute(
            """
            SELECT chunk_text, source_url, page_title, data_type, campus,
                   (embedding <=> %s::vector) AS distance
            FROM documents
            WHERE data_type = 'piazza_course' AND campus = %s
            ORDER BY distance
            LIMIT %s
            """,
            (vec_str, course_id, limit),
        )
    else:
        cur.execute(
            """
            SELECT chunk_text, source_url, page_title, data_type, campus,
                   (embedding <=> %s::vector) AS distance
            FROM documents
            WHERE data_type = 'piazza_course'
            ORDER BY distance
            LIMIT %s
            """,
            (vec_str, limit),
        )
    return cur.fetchall()


def _search_piazza_raw_fallback(cur, query_text: str, course_id: str | None, limit: int):
    terms = _keyword_terms(query_text)[:6]
    if not terms:
        return []

    patterns = [f"%{term}%" for term in terms]
    if course_id:
        cur.execute(
            """
            SELECT
                content_text AS chunk_text,
                COALESCE(source_url, 'piazza://unknown') AS source_url,
                COALESCE(title, 'Piazza Post') AS page_title,
                'piazza_course' AS data_type,
                course_id AS campus,
                0.70::float AS distance
            FROM piazza_data
            WHERE course_id = %s
              AND (
                content_text ILIKE ANY(%s)
                OR title ILIKE ANY(%s)
              )
            ORDER BY updated_at DESC
            LIMIT %s
            """,
            (course_id, patterns, patterns, limit),
        )
    else:
        cur.execute(
            """
            SELECT
                content_text AS chunk_text,
                COALESCE(source_url, 'piazza://unknown') AS source_url,
                COALESCE(title, 'Piazza Post') AS page_title,
                'piazza_course' AS data_type,
                course_id AS campus,
                0.75::float AS distance
            FROM piazza_data
            WHERE (
                content_text ILIKE ANY(%s)
                OR title ILIKE ANY(%s)
            )
            ORDER BY updated_at DESC
            LIMIT %s
            """,
            (patterns, patterns, limit),
        )

    return cur.fetchall()


def retrieve_context(
    query_embedding: list[float],
    query_text: str = "",
    top_k: int = 5,
    user_context: dict | None = None,
) -> list[dict]:
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
    context = user_context or {}
    course_id = str(context.get("course_id") or "").strip() or None
    course_query = _is_course_query(query_text)
    
    conn = psycopg2.connect(supabase_url)
    cur = conn.cursor()
    
    try:
        candidate_rows = []
        if course_query:
            candidate_rows.extend(_search_piazza_candidates(cur, vec_str, course_id, limit=max(20, top_k * 8)))
            # If vector-matched Piazza rows are sparse, fallback to raw-table text match.
            if len(candidate_rows) < top_k:
                candidate_rows.extend(_search_piazza_raw_fallback(cur, query_text, course_id, limit=max(8, top_k * 3)))

        general_candidates = _search_candidates(cur, vec_str, inferred_types, limit=max(20, top_k * 8))
        candidate_rows.extend(general_candidates)

        reranked = []
        for row in candidate_rows:
            chunk_text, source_url, page_title, data_type, campus, distance = row
            title_l = (page_title or "").lower()
            body_l = (chunk_text or "").lower()

            title_hits = sum(1 for t in terms if t in title_l)
            body_hits = sum(1 for t in terms if t in body_l)
            type_bonus = 0.2 if data_type in inferred_types else 0.0
            piazza_bonus = 0.3 if course_query and data_type == "piazza_course" else 0.0
            course_bonus = 0.15 if course_id and campus == course_id else 0.0

            score = (
                (-float(distance))
                + (0.12 * title_hits)
                + (0.03 * body_hits)
                + type_bonus
                + piazza_bonus
                + course_bonus
            )

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
            data_type = item.get("data_type")
            
            # Deadlines should not be arbitrarily limited, let them all through!
            if data_type != "deadline":
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
