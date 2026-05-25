# skilllink/storage.py

import os
from supabase import create_client

SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_SERVICE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')

_client = None

def get_supabase_client():
    global _client
    if _client is None:
        _client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
    return _client


def generate_signed_url(bucket: str, path: str, expires_in: int = 900) -> str:
    """
    Generate a time-limited signed URL for a private bucket object.
    expires_in: seconds until expiry (default 900 = 15 minutes, per SRS Section 2.1).
    """
    client = get_supabase_client()
    response = client.storage.from_(bucket).create_signed_url(path, expires_in)
    return response['signedURL']


def upload_document(bucket: str, path: str, file_bytes: bytes, content_type: str) -> str:
    """
    Upload a file to a Supabase Storage bucket.
    Returns the storage path for saving in the Document model.
    """
    client = get_supabase_client()
    client.storage.from_(bucket).upload(
        path,
        file_bytes,
        file_options={"content-type": content_type, "upsert": "false"},
    )
    return path