# Skill-Link CDO — Backend API

**A Machine Learning-Assisted Barangay-Based Skilled Labor Registry and Matching System for Cagayan de Oro City**

---

## Overview

Skill-Link CDO is a community-level digital platform that connects barangay-verified skilled workers with residents in Cagayan de Oro City. The system addresses the lack of a structured, trustworthy channel through which residents can find qualified local workers for household and livelihood services. This system is a running a .v1 pilot 1 barangay, and will enhance in the future for .v2 city wide implementation.

This repository contains the **Django REST Framework (DRF) backend** that powers all three portals of the Skill-Link CDO platform:

- **Admin Portal** — Barangay administrators manage worker and resident verification, skill categories, rate bands, and system-wide analytics.
- **Worker Portal** — Skilled workers register, manage their profiles, and respond to job offers sent by residents.
- **Resident Portal** — Residents submit job requests, receive ML-ranked worker matches, send offers, and rate completed work.

---

## The Problem It Solves

Barangay residents in Cagayan de Oro frequently rely on informal word-of-mouth referrals to find skilled workers for home repairs and household services. This creates three core problems:

1. **No accountability** — Workers have no verifiable credentials or performance history.
2. **No price transparency** — Rates are arbitrary with no community standard.
3. **No structured matching** — Residents have no way to find the most qualified worker for their specific need.

Skill-Link CDO solves all three by placing barangay administrators at the center of verification, enforcing rate bands per skill category, and using a machine learning engine to rank workers for each job request.

---

## How the System Works (Model B — Resident Selects First)

The platform follows a confirmed engagement flow documented in the System Requirements Specification (SRS v1.0):

```
1. Resident submits a job request
   (service category, description, location, budget range, preferred schedule)
         ↓
2. ML engine runs synchronously
   (TF-IDF text matching + Cosine similarity + Haversine proximity + Price compatibility + Rating score)
         ↓
3. Resident receives a ranked list of verified workers
         ↓
4. Resident selects ONE worker and sends a formal offer
         ↓
5. Worker receives the offer and accepts or declines
         ↓
6. If declined → Resident selects the next worker from the ranked list
         ↓
7. Resident marks the job as complete
         ↓
8. Both parties submit a mutual rating
```

This flow is strictly enforced at the API level — workers cannot broadcast-accept jobs, and no auto-assignment occurs.

---

## Tech Stack

| Layer          | Technology                                       |
| -------------- | ------------------------------------------------ |
| Language       | Python 3.11                                      |
| Framework      | Django 5.x + Django REST Framework               |
| Authentication | Session-based (Django built-in)                  |
| Database       | SQLite (development) → PostgreSQL (production)   |
| CORS           | django-cors-headers                              |
| Frontend       | React (Vite) + TailwindCSS — separate repository |

---

## Database Schema

The backend implements **10 entities** across three domains, as defined in ERD v1.1:

### User & Profile Domain

| Entity             | Description                                                             |
| ------------------ | ----------------------------------------------------------------------- |
| `USER`             | Base authentication entity for all roles (admin, worker, resident)      |
| `ADMIN_PROFILE`    | Barangay-specific information for admin users                           |
| `WORKER_PROFILE`   | Professional profile: skills, rate, verification status, average rating |
| `RESIDENT_PROFILE` | Personal profile: address, contact, verification status                 |

### Governance Domain

| Entity           | Description                                                                              |
| ---------------- | ---------------------------------------------------------------------------------------- |
| `SKILL_CATEGORY` | The 5 pilot skill categories (Plumbing, Electrical, Carpentry, Mason, Welding)           |
| `RATE_BAND`      | Admin-defined min/max acceptable daily rates per skill category                          |
| `DOCUMENT`       | Worker certifications, clearances, and documents (metadata only; files in cloud storage) |

### Job Transaction Domain

| Entity        | Description                                                                          |
| ------------- | ------------------------------------------------------------------------------------ |
| `JOB_REQUEST` | Core transaction entity — contains all ML input data (description, location, budget) |
| `JOB_OFFER`   | Formal engagement between resident and a selected worker                             |
| `RATING`      | Mutual performance review submitted by both parties after job completion             |

### Key Design Decisions (ERD v1.1)

- All primary keys use **UUID** — avoids sequential ID exposure in API URLs
- **Soft deletion only** — no records are hard deleted, in compliance with RA 10173 (Data Privacy Act)
- `avg_rating` is a **deliberately denormalized** cached field on `WORKER_PROFILE` for ML engine performance
- `location_lat` and `location_lng` are stored as separate `NUMERIC(10,7)` columns — Haversine distance computed in Python, not at the database layer

---

## API Endpoints

All endpoints are prefixed with `/api/`.

### Authentication

| Method | Endpoint              | Description                 | Access        |
| ------ | --------------------- | --------------------------- | ------------- |
| `POST` | `/api/auth/register/` | Register a new user account | Public        |
| `POST` | `/api/auth/login/`    | Login and start a session   | Public        |
| `POST` | `/api/auth/logout/`   | End the current session     | Authenticated |

### Workers

| Method  | Endpoint                    | Description                                                  | Access        |
| ------- | --------------------------- | ------------------------------------------------------------ | ------------- |
| `GET`   | `/api/workers/`             | List all verified workers (residents) or all workers (admin) | Authenticated |
| `GET`   | `/api/workers/<id>/`        | Get full worker profile                                      | Authenticated |
| `PATCH` | `/api/workers/<id>/verify/` | Update worker verification status                            | Admin         |

### Residents

| Method  | Endpoint                      | Description                         | Access |
| ------- | ----------------------------- | ----------------------------------- | ------ |
| `GET`   | `/api/residents/`             | List all residents for verification | Admin  |
| `PATCH` | `/api/residents/<id>/verify/` | Update resident verification status | Admin  |

