# FastAPI Authentication Boilerplate

A production-ready authentication and session management system built with [FastAPI](https://fastapi.tiangolo.com/). It provides robust, secure primitives for JWT-based auth, sessions, email verification, password reset, and RBAC, with clean architecture and deploy-ready tooling.

## Features

- JWT authentication with access and refresh tokens (HttpOnly cookies)
- Device-aware sessions (IP and User-Agent fingerprint)
- Argon2 password hashing (memory-hard)
- Email verification and password reset flows
- Role-based access control (RBAC)
- Rate limiting for login attempts (Redis or in-memory fallback)
- SQLAlchemy 2.0 + Alembic migrations
- Dockerfiles and compose for local and production

## Architecture

```
app/
  api/        # routers and dependencies
  core/       # config, security, rate limiting
  db/         # engine/session setup
  models/     # SQLAlchemy models
  schemas/    # Pydantic models
  services/   # business logic (auth, sessions, email)
  utils/      # helpers (cookies, etc.)
  main.py     # FastAPI app factory/assembly
alembic/      # database migrations
```

## Setup (Docker)

1) Copy environment template and configure values:
```bash
cp env.example .env
```

2) Start services (development):
```bash
docker compose up --build
```

3) Apply migrations:
```bash
docker compose exec api alembic upgrade head
```

4) Open API docs:
```
http://localhost:8000/docs
```

## Setup (Local)

1) Create a virtual environment and install dependencies:
```bash
pip install -r requirements.txt
```

2) Provision a database (PostgreSQL recommended) and set env vars. For SQLite, set `DB_BACKEND=sqlite` and optionally `SQLITE_PATH`.

3) (Optional) Start Redis for rate limiting, or leave `REDIS_URL` unset to use in-memory fallback (see `app/core/rate_limit.py`).

4) Run the server:
```bash
uvicorn app.main:app --reload --port 8000
```

## Configuration

Configuration is managed by Pydantic Settings from `.env` (see `app/core/config.py`). A ready-to-copy template is provided in `env.example`.

Key variables:
- `SECRET_KEY` (required)
- `DATABASE_URL` (for Postgres) or `DB_BACKEND=sqlite` with `SQLITE_PATH`
- `COOKIE_SECURE` and `COOKIE_SAMESITE` for cookie policy
- `REDIS_URL` (optional). If not set, rate limiting falls back to in-memory per-process storage

## Migrations

Generate and apply migrations with Alembic:
```bash
alembic revision --autogenerate -m "message"
alembic upgrade head
```

## Testing

```bash
pytest -q
```

## Production Deployment

Use the production compose file (Gunicorn + Uvicorn workers):
```bash
cp env.example .env
docker compose -f docker-compose.prod.yml up --build -d
docker compose -f docker-compose.prod.yml exec app alembic upgrade head
```

Recommendations:
- Provide a strong `SECRET_KEY` and a production `DATABASE_URL`
- Run behind a TLS-terminating proxy and set `COOKIE_SECURE=true`
- Set `REDIS_URL` to enable distributed rate limiting (optional)

## Security Notes

- Passwords are hashed with Argon2
- JWTs are set in HttpOnly cookies to mitigate XSS token theft
- Refresh tokens rotate; previous tokens are invalidated
- Login attempts are rate limited via Redis when available

## License

Licensed under the MIT License. See `LICENSE` for details.
