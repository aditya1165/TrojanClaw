import os
from functools import lru_cache
from typing import Optional

from dotenv import load_dotenv
from supabase import Client, create_client

load_dotenv()


class SupabaseConfigError(RuntimeError):
    """Raised when required Supabase configuration is missing."""


@lru_cache(maxsize=1)
def get_supabase_client() -> Client:
    """
    Return a cached Supabase client instance.

    Required environment variables:
    - SUPABASE_URL
    - SUPABASE_KEY
    """
    url: Optional[str] = os.getenv("SUPABASE_URL")
    key: Optional[str] = os.getenv("SUPABASE_KEY")

    if not url or not key:
        raise SupabaseConfigError(
            "Missing SUPABASE_URL or SUPABASE_KEY. "
            "Set them in your environment (or .env file) before using Supabase."
        )

    return create_client(url, key)
