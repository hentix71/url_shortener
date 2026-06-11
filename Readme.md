# URL Shortener — Backend

A production-ready URL shortening API built with **Django REST Framework**, featuring JWT authentication, Redis caching, Celery async task processing, PostgreSQL persistence, and Swagger documentation. The entire stack runs via Docker Compose.

---

## Table of Contents

- [Tech Stack](#tech-stack)
- [Architecture Overview](#architecture-overview)
- [Features](#features)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Getting Started](#getting-started)
  - [1. Clone the Repository](#1-clone-the-repository)
  - [2. Configure Environment Variables](#2-configure-environment-variables)
  - [3. Run with Docker Compose](#3-run-with-docker-compose)
  - [4. Running Locally (without Docker)](#4-running-locally-without-docker)
- [API Endpoints](#api-endpoints)
- [Authentication](#authentication)
- [Short Code Generation](#short-code-generation)
- [URL Expiry System](#url-expiry-system)
- [Caching Strategy](#caching-strategy)
- [Celery Background Tasks](#celery-background-tasks)
- [Environment Variables Reference](#environment-variables-reference)

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | Django 6 + Django REST Framework |
| Auth | JWT via `djangorestframework-simplejwt` |
| Database | PostgreSQL 17 |
| Cache / Broker | Redis 7 |
| Task Queue | Celery + Celery Beat |
| API Docs | drf-yasg (Swagger UI) |
| Containerisation | Docker + Docker Compose |
| Web Server | Gunicorn |
| Static Files | WhiteNoise |

---

## Architecture Overview

```
Client
  │
  ▼
Gunicorn (Django)
  ├── PostgreSQL  — persistent storage for users & URLs
  ├── Redis       — URL cache + click-count buffer + Celery broker
  ├── Celery Worker — async task execution
  └── Celery Beat  — periodic task scheduler (syncs click counts every 60s)
```

---

## Features

- User registration, login, logout with JWT (access + refresh tokens)
- Token blacklisting on logout
- Shorten any URL with an auto-generated or custom short code (≤7 alphanumeric chars)
- URL lifetime options: 1 Hour, 1 Day, 1 Week, or Never (permanent)
- Automatic expiry enforcement on redirect
- Click-count tracking buffered in Redis and flushed to Postgres every 60 seconds
- Cursor-based pagination for URL listing
- Search and filter on URL list (`original_url`, `short_code`, `created_at`, `expires_at`)
- `IsOwner` permission — users can only manage their own URLs
- Full Swagger / OpenAPI documentation at `/`

---

## Project Structure

```
.
├── account/                  # User auth app
│   ├── managers.py           # Custom user manager (email-based auth)
│   ├── models.py             # UUID-primary-key User model
│   ├── serializers.py
│   ├── views.py              # Register, Login, Logout
│   └── urls.py
├── url/                      # URL shortening app
│   ├── models.py             # ShortURL model
│   ├── serializers.py
│   ├── views.py              # Shorten, List, Retrieve, Update, Redirect
│   ├── urls.py
│   ├── tasks.py              # Celery task: sync click counts
│   ├── services/
│   │   ├── url_service.py    # Short-code generation logic
│   │   ├── redis_service.py  # Cache helpers
│   │   └── expiry_service.py # Expiry datetime calculation
│   └── utils/
│       └── encoder.py        # Base62 encoder
├── my_project/
│   ├── settings.py
│   ├── urls.py               # Root URL conf + Swagger
│   ├── celery.py
│   └── utils/
│       ├── custom_response.py
│       ├── custom_permissions.py
│       ├── exceptions.py
│       └── pagination.py
├── dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env.example
```

---

## Prerequisites

**For Docker (recommended):**
- [Docker](https://docs.docker.com/get-docker/) ≥ 24
- [Docker Compose](https://docs.docker.com/compose/) ≥ 2

**For local development:**
- Python 3.13
- PostgreSQL 17
- Redis 7

---

## Getting Started

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd <repo-folder>
```

### 2. Configure Environment Variables

Copy the example file and fill in your values:

```bash
cp .env.example .env
```

Open `.env` and set each variable (see [Environment Variables Reference](#environment-variables-reference) below).

### 3. Run with Docker Compose

```bash
docker compose up --build
```

Docker Compose will start six services in the correct dependency order:

| Service | Description |
|---|---|
| `postgres` | PostgreSQL database |
| `redis` | Redis instance |
| `migrate` | Runs `manage.py migrate` once on startup |
| `django` | Gunicorn app server on port `8000` |
| `worker` | Celery worker (concurrency 4) |
| `beat` | Celery Beat scheduler |

The API will be available at **http://localhost:8000**.  
Swagger UI is served at **http://localhost:8000/**.

To run in detached mode:

```bash
docker compose up --build -d
```

To stop all services:

```bash
docker compose down
```

To stop and remove volumes (wipes database and Redis data):

```bash
docker compose down -v
```

### 4. Running Locally (without Docker)

Make sure PostgreSQL and Redis are running locally, then:

```bash
# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Apply database migrations
python manage.py migrate

# Start the development server
python manage.py runserver

# In a separate terminal — start the Celery worker
celery -A my_project worker -l info

# In another terminal — start Celery Beat
celery -A my_project beat -l info
```

---

## API Endpoints

All endpoints are documented interactively at `http://localhost:8000/`.

### Account (`/api/account/`)

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/api/account/register/` | Public | Register a new user |
| POST | `/api/account/login/` | Public | Login and receive JWT tokens |
| POST | `/api/account/logout/` | Bearer | Blacklist refresh token |
| POST | `/api/account/token/refresh/` | Public | Obtain new access token |

### URL Management (`/api/url/`)

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/api/url/shorten/` | Bearer | Create a short URL |
| GET | `/api/url/list-urls/` | Bearer | List authenticated user's URLs |
| GET | `/api/url/retrieve/<short_code>/` | Bearer | Retrieve a single URL record |
| PATCH | `/api/url/update/<short_code>/` | Bearer | Update short code or expiry |
| GET | `/api/url/redirect/<short_code>/` | Public | Redirect to original URL |

#### List URLs — query parameters

| Parameter | Type | Description |
|---|---|---|
| `search` | string | Filter by `original_url` or `short_code` |
| `created_at` | datetime | Exact filter on creation date |
| `expires_at` | datetime | Exact filter on expiry date |
| `cursor` | string | Cursor for pagination |

---

## Authentication

The API uses **JWT Bearer tokens**.

1. Register or login to receive `Access Token` and `Refresh Token`.
2. Include the access token in the `Authorization` header for protected endpoints:

```
Authorization: Bearer <access_token>
```

3. Access tokens expire after **30 minutes**. Use the refresh endpoint to obtain a new one.
4. Refresh tokens expire after **7 days**.
5. Calling `/api/account/logout/` blacklists the refresh token immediately.

---

## Short Code Generation

When no custom short code is provided, one is generated automatically:

1. An atomic counter stored in Redis is incremented to obtain a unique integer ID.
2. The integer is encoded to Base62 (`0-9a-zA-Z`).
3. A random 2-character Base62 prefix is prepended.
4. A uniqueness check is performed against the database; generation retries if a collision occurs.

Custom short codes must be ≤ 7 alphanumeric characters.

---

## URL Expiry System

| Option | Value | Duration |
|---|---|---|
| `1h` | 1 Hour | Expires 1 hour after creation |
| `1d` | 1 Day | Expires 24 hours after creation |
| `1w` | 1 Week | Expires 7 days after creation |
| `never` | Permanent | Never expires (default) |

Expiry is checked on every redirect. Expired URLs return `410 Gone`.

---

## Caching Strategy

Redis is used as a read-through cache for redirect lookups:

- On first redirect, the short code is looked up in PostgreSQL, then cached in Redis for the remaining TTL of the URL (or 30 minutes for permanent URLs).
- Subsequent redirects for the same short code are served entirely from Redis — no database hit.
- Click counts are buffered as Redis counters (`clicks:<short_code>`) and flushed to PostgreSQL every 60 seconds by the Celery Beat task, avoiding a DB write on every click.
- The `ListURLSerializer` adds pending Redis click counts to the stored DB count so the UI always shows real-time totals.

---

## Celery Background Tasks

| Task | Schedule | Description |
|---|---|---|
| `url.tasks.sync_click_counts` | Every 60 seconds | Scans all `clicks:*` keys in Redis, increments the corresponding `ShortURL.click_count` in Postgres, then deletes the Redis key |

---

## Environment Variables Reference

| Variable | Description | Example |
|---|---|---|
| `SECRET_KEY` | Django secret key | `django-insecure-...` |
| `DEBUG` | Enable debug mode | `True` / `False` |
| `DB_NAME` | PostgreSQL database name | `urlshortener` |
| `DB_USER` | PostgreSQL username | `postgres` |
| `DB_PASSWORD` | PostgreSQL password | `password` |
| `DB_HOST` | PostgreSQL host | `postgres` (Docker) / `localhost` |
| `DB_PORT` | PostgreSQL port | `5432` |
| `REDIS_HOST` | Redis host | `redis` (Docker) / `localhost` |
| `REDIS_PORT` | Redis port | `6379` |
| `REDIS_DB` | Redis database number | `0` |
| `LOCATION` | Full Redis URL for Django cache | `redis://redis:6379/0` |
| `CELERY_BROKER_URL` | Celery broker URL | `redis://redis:6379/0` |
| `CELERY_RESULT_BACKEND` | Celery result backend URL | `redis://redis:6379/0` |