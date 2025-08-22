# FastAPI Authentication Boilerplate

Production-ready authentication starter for FastAPI with clean architecture, JWT (access/refresh via HttpOnly cookies), email verification, password reset, RBAC, sessions, and auditing.

## Features
- User registration (email/password)
- Login with access (15m) + refresh (30d) JWT via HttpOnly, Secure, SameSite cookies
- Logout (revoke session)
- Refresh with rotating refresh tokens (per-session, hashed in DB)
- Email verification (token-based)
- Password reset (token-based)
- Role-based access control (user/admin)
- Session management (list + revoke)
- Audit log (login, logout, refresh, reset)
- Argon2 password hashing
- Device fingerprinting (IP + User-Agent hash)
- Rate limit login attempts (Redis)
- SQLAlchemy 2.0, Alembic, Postgres, Docker, Pytest, Pydantic v2

## Quick Start (Docker)

1. Create env file from example
```
cp env.example .env
```

2. Start services (development compose)
```
docker compose up --build
```

3. Apply migrations (first run only)
```
docker compose exec api alembic upgrade head
```

4. Open API docs: http://localhost:8000/docs

## Production (Docker)

Use the production compose file with Gunicorn and Postgres:

```
cp env.example .env        # or set env vars in your platform
docker compose -f docker-compose.prod.yml up --build -d
docker compose -f docker-compose.prod.yml exec app alembic upgrade head
```

Notes:
- Provide strong `SECRET_KEY` and a real `DATABASE_URL` via environment or `.env`.
- Redis is optional for rate limiting. If you do not set `REDIS_URL`, an in-memory fallback is used (see `app/core/rate_limit.py`).
- For HTTPS, set `COOKIE_SECURE=true` and run behind a reverse proxy/ingress that terminates TLS.

## Local Development (without Docker)
- Create and activate a virtualenv
- `pip install -r requirements.txt`
- Ensure Postgres (and optional Redis) are running and env vars are set
- `uvicorn app.main:app --reload`

## Project Structure
```
app/
  api/
    routes/
  core/
  db/
  models/
  schemas/
  services/
  utils/
  main.py
alembic/
  versions/
Dockerfile
docker-compose.yml
requirements.txt
.env.example
```

## Testing
```
pytest -q
```

## Notes
- Cookies are HttpOnly, Secure, SameSite=Lax by default (configurable).
- Refresh tokens rotate on each use and previous one is invalidated.
- Email sending is stubbed; integrate your provider in `app/services/email.py`.
