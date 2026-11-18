"""Supabase Storage helper functions."""
from typing import Optional
from supabase import Client, create_client
from app.config import settings

_client: Optional[Client] = None

def get_supabase_client() -> Client:
    global _client
    if _client is None:
        if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_ROLE_KEY:
            raise RuntimeError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be configured in backend/.env")
        _client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)
    return _client

def ensure_bucket(bucket_name: Optional[str] = None) -> None:
    """Ensure the private bucket exists, create it if not."""
    b_name = bucket_name or settings.STORAGE_BUCKET
    client = get_supabase_client()
    try:
        buckets = client.storage.list_buckets()
        existing_names = [b.name for b in buckets] if buckets else []
        if b_name not in existing_names:
            client.storage.create_bucket(b_name, options={"public": False})
    except Exception as e:
        # If bucket already exists or cannot be created, raise or verify
        raise RuntimeError(f"Failed to ensure storage bucket '{b_name}': {e}") from e

def upload(path: str, data: bytes, content_type: str) -> None:
    """Upload binary data to the storage bucket."""
    client = get_supabase_client()
    client.storage.from_(settings.STORAGE_BUCKET).upload(
        path=path,
        file=data,
        file_options={"content-type": content_type, "upsert": "true"}
    )

def download(path: str) -> bytes:
    """Download binary data from the storage bucket."""
    client = get_supabase_client()
    return client.storage.from_(settings.STORAGE_BUCKET).download(path)

def signed_url(path: str, expires_seconds: int = 600) -> str:
    """Generate a signed download URL valid for expires_seconds."""
    client = get_supabase_client()
    res = client.storage.from_(settings.STORAGE_BUCKET).create_signed_url(path, expires_seconds)
    if isinstance(res, dict):
        return res.get("signedURL") or res.get("signed_url") or ""
    return str(res)

def delete(paths: list[str]) -> None:
    """Delete multiple paths from the storage bucket."""
    if not paths:
        return
    client = get_supabase_client()
    client.storage.from_(settings.STORAGE_BUCKET).remove(paths)

