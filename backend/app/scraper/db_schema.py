import psycopg2


def ensure_documents_schema(cur: psycopg2.extensions.cursor) -> None:
    """
    Ensure the documents table and key indexes/columns exist.
    This aligns runtime ingestion writes with the expected RAG schema.
    """
    cur.execute(
        """
        CREATE EXTENSION IF NOT EXISTS vector
        """
    )

    cur.execute(
        """
        CREATE EXTENSION IF NOT EXISTS pgcrypto
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS documents (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            source_url TEXT NOT NULL,
            page_title TEXT,
            data_type TEXT,
            campus TEXT,
            chunk_text TEXT NOT NULL,
            embedding VECTOR(1536),
            chunk_index INT,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            last_scraped TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
        """
    )

    cur.execute(
        """
        ALTER TABLE documents
        ADD COLUMN IF NOT EXISTS chunk_index INT
        """
    )
    cur.execute(
        """
        ALTER TABLE documents
        ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        """
    )
    cur.execute(
        """
        ALTER TABLE documents
        ADD COLUMN IF NOT EXISTS last_scraped TIMESTAMPTZ NOT NULL DEFAULT NOW()
        """
    )

    # Remove legacy duplicates so unique index creation does not fail on existing datasets.
    cur.execute(
        """
        DELETE FROM documents d
        USING (
            SELECT ctid
            FROM (
                SELECT
                    ctid,
                    row_number() OVER (
                        PARTITION BY source_url, chunk_index
                        ORDER BY last_scraped DESC, created_at DESC
                    ) AS rn
                FROM documents
                WHERE chunk_index IS NOT NULL
            ) ranked
            WHERE rn > 1
        ) dupes
        WHERE d.ctid = dupes.ctid
        """
    )

    cur.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS docs_unique_source_chunk
        ON documents(source_url, chunk_index)
        """
    )
    cur.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_documents_source
        ON documents(source_url)
        """
    )
    cur.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_documents_data_type
        ON documents(data_type)
        """
    )
    cur.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_documents_campus
        ON documents(campus)
        """
    )

    # HNSW works well for online ingestion without heavy training requirements.
    cur.execute(
        """
        CREATE INDEX IF NOT EXISTS documents_embedding_idx
        ON documents
        USING hnsw (embedding vector_cosine_ops)
        """
    )
