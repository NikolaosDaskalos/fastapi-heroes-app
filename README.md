# FastAPI Heroes App

A small FastAPI backend for managing heroes and the missions assigned to them.
The app uses SQLModel with SQLite, JWT bearer authentication, bcrypt password
hashing, and pytest coverage for the API routes.

## What the App Provides

- User registration and login with JWT access tokens.
- A `/auth/me` endpoint for checking the current authenticated user.
- Hero CRUD endpoints.
- Mission CRUD endpoints linked to heroes.
- Admin-only delete operations.
- Pagination on hero and mission list endpoints with `skip` and `limit`.
- Automatic SQLite table creation on application startup.
- Interactive OpenAPI docs at `/docs` when the app is running.

## Project Structure

```text
app/
  main.py              FastAPI app setup, CORS, lifespan, router registration
  config.py            Environment-driven settings
  db.py                SQLModel engine and session dependency
  depedencies.py       Auth, admin, session, and pagination dependencies
  security.py          Password hashing and JWT helpers
  models/models.py     SQLModel table models
  routers/             Auth, heroes, and missions routes
  schemas/             Pydantic request and response schemas
tests/
  conftest.py          Test database and auth fixtures
  routers/             API route tests
requirements.txt       Direct Python dependencies for app code, local serving, and tests
heroes.db              Default local SQLite database file
```

Note: the dependency module is named `app/depedencies.py` in this repository.

## Requirements

- Python 3.11 or newer is recommended.
- `pip`
- A virtual environment

The `requirements.txt` file includes the direct dependencies needed to run the
API locally and execute the tests.

## Setup

From the project root:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Create a local environment file if you want to override defaults:

```bash
cp .env.example .env
```

At minimum, set a real secret key for non-test usage:

```env
SECRET_KEY=change-this-to-a-long-random-value
```

## Configuration

Settings are loaded from environment variables or `.env` by
`pydantic-settings`.

| Setting | Default | Purpose |
| --- | --- | --- |
| `DATABASE_URL` | `sqlite:///./heroes.db` | SQLModel database URL |
| `SECRET_KEY` | `123456789` | JWT signing key |
| `ALGORITHM` | `HS256` | JWT signing algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Access token lifetime |
| `CORS_ORIGINS` | `["http://localhost:3000", "http://localhost:5173"]` | Allowed browser origins |

For SQLite, the default database file is `heroes.db` in the project root. Tables
are created automatically during FastAPI startup.

## Run the API

After setup:

```bash
source .venv/bin/activate
python -m uvicorn app.main:app --reload
```

Then open:

- API root: `http://127.0.0.1:8000/`
- Swagger UI: `http://127.0.0.1:8000/docs`
- OpenAPI JSON: `http://127.0.0.1:8000/openapi.json`

The root endpoint returns:

```json
{"message": "FastAPI Heroes App", "docs": "/docs"}
```

## Authentication

Register a user:

```bash
curl -X POST http://127.0.0.1:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "test_user", "password": "12345678"}'
```

Register an admin user:

```bash
curl -X POST http://127.0.0.1:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "test_admin", "password": "12345678"}'
```

Any username containing `admin` is marked as an admin by the current
implementation.

Log in and save a token:

```bash
TOKEN=$(curl -s -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test_user&password=12345678" \
  | python -c "import sys, json; print(json.load(sys.stdin)['access_token'])")
```

Use the token:

```bash
curl http://127.0.0.1:8000/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

## Data Rules

Users:

- `username`: 3 to 50 characters.
- `password`: at least 8 characters.
- Leading and trailing whitespace is stripped on registration and login.
- Responses never include password hashes.

Heroes:

- `name`: 3 to 50 characters.
- `power`: 3 to 50 characters.
- `level`: 1 to 100, defaults to `1`.
- `active`: boolean, defaults to `true`.

Missions:

- `title`: at least 5 characters.
- `difficulty`: 1 to 10.
- `completed`: boolean, defaults to `false`.
- `hero_id`: must reference an existing hero when creating a mission.

Delete behavior:

- Deleting heroes and missions requires an admin token.
- A hero cannot be deleted while they have any incomplete mission.
- A hero can be deleted when all related missions are completed.

## Example Workflow

Create a hero:

```bash
curl -X POST http://127.0.0.1:8000/heroes \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Storm", "power": "Weather control", "level": 10, "active": true}'
```

List heroes:

```bash
curl "http://127.0.0.1:8000/heroes?skip=0&limit=20"
```

Create a mission:

```bash
curl -X POST http://127.0.0.1:8000/missions \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Protect city", "difficulty": 5, "completed": false, "hero_id": 1}'
```

Update a mission:

```bash
curl -X PATCH http://127.0.0.1:8000/missions/1 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Updated mission", "difficulty": 8, "completed": true}'
```

Delete with an admin token:

```bash
ADMIN_TOKEN=$(curl -s -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test_admin&password=12345678" \
  | python -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

curl -X DELETE http://127.0.0.1:8000/missions/1 \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

## Testing

Run all tests:

```bash
source .venv/bin/activate
python -m pytest
```

Run one test file:

```bash
python -m pytest tests/routers/test_auth.py
python -m pytest tests/routers/test_heroes.py
python -m pytest tests/routers/test_missions.py
```

The test suite uses an in-memory SQLite database through FastAPI dependency
overrides, so tests do not modify `heroes.db`.


## Development Notes

- The FastAPI lifespan handler creates database tables at startup.
- The app uses `OAuth2PasswordBearer` with `tokenUrl="auth/login"`.
- Login expects form data, not JSON, because it uses
  `OAuth2PasswordRequestForm`.
- JWT payloads use the username as the `sub` claim.
- Passwords are hashed with bcrypt through Passlib.
- CORS is enabled for local frontend origins on ports `3000` and `5173` by
  default.
