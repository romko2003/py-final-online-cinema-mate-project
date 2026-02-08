# Online Cinema API (Mate Academy — Online Cinema Project)

Backend API for an online cinema platform built with **FastAPI**, **SQLAlchemy**, **PostgreSQL**, **JWT (access/refresh)**, **Docker Compose**, and **Poetry**.

This repo follows the Mate Academy “FLEX” approach: I implement **8 core features** from the project specification and cover all custom endpoints with tests.

---

## Tech Stack

- **FastAPI** — REST API + Swagger/OpenAPI docs
- **SQLAlchemy 2.0** — ORM
- **Alembic** — DB migrations
- **PostgreSQL** — main database
- **JWT** — access & refresh auth flow
- **Poetry** — dependency management
- **Docker + Docker Compose** — local dev environment
- **Pytest + coverage** — automated tests
- **GitHub Actions** — CI (lint/type-check/tests)

---

## Implemented Features (FLEX 6–8)

### Accounts & Auth
1. **Registration** by email + password  
   - Email uniqueness validation  
   - Password complexity validation  
   - Creates activation token and sends it via mailer stub (console output)

2. **Account activation** using activation token  
   - Token expiry (24h) validation  
   - After activation token is removed

3. **Resend activation token**  
   - Generates new token if user exists and is not active  
   - Does not reveal whether email exists

4. **Login**  
   - Requires active account  
   - Returns **JWT pair**: `access` + `refresh`

5. **Refresh access token**  
   - Uses refresh JWT  
   - Checks refresh token is not revoked and not expired

6. **Logout**  
   - Revokes refresh token (deletes it from DB), so it can’t be used again

### Movies (minimal catalog)
7. **Movies list**  
   - Pagination  
   - Search by title (basic)

### Shopping Cart (minimal)
8. **Cart management**
   - Add movie to cart (no duplicates)
   - Remove from cart
   - List cart items

> Note: Celery-beat cleanup of expired activation tokens is described in the roadmap. The current implementation focuses on core API flows for the FLEX scope.

---

## Project Structure

online-cinema/
pyproject.toml
README.md
.env.example
docker-compose.yml
Dockerfile
alembic.ini
alembic/
src/
main.py
app.py
config/
database/
models/
schemas/
security/
services/
api/
tests/
.github/workflows/ci.yml


---

## Requirements

- Docker + Docker Compose
- Python 3.12 (only if running without Docker)
- Poetry (only if running without Docker)

---

## Environment Variables

Create `.env` file from example:

```bash
cp .env.example .env
Example .env:

APP_ENV=dev
APP_HOST=0.0.0.0
APP_PORT=8000
APP_SECRET_KEY=dev-secret-change-me
ACCESS_TOKEN_TTL_MIN=15
REFRESH_TOKEN_TTL_DAYS=7

DATABASE_URL=postgresql+psycopg://cinema:cinema@db:5432/cinema
Run with Docker Compose (Recommended)
docker compose up --build
API will be available at:

http://localhost:8000

API Documentation (Swagger / OpenAPI)
Swagger UI: http://localhost:8000/docs

OpenAPI JSON: http://localhost:8000/openapi.json

Database Migrations (Alembic)
Inside container (or locally with Poetry):

alembic upgrade head
If running inside Docker container, open a shell:

docker compose exec app bash
Run Tests + Coverage
Locally via Poetry:

poetry install
pytest -q --cov=src --cov-report=term-missing
Or inside Docker container:

docker compose exec app pytest -q --cov=src --cov-report=term-missing
API Endpoints (Quick Reference)
Base prefix: /api/v1

Accounts
1) Register
POST /api/v1/accounts/register

Request:

{
  "email": "user@example.com",
  "password": "Passw0rd1"
}
Response:

{ "message": "Registration successful. Check email for activation." }
Activation token is sent using a dev mailer stub (printed to console).

2) Activate account
POST /api/v1/accounts/activate

Request:

{
  "token": "ACTIVATION_TOKEN_FROM_EMAIL"
}
Response:

{ "message": "Account activated." }
3) Resend activation
POST /api/v1/accounts/resend-activation

Request:

{
  "email": "user@example.com"
}
Response:

{ "message": "If the email exists, a new activation token was sent." }
4) Login
POST /api/v1/accounts/login

Request:

{
  "email": "user@example.com",
  "password": "Passw0rd1"
}
Response:

{
  "access": "ACCESS_JWT",
  "refresh": "REFRESH_JWT"
}
5) Refresh access token
POST /api/v1/accounts/refresh

Request:

{
  "refresh": "REFRESH_JWT"
}
Response:

{
  "access": "NEW_ACCESS_JWT",
  "refresh": "REFRESH_JWT"
}
6) Logout (revoke refresh token)
POST /api/v1/accounts/logout

Request:

{
  "refresh": "REFRESH_JWT"
}
Response:

{ "message": "Logged out." }
Development Notes
Password Complexity
Password must be:

at least 8 characters

contain letters and digits

CI (GitHub Actions)
On every push/PR to main, CI runs:

ruff check .

mypy src

pytest --cov

Roadmap (Not in FLEX scope yet)
Celery + Celery Beat periodic cleanup for expired activation tokens

Full Movies module:

likes/dislikes, comments, rating (1–10), favorites

filtering/sorting by imdb/year/price/popularity

Orders & Payments:

order creation from cart

Stripe payments + webhooks

payment history + refunds

Role-based access:

Moderator/Admin permissions for CRUD and analytics

Restrict Swagger docs for authorized users only