### Skill Categories & Rate Bands

| Method | Endpoint                | Description                  | Access        |
| ------ | ----------------------- | ---------------------------- | ------------- |
| `GET`  | `/api/categories/`      | List all skill categories    | Authenticated |
| `POST` | `/api/categories/`      | Create a new skill category  | Admin         |
| `PUT`  | `/api/categories/<id>/` | Update category or rate band | Admin         |

### Job Requests

| Method  | Endpoint                       | Description                                               | Access           |
| ------- | ------------------------------ | --------------------------------------------------------- | ---------------- |
| `GET`   | `/api/requests/`               | List requests (own requests for residents, all for admin) | Authenticated    |
| `POST`  | `/api/requests/create/`        | Submit a new job request                                  | Resident         |
| `GET`   | `/api/requests/<id>/match/`    | Get ML-ranked worker list for a request                   | Resident         |
| `POST`  | `/api/requests/<id>/offer/`    | Send a job offer to a selected worker                     | Resident         |
| `PATCH` | `/api/requests/<id>/complete/` | Mark a job as complete                                    | Resident         |
| `PATCH` | `/api/requests/<id>/cancel/`   | Cancel a job request (soft cancel)                        | Resident / Admin |
| `POST`  | `/api/requests/<id>/rate/`     | Submit a rating after job completion                      | Resident         |

### Job Offers

| Method  | Endpoint                    | Description                         | Access |
| ------- | --------------------------- | ----------------------------------- | ------ |
| `PATCH` | `/api/offers/<id>/respond/` | Accept or decline an incoming offer | Worker |

### Admin Analytics

| Method | Endpoint      | Description                        | Access |
| ------ | ------------- | ---------------------------------- | ------ |
| `GET`  | `/api/stats/` | KPI counts for the admin dashboard | Admin  |

---

## Job Request & Offer Status Flows

### JOB_REQUEST.status

```
pending_match → offer_sent → offer_accepted → completed
                                           → cancelled
```

### JOB_OFFER.status

```
pending_response → accepted
               → declined  (resident may send a new offer to the next ranked worker)
```

### WORKER_PROFILE / RESIDENT_PROFILE.verification_status

```
pending → verified
       → rejected → pending (after user corrects and resubmits)
       → flagged  → verified (Admin override)
```

---

## Final Project Structure (Currently on initial Setup)

```
skilllink-cdo-backend/
├── core/                        ← Custom User model, authentication
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   └── admin.py
├── workers/                     ← Worker profiles, verification, documents
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   └── admin.py
├── residents/                   ← Resident profiles, verification
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   └── admin.py
├── jobs/                        ← Job requests, offers, ratings, ML match
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   └── admin.py
├── skilllink/                   ← Project configuration
│   ├── settings.py
│   └── urls.py
├── manage.py
├── requirements.txt
└── README.md
```

---

## Getting Started

### Prerequisites

- Python 3.11+
- pip
- Git

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/Quenie-Ann/Skill-Link-Cdo-Backend.git
cd Skill-Link-Cdo-Backend

# 2. Create and activate virtual environment
python -m venv venv

# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run migrations
python manage.py makemigrations
python manage.py migrate

# 5. Seed pilot data (categories, test accounts)
python manage.py seed

# 6. Create a superuser (for Django admin panel)
python manage.py createsuperuser

# 7. Start the development server
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000/`.  
The Django admin panel is at `http://127.0.0.1:8000/admin/`.

---

## Demo Accounts (after running seed)

| Role     | Email                  | Password    |
| -------- | ---------------------- | ----------- |
| Admin    | admin@skilllink.com    | admin123    |
| Worker   | worker@skilllink.com   | worker123   |
| Resident | resident@skilllink.com | resident123 |

---

## Testing with httpie

```bash
# Install httpie
pip install httpie

# Register a new resident
http POST http://127.0.0.1:8000/api/auth/register/ \
  email="test@skilllink.com" \
  password="test123" \
  role="resident"

# Login
http POST http://127.0.0.1:8000/api/auth/login/ \
  email="admin@skilllink.com" \
  password="admin123"

# Get all workers (admin)
http GET http://127.0.0.1:8000/api/workers/

# Submit a job request (as resident)
http POST http://127.0.0.1:8000/api/requests/create/ \
  category_id=1 \
  description="Leaking pipe under kitchen sink" \
  location_address="Zone 1, Bulua, CDO" \
  budget_min:=400 \
  budget_max:=600

# Get ML-ranked workers for a request
http GET http://127.0.0.1:8000/api/requests/1/match/
```

---

## Pilot Skill Categories

The system currently supports five skill categories in the Bulua barangay pilot:

| Category   | Description                                        |
| ---------- | -------------------------------------------------- |
| Plumbing   | Pipe installation, leak repair, drainage, fixtures |
| Electrical | Wiring, circuit breakers, outlets, panel upgrades  |
| Carpentry  | Furniture, cabinets, doors/windows, flooring       |
| Mason      | Brickwork, concrete, tile setting, plastering      |
| Welding    | Gates, fences, metal fabrication, pipe welding     |

---

## Related Repositories

| Repository               | Description                                                             |
| ------------------------ | ----------------------------------------------------------------------- |
| `skill-link-cdo`         | React (Vite) web application — Admin, Worker, and Resident portals      |
| `Skill-Link-Cdo-Mobile`  | React Native (Expo Go) mobile pplication - Worker, and Resident portals |
| `Skill-Link-Cdo-Backend` | This repository — Django REST Framework API                             |

---

## Academic Information

**Course Subject:** Application Development and Emerging Technologies
**Institution:** University of Science and Technology of Southern Philippines  
**Academic Year:** 2025–2026

---

## License

This project is developed for academic purposes only.
