# Future Improvements

This project is a solid FastAPI learning app. The ideas below would make it
more production-ready, easier to maintain, and more useful as a backend service.

## Application Structure

- Split database models into separate files when the domain grows.
- Add a service layer for business rules, especially hero deletion and mission
  assignment.
- Add repository/helper functions for repeated SQLModel queries.
- Add application factories so tests and runtime configuration can create
  isolated app instances cleanly.

## Configuration

- Require `SECRET_KEY` in non-development environments instead of using the
  default `123456789`.
- Add explicit environment names such as `development`, `test`, and
  `production`.
- Document and validate CORS origins through `.env`.
- Add a separate test database URL setting.
- Add logging configuration through settings.

## Database

- Add Alembic migrations instead of relying only on `SQLModel.metadata.create_all`.
- Add indexes for frequently queried fields.
- Add cascading or restricted delete behavior intentionally for missions linked
  to heroes.
- Add created and updated timestamps to users, heroes, and missions.

## Authentication and Authorization

- Replace the current admin rule where any username containing `admin` becomes
  an admin.
- Add explicit role management.
- Add refresh tokens or a token renewal flow.
- Add password change and password reset flows.
- Add account uniqueness checks after trimming whitespace.
- Add stronger password policy rules.
- Add rate limiting on login and registration endpoints.

## API Behavior

- Make update schemas truly partial by using optional fields for PATCH requests.
- Add consistent response envelopes or keep the current direct JSON style and
  document it as a project decision.
- Add search and filtering for heroes and missions.
- Add sorting options to list endpoints.
- Add pagination metadata such as total count, page size, and next/previous
  links.
- Add mission reassignment from one hero to another.
- Add endpoints to list missions for a specific hero.
- Add support for marking a mission completed with a dedicated endpoint.

## Validation

- Normalize hero names, powers, and mission titles consistently.
- Prevent duplicate hero names if the product requires unique heroes.
- Validate that inactive heroes cannot receive new active missions, if that rule
  fits the domain.
- Add clearer error messages for validation failures.
- Add schemas that distinguish create, update, and response data more strictly.

## Testing

- Add unit tests for `security.py` and dependency helpers.
- Add tests for token expiry behavior.
- Add tests for malformed JWT payloads.
- Add tests for CORS configuration if browser clients are expected.
- Add tests for partial update behavior after update schemas are changed.
- Add tests around duplicate usernames with whitespace variants.
- Add integration tests that run against a temporary file-based SQLite database.
- Add coverage reporting.

## Developer Experience

- Add a `Makefile` or task runner with commands for setup, run, test, and lint.
- Add formatting and linting tools such as Ruff.
- Add type checking with mypy or pyright.
- Add pre-commit hooks.
- Add a `.python-version` or similar project runtime marker.
- Add example API requests in an HTTP collection file.

## Documentation

- Add a short architecture section explaining routers, schemas, models, and
  dependencies.
- Add a database schema diagram.
- Add sequence diagrams for registration, login, and authenticated requests.
- Add troubleshooting notes for common setup issues.
- Add sample `.env` values for local development.
- Add deployment instructions once a target platform is chosen.

## Production Readiness

- Add structured logging.
- Add request IDs for tracing.
- Add health and readiness endpoints.
- Add metrics instrumentation.
- Add error monitoring integration.
- Add Docker and Docker Compose files.
- Add CI to run tests and linting on every pull request.
- Add dependency vulnerability scanning.
- Add deployment configuration for the chosen hosting environment.
