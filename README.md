# AI-Augmented API Gateway & Microservices Platform

An incremental backend platform that combines a FastAPI API gateway with JWT/RBAC authentication, Redis-backed rate limiting, gRPC service routing, Kafka events, and real-time anomaly detection.

This repository is being built milestone by milestone. Each milestone is kept runnable and documented so progress can be reviewed and pushed to GitHub independently.

## Current Status

**Milestone 0: repository and gateway foundation**

- FastAPI gateway application
- `GET /health` liveness endpoint
- Versioned `GET /api/v1` root endpoint
- Isolated Python development environment
- Automated smoke tests

The larger architecture and delivery roadmap are captured in [project.md](project.md).

## Quick Start

Requirements: Python 3.11+ and Docker Compose.

```bash
python3 -m venv .venv
.venv/bin/pip install -e '.[dev]'
.venv/bin/python -m pytest -q
.venv/bin/uvicorn gateway.main:app --reload
```

Then open `http://127.0.0.1:8000/docs` for the generated API documentation.

## Local Infrastructure

The planned local dependencies are defined in `docker-compose.yml`:

```bash
docker compose up -d postgres redis kafka
```

The gateway does not depend on those services yet; they will be connected in later milestones.

## Project Layout

```text
gateway/        FastAPI gateway and shared gateway modules
tests/          Automated tests
docs/           Architecture and milestone documentation
project.md      Full product specification and roadmap
```

## Roadmap

1. Gateway foundation and local infrastructure
2. JWT authentication and RBAC
3. gRPC contracts and downstream services
4. Gateway routing, Redis rate limiting, and GraphQL
5. Kafka events and analytics consumer
6. Anomaly detection and admin controls
7. Kubernetes, CI/CD, observability, and measured load testing

## Development Checks

```bash
.venv/bin/python -m pytest -q
.venv/bin/ruff check .
```

Measured performance claims will be added only after load tests produce the numbers.
