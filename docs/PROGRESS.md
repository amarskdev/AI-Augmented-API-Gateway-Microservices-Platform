# Build Progress

This file records completed milestones and the next verified increment.

## Completed

### Milestone 0: Gateway foundation

- Initialized Python package metadata in `pyproject.toml`.
- Added a FastAPI application with `/health` and `/api/v1` endpoints.
- Added smoke tests for both endpoints.
- Added Docker Compose definitions for PostgreSQL, Redis, and Kafka.
- Added a container image definition and GitHub-ready README.

Validation: `2 passed` with the project development environment.

## Next

### Milestone 1: JWT authentication and RBAC

- Added an in-memory user store with PBKDF2 password hashing.
- Added JWT issuance and validation with expiration and role claims.
- Added `/auth/login`, `/api/v1/users/me`, and admin-only `/admin/status` endpoints.
- Added authentication contract tests covering invalid credentials, token validation, and role enforcement.

Validation: `6 passed` with the project development environment.

## Next

Replace the in-memory user store with PostgreSQL persistence while preserving the authentication service contract.
