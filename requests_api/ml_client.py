# requests_api/ml_client.py
#
# Inter-Service HTTP Client — Skill-Link CDO Django Backend
#
# This module is the only place in the Django that communicates to ML
# The Django API contains NO Scikit-learn or Pandas imports.
# All ML computation is delegated to the FastAPI service.

import os
import logging
import requests as http_client
 
logger = logging.getLogger(__name__)
 
ML_SERVICE_URL    = os.environ.get("ML_SERVICE_URL", "")
SERVICE_API_KEY   = os.environ.get("SERVICE_API_KEY", "")
ML_TIMEOUT_SECONDS = 10  # SRS Section 7.3
 
 
class MLServiceUnavailable(Exception):
    """
    Raised when the ML service times out, refuses the connection,
    or returns a non-200 status. The caller catches this and returns
    HTTP 503 to the client. The JobRequest is NOT deleted — it remains
    in 'pending_match' status for retry.
    """
    pass
 
 
def _build_job_description(job_request) -> str:
    """
    Constructs the TF-IDF query string from the job request.
 
    Primary input: job_type.description (Admin-defined canonical text).
    Secondary input: job_request.description (optional resident note,
    stored in the existing description field).
    """
    parts = []
 
    if job_request.job_type and job_request.job_type.description.strip():
        parts.append(job_request.job_type.description.strip())
 
    if job_request.description and job_request.description.strip():
        parts.append(job_request.description.strip())
 
    return " ".join(parts) if parts else ""
 
 
def build_ml_payload(job_request, candidates) -> dict:
    """
    Builds the JSON payload for POST /match/.
 
    job_request : requests_api.models.JobRequest instance
    candidates  : QuerySet of workers.models.WorkerProfile instances,
                  already pre-filtered by Django (verified + correct category).
    """
    return {
        "job_request": {
            "job_description": _build_job_description(job_request),
            "budget_min":  float(job_request.budget_min)  if job_request.budget_min  is not None else None,
            "budget_max":  float(job_request.budget_max)  if job_request.budget_max  is not None else None,
            "location_lat": float(job_request.location_lat) if job_request.location_lat is not None else 0.0,
            "location_lng": float(job_request.location_lng) if job_request.location_lng is not None else 0.0,
        },
        "candidates": [
            {
                "worker_id":     str(w.id),
                "bio":           w.bio or "",
                "declared_rate": float(w.declared_rate),
                "avg_rating":    float(w.avg_rating),
                "address_lat":   float(w.address_lat) if w.address_lat is not None else None,
                "address_lng":   float(w.address_lng) if w.address_lng is not None else None,
            }
            for w in candidates
        ],
    }
 
 
def call_ml_service(payload: dict) -> list[dict]:
    """
    Sends POST /match/ to the FastAPI ML service.
 
    Returns:
        list of { "worker_id": str, "score": float, "score_breakdown": dict }
        ordered by composite score descending.
 
    Raises:
        MLServiceUnavailable on timeout, connection error, or non-200 response.
    """
    if not ML_SERVICE_URL:
        logger.error("ML_SERVICE_URL environment variable is not set.")
        raise MLServiceUnavailable("ML service URL is not configured.")
 
    url = f"{ML_SERVICE_URL.rstrip('/')}/match/"
    headers = {
        "Content-Type":  "application/json",
        "X-Service-Key": SERVICE_API_KEY,
    }
 
    try:
        response = http_client.post(
            url,
            json=payload,
            headers=headers,
            timeout=ML_TIMEOUT_SECONDS,
        )
    except http_client.Timeout:
        logger.error(
            "ML service timed out after %ds. Job request preserved in pending_match.",
            ML_TIMEOUT_SECONDS,
        )
        raise MLServiceUnavailable("ML service did not respond within the timeout window.")
    except http_client.ConnectionError as exc:
        logger.error("ML service connection failed: %s", exc)
        raise MLServiceUnavailable("Unable to connect to the ML service.")
 
    if response.status_code == 403:
        logger.critical(
            "ML service returned 403. Verify SERVICE_API_KEY matches in both services."
        )
        raise MLServiceUnavailable("ML service authentication failed (HTTP 403).")
 
    if response.status_code != 200:
        logger.error(
            "ML service returned unexpected status %d: %s",
            response.status_code,
            response.text[:300],
        )
        raise MLServiceUnavailable(f"ML service returned HTTP {response.status_code}.")
 
    return response.json().get("ranked", [])
 
 
def get_matched_workers(job_request, candidates) -> list[dict]:
    """
    Convenience function called by RequestListCreateView.
    Builds the payload, calls the ML service, returns the ranked list.
 
    Returns an empty list if candidates is empty (no ML call made).
    Raises MLServiceUnavailable on any failure — the view handles that.
    """
    if not candidates:
        logger.info(
            "Job request %s — no verified candidates in category '%s'. Skipping ML call.",
            job_request.id,
            job_request.category,
        )
        return []
 
    payload = build_ml_payload(job_request, candidates)
    return call_ml_service(payload)
 