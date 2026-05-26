# Skill-Link CDO — Django REST API Backend

## Project Description

Skill-Link CDO is a machine learning-assisted, barangay-based skilled worker registry and matching system for Cagayan de Oro City, Philippines. This repository contains the Django REST Framework backend — the central integration hub of the system. It handles authentication, profile management, job transactions, rate governance, notification dispatch, and analytics aggregation. It is the sole client of the PostgreSQL database and the sole caller of the FastAPI ML matching service.

---

## Features

- **Authentication & Security:** JWT-based login with role-based access control (Worker, Resident, Admin). Refresh tokens stored in HttpOnly cookies. Login event logging, new-device email alerts, rate limiting (10 attempts/minute on login), token blacklisting on rotation, and one-time UUID password reset tokens with 15-minute expiry.
- **Profile Management:** Worker and resident registration, profile editing, admin verification queue, walk-in registration flow, and RA 10173-compliant soft deletion.
- **Document Handling:** Multipart file upload to Cloudinary or Supabase Storage. Time-limited access URL generation. Document access restricted to owner and admin.
- **Rate Governance:** Admin-defined rate bands per skill category. Automatic `flagged` status assignment when a worker's declared rate falls outside the active band.
- **ML Job Matching:** Accepts job requests from verified residents, pre-filters verified worker candidates by exact skill category, and calls the FastAPI ML service via authenticated HTTP POST. Returns a ranked worker list with composite scores and score breakdowns.
- **Job Engagement:** Full job lifecycle management — offer creation, accept/decline, job completion, and mutual rating submission. Atomic update of worker `avg_rating` via Django post-save signal.
- **Analytics:** Admin dashboard aggregates — worker counts, job request volume, weekly trends, skill category breakdown, ML match logs, and activity feed.
- **Notifications:** In-app notification creation for key job lifecycle events (new offer, accepted, completed, rated) with read/dismiss support.
- **Audit Logging:** Append-only audit log for all admin actions involving personal data (RA 10173 compliance).

---

## Technology Stack

| Layer                | Technology                                                  |
| -------------------- | ----------------------------------------------------------- |
| Language             | Python 3.11+                                                |
| Framework            | Django 5.x + Django REST Framework                          |
| Authentication       | djangorestframework-simplejwt                               |
| Database ORM         | Django ORM                                                  |
| Database             | PostgreSQL 15+                                              |
| API Documentation    | drf-yasg (Swagger UI / ReDoc)                               |
| CORS                 | django-cors-headers                                         |
| Static Files         | WhiteNoise                                                  |
| Environment Config   | python-dotenv                                               |
| Database URL Parsing | dj-database-url                                             |
| Email                | Django email backend (SMTP / Resend API via django-anymail) |
| Deployment           | Render (Web Service)                                        |

> **Note:** This repository intentionally excludes Scikit-learn and Pandas. All ML logic resides in the separate `Skill-Link-Cdo-ML` repository.

---

## System Architecture

```
[React Web App / React Native Mobile]
        │  HTTPS + JWT Bearer Token
        ▼
┌─────────────────────────────────────────┐
│         Django REST API (this repo)     │
│                                         │
│  ┌──────────┐  ┌──────────┐            │
│  │   Auth   │  │ Profiles │            │
│  └──────────┘  └──────────┘            │
│  ┌──────────┐  ┌──────────┐            │
│  │  Jobs &  │  │Analytics │            │
│  │ Matching │  │  & Notif │            │
│  └──────────┘  └──────────┘            │
└──────────┬─────────────┬───────────────┘
           │             │
    HTTP POST         Django ORM
  X-Service-Key          │
           ▼             ▼
  [FastAPI ML Service]  [PostgreSQL]
           │
           ▼
  [Cloudinary / Supabase Storage]
```

---

## API Endpoints (Summary)

Full interactive documentation is available at `/swagger/` or `/redoc/` when the server is running.

| Method | Endpoint                                  | Description                                        |
| ------ | ----------------------------------------- | -------------------------------------------------- |
| POST   | `/api/login/`                             | Authenticate and receive JWT tokens                |
| POST   | `/api/register/`                          | Register a new Worker or Resident account          |
| GET    | `/api/me/`                                | Get the authenticated user's profile               |
| POST   | `/api/logout/`                            | Blacklist the refresh token                        |
| GET    | `/api/workers/`                           | Admin: list all workers                            |
| PATCH  | `/api/workers/<uuid>/verify/`             | Admin: approve or reject a worker                  |
| GET    | `/api/skill-categories/`                  | List all active skill categories                   |
| GET    | `/api/skill-categories/<uuid>/job-types/` | List job types for a category                      |
| POST   | `/api/requests/`                          | Resident: submit a job request (triggers ML match) |
| GET    | `/api/resident/requests/`                 | Resident: list own job requests                    |
| POST   | `/api/requests/<uuid>/send-offer/<uuid>/` | Resident: send offer to a worker                   |
| GET    | `/api/worker/match/pending/`              | Worker: get incoming pending offer                 |
| POST   | `/api/worker/match/<uuid>/accept/`        | Worker: accept a job offer                         |
| POST   | `/api/worker/match/<uuid>/decline/`       | Worker: decline a job offer                        |
| POST   | `/api/ratings/`                           | Submit a rating for a completed job                |
| GET    | `/api/notifications/`                     | List unread notifications                          |
| GET    | `/api/stats/`                             | Admin: KPI aggregates                              |

