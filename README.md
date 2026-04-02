# SnapShort

A serverless URL shortener with click analytics, built with FastAPI, AWS Lambda, DynamoDB, and PostgreSQL.

## Features

- **Anyone** can shorten a URL with `POST /links` (no login; random short code only).
- **Signed-in users** can use custom short codes, list their links, delete, and view analytics.
- Public redirect: visit short URL → redirect to original and record click
- User auth (register, login with JWT)
- Per-link analytics: total clicks, last 7/30 days, recent clicks (account owners only)

## Tech stack

- **API**: FastAPI, Mangum (Lambda)
- **Databases**: DynamoDB (links, redirects), PostgreSQL (users, click analytics)
- **Auth**: JWT (python-jose), bcrypt (passlib)
- **Deploy**: AWS SAM, GitHub Actions

## Quick start (local)

1. Clone and create a virtualenv (e.g. `python -m venv .venv`), activate it.
2. `pip install -r requirements.txt -r requirements-dev.txt`
3. Copy `.env.example` to `.env` and set at least `SECRET_KEY`, `DATABASE_URL`, `DYNAMODB_ENDPOINT_URL` (for DynamoDB Local).
4. `docker-compose up -d` then `make create-dynamo-local` and `make migrate`.
5. `make dev` — API at http://localhost:8080, docs at http://localhost:8080/docs.

## API overview

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | /auth/register | No | Register (email, password) |
| POST | /auth/token | No | Login (form: username, password) → JWT |
| POST | /links | Optional | Create short link (Bearer optional; custom code requires login) |
| GET | /links | Bearer | List my links |
| DELETE | /links/{code} | Bearer | Delete my link |
| GET | /{code} | No | Redirect to original URL |
| GET | /analytics/{code} | Bearer | Analytics for my link |
| GET | /health | No | Health check |

## Tests

```bash
make test
```

## Deployment

- **AWS**: See `docs/guide/aws_setup_guide.md` and `docs/guide/prod.md` (create S3 bucket, set GitHub Secrets, run `sam build --use-container` and `sam deploy`).
- **CI**: Push to `main` runs tests and deploys when secrets are configured. 

## License

MIT
