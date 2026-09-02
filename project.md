# Project 1: AI-Augmented API Gateway & Microservices Platform

**Target roles:** Senior Backend Engineer · Python Backend Developer · AI Engineer
**Estimated build time:** 5–7 weeks (part-time)

## 1. Problem Statement

Modern SaaS platforms route traffic through a gateway that must authenticate,
rate-limit, and route requests across multiple services — while staying resilient
under abuse or traffic spikes. This project builds that gateway from scratch and
adds an AI layer that detects abnormal traffic patterns (bot floods, credential
stuffing, scraping) in real time and reacts automatically, instead of relying on
static rate limits.

This directly demonstrates: HLD/LLD, event-driven architecture, gRPC, GraphQL,
Kubernetes, and applied AI/ML — skills currently listed on your resume with no
project evidence behind them.

## 2. Tech Stack

| Layer | Choice |
|---|---|
| Gateway / API layer | FastAPI (async, high-throughput) or Django + DRF |
| Inter-service comms | gRPC (protobuf-defined contracts) |
| Public query API | GraphQL (Strawberry or Ariadne) alongside REST |
| Event bus | Kafka |
| Cache / pub-sub | Redis |
| Database | PostgreSQL |
| AI/anomaly detection | Python (scikit-learn IsolationForest, or a lightweight LLM-scored classifier via OpenAI/local model) |
| Auth | JWT + RBAC |
| Containerization | Docker |
| Orchestration | Kubernetes (k3d/minikube locally, EKS-style manifests) |
| Observability | Prometheus + Grafana, or CloudWatch-style structured logging |
| CI/CD | GitHub Actions |

## 3. High-Level Design (HLD)

```
                     ┌─────────────────────┐
   Client ─────────▶ │   API Gateway (FastAPI) │
                     │  - JWT/RBAC auth        │
                     │  - Rate limiter (Redis)  │
                     │  - Anomaly scorer (AI)   │
                     └────────┬────────────────┘
                              │ gRPC
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
        Orders Service   Users Service   Notifications Service
              │               │               │
              └────────► Kafka Event Bus ◄────┘
                              │
                     Kafka Consumer (analytics)
                              │
                        PostgreSQL (audit/events)
```

**Key architectural decisions to document (for interviews):**
- Why gRPC internally vs REST internally (binary protocol, strict contracts, lower latency)
- Why GraphQL only at the public edge (avoids over-fetching for frontend clients)
- Why Kafka instead of direct service calls for audit/analytics events (decoupling, replay-ability)
- Sync vs async request paths — which endpoints go through Kafka vs direct gRPC

## 4. Low-Level Design (LLD)

### 4.1 Database Schema (PostgreSQL)

```sql
-- users
id UUID PK, email VARCHAR UNIQUE, password_hash VARCHAR,
role VARCHAR (admin/user/service), created_at TIMESTAMP

-- api_keys
id UUID PK, user_id FK, key_hash VARCHAR, scopes TEXT[],
rate_limit_tier VARCHAR, created_at TIMESTAMP, revoked_at TIMESTAMP NULL

-- request_logs (partitioned by day)
id BIGSERIAL PK, api_key_id FK, endpoint VARCHAR, method VARCHAR,
status_code INT, latency_ms INT, ip_address INET,
anomaly_score FLOAT, flagged BOOLEAN, created_at TIMESTAMP

-- anomaly_events
id UUID PK, request_log_id FK, reason VARCHAR, action_taken VARCHAR
(throttled/blocked/flagged_only), created_at TIMESTAMP
```

### 4.2 Core Modules

- `gateway/auth/` — JWT issuance, validation, RBAC middleware
- `gateway/rate_limiter/` — Redis token-bucket implementation, per-tier limits
- `gateway/anomaly/` — feature extraction (request rate, endpoint entropy, IP diversity) + IsolationForest scoring, retrained on a schedule
- `gateway/router/` — gRPC client stubs to downstream services
- `services/orders/`, `services/users/`, `services/notifications/` — minimal gRPC services with their own DB or in-memory store
- `analytics_consumer/` — Kafka consumer writing to `request_logs`

### 4.3 API Endpoints (Gateway public surface)

```
POST   /auth/login              -> JWT
POST   /auth/refresh
GET    /graphql                 -> GraphQL playground/endpoint
GET    /api/v1/orders/{id}      -> proxied to Orders service via gRPC
POST   /api/v1/orders
GET    /api/v1/users/me
GET    /admin/anomalies         -> list flagged requests (admin only)
POST   /admin/anomalies/{id}/resolve
```

### 4.4 Anomaly Detection Approach

1. Extract rolling features per API key: requests/min, unique endpoints hit,
   error rate, payload size variance.
2. Score with IsolationForest (unsupervised — good for "unknown unknowns" like
   novel bot behavior).
3. On high anomaly score: apply progressive response — soft throttle → hard
   throttle → temporary block, logged to `anomaly_events`.
4. Optional stretch: use an LLM to generate a human-readable explanation of
   *why* a request pattern was flagged, surfaced in the admin dashboard.

## 5. Build Roadmap

| Week | Milestone |
|---|---|
| 1 | Repo setup, Docker Compose (Postgres, Redis, Kafka), auth + RBAC |
| 2 | gRPC service contracts + 3 minimal downstream services |
| 3 | Gateway routing, rate limiter, GraphQL edge layer |
| 4 | Kafka event pipeline + analytics consumer |
| 5 | Anomaly detection model, feature pipeline, admin endpoints |
| 6 | Kubernetes manifests, CI/CD pipeline, observability dashboards |
| 7 | Load testing (Locust/k6), write-up, README, architecture diagrams |

## 6. Non-Functional Requirements to Demonstrate

- Load test to a stated number (e.g., "handled 2K concurrent requests with
  p99 latency under 200ms") — **measure this yourself, don't estimate.**
- Graceful degradation: if the anomaly service is down, gateway should fail
  open (not block all traffic).
- Zero-downtime deploy strategy documented (rolling update in K8s).

## 7. Testing Strategy

- Unit tests per module (pytest)
- Contract tests for gRPC services
- Load tests with Locust/k6, capture before/after latency numbers
- Chaos test: kill a downstream service pod, verify gateway handles it gracefully

## 8. Deployment / DevOps

- Dockerfile per service, multi-stage builds
- `k8s/` manifests: Deployments, Services, HPA (horizontal pod autoscaler)
- GitHub Actions: lint → test → build image → push → deploy
- Structured JSON logging, basic Grafana dashboard for request rate/latency/anomaly count

## 9. What to Put on GitHub

- Root `README.md` with architecture diagram (draw.io/excalidraw export as PNG)
- `docs/HLD.md` and `docs/LLD.md`
- Postman/Insomnia collection or `.http` file for the API
- A short demo GIF or Loom link showing the anomaly detection firing

## 10. Resume Bullet Templates (fill in with your real measured numbers)

- "Designed and built an AI-augmented API gateway handling [X] req/s with gRPC-based microservice routing, GraphQL edge layer, and Redis-backed rate limiting."
- "Implemented an unsupervised anomaly detection pipeline (IsolationForest) that flagged [X]% of abusive traffic patterns in load testing, reducing false-positive throttling by [X]% vs static rate limits."
- "Deployed the platform on Kubernetes with horizontal pod autoscaling and zero-downtime rolling updates, achieving [X]% uptime under simulated failure conditions."