---

## Installation & Setup

### Prerequisites

- Python 3.11+
- pip
- PostgreSQL (local) or a Render/Supabase managed instance
- The FastAPI ML service (`Skill-Link-Cdo-ML`) must be running and accessible

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/Quenie-Ann/Skill-Link-Cdo-Backend.git
cd skill-link-cdo-backend

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables
cp .env.example .env
# Edit .env — see Environment Variables table below

# 5. Apply database migrations
python manage.py migrate

# 6. Create a superuser (Barangay Admin account)
python manage.py createsuperuser

# 7. Start the development server
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000/`.
Swagger documentation: `http://127.0.0.1:8000/swagger/`

### Environment Variables

| Variable               | Description                                  | Example                                     |
| ---------------------- | -------------------------------------------- | ------------------------------------------- |
| `SECRET_KEY`           | Django secret key                            | `your-secret-key-here`                      |
| `DEBUG`                | Enable debug mode                            | `True`                                      |
| `ALLOWED_HOSTS`        | Comma-separated allowed hosts                | `localhost`                                 |
| `DATABASE_URL`         | PostgreSQL connection URL (production)       | `postgresql://user:pass@host/db`            |
| `CORS_ALLOWED_ORIGINS` | Comma-separated allowed frontend origins     | `http://localhost:5173,https://.vercel.app` |
| `ML_SERVICE_URL`       | Base URL of the FastAPI ML service           | `https://.onrender.com`                     |
| `ML_SERVICE_API_KEY`   | Shared API key for ML service authentication | `your-ml-service-key`                       |
| `EMAIL_HOST_USER`      | SMTP sender address                          | `noreply@skilllink.com`                     |
| `EMAIL_HOST_PASSWORD`  | SMTP password                                | `your-smtp-password`                        |

> **Security:** `CORS_ALLOW_ALL_ORIGINS` must never be `True` in staging or production environments.

---

## Deployment Link

**Live API Base URL:** `https://skill-link-cdo-backend.onrender.com/api`
**Swagger UI:** `https://skill-link-cdo-backend.onrender.com/swagger/`

---

## Test Accounts

| Role           | Email                    | Password      |
| -------------- | ------------------------ | ------------- |
| Barangay Admin | `admin@skilllink.com`    | `admin123`    |
| Skilled Worker | `worker@skilllink.com`   | `worker123`   |
| Resident       | `resident@skilllink.com` | `resident123` |

---

## Team Members and Roles

| Name                     | Role                                                 |
| ------------------------ | ---------------------------------------------------- |
| [Abragan, Quenie Ann H.] | Backend Lead / API Design / Integration & Deployment |
| [Tubio, Johnlie P.]      | Worker & Resident API Endpoints                      |
| [Gaccion, Tirso Louise]  | Worker & Resident API Endpoints                      |

---

## Known Limitations

- **Synchronous ML pipeline.** The ML matching call is synchronous and blocks the Django request thread until the FastAPI service responds. Under the pilot scope of up to 50 concurrent users this is acceptable. City-wide deployment will require replacing this with an asynchronous Celery task queue backed by Redis.
- **Polling-based notifications.** In-app notifications are delivered via client polling rather than WebSocket push. A future enhancement will introduce Server-Sent Events (SSE) for real-time delivery.
- **Free-tier cold starts.** On Render's free tier, the service hibernates after inactivity. The first request after a cold start may take up to 30 seconds. A scheduled health-check ping to `GET /api/health/` every 10 minutes mitigates this during active hours.
- **Document authenticity.** Uploaded certifications and clearances cannot be verified programmatically. Manual review by the Barangay Administrator is required.
- **No asynchronous email.** Transactional emails (login alerts, password reset) are sent synchronously within the request cycle. High email volume could introduce latency.

---

## Screenshots

> _(Add screenshots of the Swagger UI and ReDoc documentation pages here.)_
> ![Swagger UI](image.png)
