import json
import os
import re
from pathlib import Path
from typing import Any

import httpx
import openai
import psycopg2
from psycopg2.extras import Json
from dotenv import load_dotenv

from app.scraper.chunker import chunk_text, clean_html
from app.scraper.db_schema import ensure_documents_schema

try:
    from piazza_api import Piazza
except Exception:
    Piazza = None

ENV_PATH = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=ENV_PATH)


def _openai_client() -> openai.OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY is required for Piazza ingestion.")
    return openai.OpenAI(api_key=api_key)


def _embed_text(client: openai.OpenAI, text: str, model: str = "text-embedding-3-small") -> list[float]:
    response = client.embeddings.create(input=text, model=model)
    return response.data[0].embedding


def _collect_export_json_files(export_dir: Path) -> list[Path]:
    if not export_dir.exists() or not export_dir.is_dir():
        return []
    return sorted([p for p in export_dir.rglob("*.json") if p.is_file()])


def _extract_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, list):
        return "\n".join(_extract_text(item) for item in value if _extract_text(item))
    if isinstance(value, dict):
        pieces: list[str] = []
        for key in ["subject", "title", "content", "text", "body", "question"]:
            if key in value:
                chunk = _extract_text(value[key])
                if chunk:
                    pieces.append(chunk)
        for key in ["history", "followups", "replies", "children", "notes"]:
            if key in value and isinstance(value[key], list):
                for child in value[key]:
                    chunk = _extract_text(child)
                    if chunk:
                        pieces.append(chunk)
        return "\n".join(pieces)
    return str(value).strip()


def _parse_piazza_posts_from_json(file_path: Path) -> list[dict[str, str]]:
    try:
        payload = json.loads(file_path.read_text(encoding="utf-8", errors="ignore"))
    except Exception:
        return []

    if isinstance(payload, dict):
        if isinstance(payload.get("posts"), list):
            rows = payload["posts"]
        elif isinstance(payload.get("results"), list):
            rows = payload["results"]
        else:
            rows = [payload]
    elif isinstance(payload, list):
        rows = payload
    else:
        return []

    parsed: list[dict[str, str]] = []
    for row in rows:
        if not isinstance(row, dict):
            continue

        post_id = str(
            row.get("id")
            or row.get("post_id")
            or row.get("nr")
            or row.get("uid")
            or ""
        ).strip()
        title = _extract_text(row.get("subject") or row.get("title") or row.get("question"))
        body = _extract_text(row)
        content = "\n\n".join(piece for piece in [title, body] if piece).strip()
        if not content:
            continue

        source_url = str(row.get("url") or "").strip()
        if not source_url and post_id:
            source_url = f"piazza://post/{post_id}"
        elif not source_url:
            source_url = f"piazza://file/{file_path.name}"

        parsed.append(
            {
                "post_id": post_id or file_path.stem,
                "title": title or f"Piazza Post {post_id or file_path.stem}",
                "content": content,
                "source_url": source_url,
                "raw_payload": row,
            }
        )

    return parsed


def _scrape_thread_urls(course_id: str | None) -> list[dict[str, str]]:
    raw_urls = os.getenv("PIAZZA_THREAD_URLS", "").strip()
    piazza_cookie = os.getenv("PIAZZA_COOKIE", "").strip()
    if not raw_urls:
        return []

    headers = {
        "User-Agent": "Mozilla/5.0",
    }
    if piazza_cookie:
        headers["Cookie"] = piazza_cookie

    urls = [u.strip() for u in raw_urls.split(",") if u.strip()]
    output: list[dict[str, str]] = []
    for url in urls:
        try:
            response = httpx.get(url, headers=headers, follow_redirects=True, timeout=20.0)
            response.raise_for_status()
            text = clean_html(response.text)
            text = re.sub(r"\s+", " ", text).strip()
            if not text:
                continue

            title = f"Piazza Thread ({course_id or 'course'})"
            output.append(
                {
                    "post_id": re.sub(r"\W+", "-", url).strip("-")[:60] or "thread",
                    "title": title,
                    "content": text,
                    "source_url": url,
                    "raw_payload": {"url": url, "scraped": True},
                }
            )
        except Exception as exc:
            print(f"[piazza] failed to scrape {url}: {exc}")

    return output


def _normalize_course_id(course_id: str | None) -> str:
    if not course_id:
        return os.getenv("DEFAULT_COURSE_ID", "USC-COURSE").strip() or "USC-COURSE"
    return course_id.strip() or "USC-COURSE"


def _resolve_piazza_network_id(course_id: str) -> str:
    """
    Resolve Piazza network ID from env.
    Priority:
    1) PIAZZA_NETWORK_MAP (JSON object of course_id -> network_id)
    2) PIAZZA_NETWORK_ID (single fallback network)
    """
    raw_map = os.getenv("PIAZZA_NETWORK_MAP", "").strip()
    if raw_map:
        try:
            parsed = json.loads(raw_map)
            if isinstance(parsed, dict):
                mapped = parsed.get(course_id)
                if mapped:
                    return str(mapped).strip()
        except Exception:
            pass

    fallback = os.getenv("PIAZZA_NETWORK_ID", "").strip()
    return fallback


