# requests_api/ml_client.py
#
# Django-side HTTP client for the FastAPI ML service.
# Updated payload to include:
#   - job_type_name  (replaces free-text description as primary text signal)
#   - years_experience per candidate (new scoring signal)

from __future__ import annotations

import logging
import os
from typing import Any

import requests

logger = logging.getLogger(__name__)

ML_SERVICE_URL = os.getenv('ML_SERVICE_URL', 'http://localhost:8001')
SERVICE_API_KEY = os.getenv('SERVICE_API_KEY', '')
ML_TIMEOUT_SECONDS = 10


class MLServiceUnavailable(Exception):
    pass


def _build_payload(job_request, candidates) -> dict[str, Any]:
    """
    Build the POST /match/ payload from a JobRequest instance and a
    pre-filtered WorkerProfile queryset.

    job_type_name is the primary text signal — it is the admin-defined
    label selected by the resident (e.g. 'Fix leaking pipe').
    description carries optional resident notes as supplementary context.
    bio is included per worker but is nullable — the ML engine handles
    missing bios gracefully with a neutral text score.
    years_experience is now included as a scoring signal.
    """
    # Resolve job type name — prefer job_type.name if FK populated,
    # fall back to job_request.title (set to specific_problem on creation)
    job_type_name = ''
    if job_request.job_type_id:
        try:
            job_type_name = job_request.job_type.name
        except Exception:
            pass
    if not job_type_name:
        job_type_name = job_request.title or ''

    return {
        'job_request': {
            'job_type_name': job_type_name,
            'description':   job_request.description or '',
            'budget_min':    float(job_request.budget_min) if job_request.budget_min is not None else None,
            'budget_max':    float(job_request.budget_max) if job_request.budget_max is not None else None,
            'location_lat':  float(job_request.location_lat) if job_request.location_lat is not None else None,
            'location_lng':  float(job_request.location_lng) if job_request.location_lng is not None else None,
        },
        'candidates': [
            {
                'worker_id':        str(w.id),
                'declared_rate':    float(w.declared_rate),
                'avg_rating':       float(w.avg_rating),
                'years_experience': int(w.years_experience or 0),
                'address_lat':      float(w.address_lat) if w.address_lat is not None else None,
                'address_lng':      float(w.address_lng) if w.address_lng is not None else None,
                'bio':              w.bio or '',
            }
            for w in candidates
        ],
    }


def get_matched_workers(job_request, candidates) -> list[dict[str, Any]]:
    """
    Call POST /match/ on the ML service and return the ranked list.
    Raises MLServiceUnavailable on timeout or non-200 response so the
    Django view can return HTTP 503 without losing the job_request record.
    """
    payload = _build_payload(job_request, candidates)

    try:
        response = requests.post(
            f'{ML_SERVICE_URL}/match/',
            json=payload,
            headers={
                'Content-Type': 'application/json',
                'X-Service-Key': SERVICE_API_KEY,
            },
            timeout=ML_TIMEOUT_SECONDS,
        )
    except requests.Timeout:
        raise MLServiceUnavailable('ML service timed out after 10 seconds.')
    except requests.ConnectionError as exc:
        raise MLServiceUnavailable(f'ML service connection failed: {exc}')

    if response.status_code == 403:
        raise MLServiceUnavailable('ML service rejected the request (invalid API key).')
    if response.status_code != 200:
        raise MLServiceUnavailable(
            f'ML service returned HTTP {response.status_code}: {response.text[:200]}'
        )

    data = response.json()
    # Response shape: { "ranked": [{ "worker_id", "score", "score_breakdown" }, ...] }
    return data.get('ranked', [])