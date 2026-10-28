from fastapi import Depends, FastAPI, HTTPException, status
from pydantic import BaseModel

from gateway.auth import AuthService, User, create_default_auth_service
from gateway.auth import dependencies as auth_dependencies
from gateway.auth.dependencies import get_current_user, require_role

app = FastAPI(
    title="AI-Augmented API Gateway",
    version="0.1.0",
    description=(
        "Gateway foundation for authentication, routing, rate limiting, and anomaly detection."
    ),
)
auth_service: AuthService = create_default_auth_service()
auth_dependencies.auth_service = auth_service


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


@app.get("/health", tags=["system"])
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/v1", tags=["system"])
async def api_root() -> dict[str, str]:
    return {"service": "api-gateway", "version": "v1"}


@app.post("/auth/login", response_model=TokenResponse, tags=["authentication"])
async def login(request: LoginRequest) -> TokenResponse:
    try:
        user = auth_service.authenticate(request.username, request.password)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        ) from None
    return TokenResponse(access_token=auth_service.issue_token(user))


@app.get("/api/v1/users/me", tags=["users"])
async def current_user(user: User = Depends(get_current_user)) -> dict[str, str]:
    return {"username": user.username, "role": user.role}


@app.get("/admin/status", tags=["admin"])
async def admin_status(user: User = Depends(require_role("admin"))) -> dict[str, str]:
    return {"status": "ok", "username": user.username, "role": user.role}