def _fetch_posts_via_piazza_api(course_id: str, max_posts: int) -> list[dict[str, str]]:
    """
    Fetch Piazza posts directly using piazza-api package.
    Requires: PIAZZA_EMAIL, PIAZZA_PASSWORD, and a resolvable network id.
    """
    if Piazza is None:
        return []

    email = os.getenv("PIAZZA_EMAIL", "").strip()
    password = os.getenv("PIAZZA_PASSWORD", "").strip()
    network_id = _resolve_piazza_network_id(course_id)
    if not email or not password or not network_id:
        return []

    try:
        client = Piazza()
        client.user_login(email=email, password=password)
        network = client.network(network_id)
    except Exception as exc:
        print(f"[piazza-api] login/network failed for course={course_id}: {exc}")
        return []

    posts: list[dict[str, str]] = []
    try:
        for idx, post in enumerate(network.iter_all_posts(limit=50)):
            if idx >= max_posts:
                break

            if not isinstance(post, dict):
                continue

            post_id = str(post.get("id") or post.get("nr") or post.get("uid") or "").strip()

            history = post.get("history") if isinstance(post.get("history"), list) else []
            latest_history = history[-1] if history and isinstance(history[-1], dict) else {}

            title = _extract_text(
                post.get("subject")
                or latest_history.get("subject")
                or post.get("title")
                or post.get("question")
            )
            body = _extract_text(post)
            content = "\n\n".join(piece for piece in [title, body] if piece).strip()
            if not content:
                continue

            if post_id:
                source_url = f"https://piazza.com/class/{network_id}?cid={post_id}"
            else:
                source_url = f"piazza://network/{network_id}"

            posts.append(
                {
                    "post_id": post_id or f"row-{idx}",
                    "title": title or f"Piazza Post {post_id or idx}",
                    "content": content,
                    "source_url": source_url,
                    "raw_payload": post,
                }
            )
    except Exception as exc:
        print(f"[piazza-api] fetching posts failed for course={course_id}: {exc}")
        return []

    return posts


def _dedupe_posts(posts: list[dict[str, str]]) -> list[dict[str, str]]:
    seen: set[tuple[str, str]] = set()
    output: list[dict[str, str]] = []
    for post in posts:
        key = (post.get("source_url", ""), post.get("title", ""))
        if key in seen:
            continue
        seen.add(key)
        output.append(post)
    return output


def _ensure_piazza_data_table(cur) -> None:
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS piazza_data (
            id BIGSERIAL PRIMARY KEY,
            course_id TEXT NOT NULL,
            post_id TEXT,
            title TEXT,
            source_url TEXT,
            content_text TEXT NOT NULL,
            raw_payload JSONB,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
        """
    )
    cur.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_piazza_data_course_id ON piazza_data(course_id)
        """
    )
    cur.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_piazza_data_post_id ON piazza_data(post_id)
        """
    )


def _store_raw_posts(cur, course_id: str, posts: list[dict[str, Any]]) -> None:
    cur.execute(
        """
        DELETE FROM piazza_data
        WHERE course_id = %s
        """,
        (course_id,),
    )

    for post in posts:
        cur.execute(
            """
            INSERT INTO piazza_data (
                course_id,
                post_id,
                title,
                source_url,
                content_text,
                raw_payload,
                updated_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, NOW())
            """,
            (
                course_id,
                post.get("post_id"),
                post.get("title"),
                post.get("source_url"),
                post.get("content") or "",
                Json(post.get("raw_payload") or {}),
            ),
        )


def _fetch_piazza_documents(course_id: str | None) -> list[dict[str, str]]:
    normalized_course = _normalize_course_id(course_id)
    export_dir = Path(os.getenv("PIAZZA_EXPORT_DIR", str(Path(__file__).resolve().parents[2] / "data" / "piazza")))

    # Primary path: piazza-api direct fetch.
    posts: list[dict[str, str]] = _fetch_posts_via_piazza_api(normalized_course, max_posts=400)

    # Fallback paths: local JSON exports and optional raw thread scraping.
    for json_file in _collect_export_json_files(export_dir):
        posts.extend(_parse_piazza_posts_from_json(json_file))

    posts.extend(_scrape_thread_urls(normalized_course))
    return _dedupe_posts(posts)


def sync_piazza_course_documents(course_id: str | None, max_posts: int = 200) -> int:
    """
    Ingest Piazza course context into documents table as data_type='piazza_course'.
    Stores course identifier in the 'campus' column for retrieval filtering.
    """
    supabase_url = os.getenv("SUPABASE_URL", "")
    if not supabase_url.startswith("postgres"):
        raise ValueError("SUPABASE_URL must be a postgres connection string.")

    normalized_course = _normalize_course_id(course_id)
    conn = psycopg2.connect(supabase_url)
    cur = conn.cursor()
    ensure_documents_schema(cur)
    conn.commit()
    _ensure_piazza_data_table(cur)
    conn.commit()

    posts = _fetch_piazza_documents(normalized_course)
    if not posts:
        cur.close()
        conn.close()
        return 0

    client = _openai_client()

    inserted = 0
    try:
        _store_raw_posts(cur, normalized_course, posts)

        # Replace prior Piazza chunks for this course to avoid uncontrolled duplication.
        cur.execute(
            """
            DELETE FROM documents
            WHERE data_type = %s AND campus = %s
            """,
            ("piazza_course", normalized_course),
        )
        conn.commit()

        for post in posts[:max_posts]:
            metadata = {
                "url": post["source_url"],
                "page_title": post["title"],
                "data_type": "piazza_course",
                "campus": normalized_course,
            }
            chunks = chunk_text(post["content"], metadata=metadata, chunk_size=320, overlap=40)
            for chunk in chunks:
                embedding = _embed_text(client, chunk["chunk_text"])
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
                        chunk["source_url"],
                        chunk["page_title"],
                        chunk["data_type"],
                        chunk["campus"],
                        chunk["chunk_text"],
                        vec_str,
                        chunk.get("chunk_index", 0),
                    ),
                )
                inserted += 1

        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()

    return inserted
