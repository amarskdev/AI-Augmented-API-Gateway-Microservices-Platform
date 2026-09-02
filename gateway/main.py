from fastapi import FastAPI

app = FastAPI(
    title="AI-Augmented API Gateway",
    version="0.1.0",
    description=(
        "Gateway foundation for authentication, routing, rate limiting, and anomaly detection."
    ),
)


@app.get("/health", tags=["system"])
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/v1", tags=["system"])
async def api_root() -> dict[str, str]:
    return {"service": "api-gateway", "version": "v1"}
