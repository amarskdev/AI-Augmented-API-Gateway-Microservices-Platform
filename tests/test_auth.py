from fastapi.testclient import TestClient

from gateway.main import app

client = TestClient(app)


def login(username: str, password: str) -> str:
    response = client.post(
        "/auth/login",
        json={"username": username, "password": password},
    )
    assert response.status_code == 200
    return response.json()["access_token"]


def test_login_issues_jwt_and_returns_current_user() -> None:
    token = login("user", "user123")

    response = client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json() == {"username": "user", "role": "user"}


def test_invalid_credentials_are_rejected() -> None:
    response = client.post(
        "/auth/login",
        json={"username": "user", "password": "wrong"},
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid username or password"}


def test_protected_endpoint_requires_authentication() -> None:
    response = client.get("/api/v1/users/me")

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


def test_admin_endpoint_enforces_role() -> None:
    user_token = login("user", "user123")
    admin_token = login("admin", "admin123")

    forbidden = client.get(
        "/admin/status",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    allowed = client.get(
        "/admin/status",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert forbidden.status_code == 403
    assert allowed.status_code == 200
    assert allowed.json() == {"status": "ok", "username": "admin", "role": "admin"}
