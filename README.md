# SkillLink Platform

> A platform that connects clients with verified specialists for on-demand services.

---

## Problem Statement

Finding reliable specialists (plumbers, electricians, tutors, etc.) is slow and trust-dependent. SkillLink solves this by creating a structured marketplace where specialists are accredited, rated, and bookable — all in one place.

---

## Features

- JWT-based authentication with token blocklist (logout support)
- Specialist profiles with accreditation, ratings, and H3 geolocation zones
- Order lifecycle management (create → request → approve → complete)
- File upload support for specialist images
- Background tasks via Celery (email notifications, image processing, order expiry)
- Rate limiting and request logging middleware
- Fully containerized with Docker Compose

---

## Technology Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI (Python 3.12) |
| Database | PostgreSQL 16 + SQLModel + Alembic |
| Cache / Broker | Redis 7 |
| Background Tasks | Celery + Celery Beat |
| Frontend | React 18 + TypeScript + Vite |
| Animations | Framer Motion |
| Containerization | Docker + Docker Compose |
| Reverse Proxy | Nginx |

---

## Installation

### Prerequisites

- Docker and Docker Compose installed
- Git

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/your-username/skilllink-platform.git
cd skilllink-platform

# 2. Copy and configure environment variables
cp .env.example .env
# Edit .env with your database credentials, secret keys, etc.

# 3. Build and start all services
docker compose up -d --build

# 4. Run database migrations
docker compose exec api alembic upgrade head
```

---

## Usage

Once running, the following services are available:

| URL | Service |
|-----|---------|
| http://localhost:8000/docs | FastAPI Swagger UI (API docs) |
| http://localhost:80 | Nginx → API |
| http://localhost:5173 | Frontend (Vite dev server) |
| http://localhost:5555 | Flower (Celery task monitor) |
| http://localhost:8081 | Redis Commander (cache inspector) |
| http://localhost:8082 | Adminer (database viewer) |

### Useful Commands

```bash
# View API logs
docker compose logs -f api

# View Celery worker logs
docker compose logs -f celery_worker

# Rebuild only the API after code changes
docker compose up -d --build api

# Stop everything (data preserved)
docker compose down

# Stop and wipe all data
docker compose down -v
```

---

## Project Structure

```
skilllink-platform/
├── backend/
│   └── app/
│       ├── api/v1/        # Route handlers (Auth, Orders, Specialists, etc.)
│       ├── core/          # Config, security, Redis client
│       ├── dao/           # Data access layer
│       ├── db/            # SQLModel models and DB session
│       ├── exceptions/    # Custom exception classes
│       ├── middleware/     # Logging, rate limiting, profiling
│       ├── schemas/        # Pydantic request/response schemas
│       ├── services/       # Business logic layer
│       ├── tasks/          # Celery tasks (email, image, orders)
│       ├── validation/     # Input validation helpers
│       └── main.py        # FastAPI app entrypoint
├── frontend/
│   └── src/
│       ├── App.tsx
│       ├── main.tsx
│       └── styles.css
├── alembic/               # Database migration scripts
├── nginx/                 # Nginx reverse proxy config
├── Dockerfile
├── docker-compose.yml
├── .gitignore
├── .dockerignore
└── README.md
```

---

## API Overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Register a new user |
| POST | `/api/v1/auth/login` | Login and receive JWT |
| POST | `/api/v1/auth/logout` | Invalidate token |
| GET | `/api/v1/specialists` | Browse specialists |
| POST | `/api/v1/orders` | Create an order |
| GET | `/api/v1/catalog` | Get service categories |

Full interactive docs available at `/docs` when the app is running.
