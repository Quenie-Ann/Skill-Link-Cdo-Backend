# skilllink/storage.py
import os
import uuid
import mimetypes
import requests


SUPABASE_URL      = os.environ.get('SUPABASE_URL', '')        # e.g. https://xxxx.supabase.co
SUPABASE_KEY      = os.environ.get('SUPABASE_SERVICE_KEY', '') # service_role key (not anon)
SUPABASE_BUCKET   = os.environ.get('SUPABASE_BUCKET', 'skilllink-documents')


def upload_to_supabase(file, folder: str, original_filename: str) -> str:
    """
    Uploads a file-like object to Supabase Storage.

    Args:
        file:              Django InMemoryUploadedFile or similar
        folder:            Subfolder inside the bucket, e.g. 'workers' or 'residents'
        original_filename: The user's original file name, used to derive extension

    Returns:
        Public URL string of the uploaded file.

    Raises:
        Exception if upload fails.
    """
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise Exception(
            'Supabase is not configured. '
            'Set SUPABASE_URL and SUPABASE_SERVICE_KEY environment variables.'
        )

    # Build a unique storage path so files never collide
    ext          = original_filename.rsplit('.', 1)[-1].lower() if '.' in original_filename else 'bin'
    unique_name  = f'{uuid.uuid4().hex}.{ext}'
    storage_path = f'{folder}/{unique_name}'

    content_type = mimetypes.guess_type(original_filename)[0] or 'application/octet-stream'

    upload_url = (
        f'{SUPABASE_URL}/storage/v1/object/{SUPABASE_BUCKET}/{storage_path}'
    )

    response = requests.post(
        upload_url,
        headers={
            'Authorization': f'Bearer {SUPABASE_KEY}',
            'Content-Type':  content_type,
            'x-upsert':      'false',   # fail if path already exists (UUID makes this safe)
        },
        data=file.read(),
        timeout=30,
    )

    if response.status_code not in (200, 201):
        raise Exception(
            f'Supabase upload failed [{response.status_code}]: {response.text}'
        )

    # Build the public URL — bucket must have public access enabled in Supabase dashboard
    public_url = (
        f'{SUPABASE_URL}/storage/v1/object/public/{SUPABASE_BUCKET}/{storage_path}'
    )
    return public_url