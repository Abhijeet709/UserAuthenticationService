# User Authentication Service

A small FastAPI-based authentication service. Provides signup, login (JWT bearer
tokens) and a `/auth/me` endpoint that validates an access token.

```
[ Client (Web) ]
       |
   FastAPI app
       |
   Auth Service
       |
 ┌───────────────┬───────────────┐
 | Postgres      | Redis         |
 | (users)       | (sessions)*   |
 └───────────────┴───────────────┘
```

\* Redis-backed sessions / refresh tokens are not implemented yet — see
"Roadmap" at the bottom.

## Layout

```
configs/        Settings loader (pydantic-settings)
controller/     FastAPI router and dependencies
models/         Pydantic request / domain models
repository/     asyncpg connection pool wrapper
services/
  JWT/          Token encode / decode
  login/        Login service + queries
  signup/       Signup service + queries + password hashing
tests/          Unit tests (pytest + pytest-asyncio)
schema.sql      Postgres schema
```

## Quick start

```bash
python -m venv .venv
.venv\Scripts\activate           # Windows
# source .venv/bin/activate      # Linux / macOS

pip install -r requirements.txt

cp .env.example .env             # then edit values
psql "$DATABASE_URL" -f schema.sql

uvicorn main:app --reload
```

Visit `http://localhost:8000/docs` for the OpenAPI UI.

## Endpoints

| Method | Path           | Description                                  |
| ------ | -------------- | -------------------------------------------- |
| GET    | `/`            | Liveness banner                              |
| GET    | `/health`      | Health check                                 |
| POST   | `/auth/signup` | Create a user                                |
| POST   | `/auth/login`  | Exchange credentials for an access token     |
| GET    | `/auth/me`     | Validate the bearer token, return `user_id`  |

## Configuration

All configuration is read from environment variables (a `.env` file is loaded
automatically). See `.env.example` for the full list.

## Tests

```bash
pytest
```

## Roadmap / not yet implemented

- Refresh tokens and token revocation (Redis sessions).
- Password reset flow (email).
- Email verification at signup.
- Rate limiting / brute-force protection on `/auth/login`.
- Migrations via Alembic (currently a single `schema.sql`).
- Dockerfile and docker-compose with Postgres.
