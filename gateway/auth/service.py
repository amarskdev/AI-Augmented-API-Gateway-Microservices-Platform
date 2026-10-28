"""JWT authentication backed by an in-memory user store."""

from __future__ import annotations

import base64
import hashlib
import hmac
import os
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Final

import jwt

PASSWORD_ITERATIONS: Final = 310_000
JWT_ALGORITHM: Final = "HS256"
JWT_EXPIRATION_MINUTES: Final = 30


@dataclass(frozen=True, slots=True)
class User:
    username: str
    password_hash: str
    role: str
    disabled: bool = False


class UserNotFoundError(LookupError):
    """Raised when a username is not present in the user store."""


class InMemoryUserStore:
    """User repository used until the PostgreSQL integration is introduced."""

    def __init__(self, users: list[User] | None = None) -> None:
        self._users = {user.username: user for user in users or []}

    def get(self, username: str) -> User:
        try:
            return self._users[username]
        except KeyError as error:
            raise UserNotFoundError(username) from error

    def add(self, user: User) -> None:
        self._users[user.username] = user


def hash_password(password: str) -> str:
    """Hash a password with a per-password salt using PBKDF2-HMAC-SHA256."""
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, PASSWORD_ITERATIONS
    )
    return f"pbkdf2_sha256${PASSWORD_ITERATIONS}${_encode(salt)}${_encode(digest)}"


def verify_password(password: str, encoded_hash: str) -> bool:
    """Verify a password without exposing whether the password or user was wrong."""
    try:
        algorithm, iterations, salt, expected = encoded_hash.split("$")
        if algorithm != "pbkdf2_sha256":
            return False
        actual = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            _decode(salt),
            int(iterations),
        )
    except (TypeError, ValueError):
        return False
    return hmac.compare_digest(_encode(actual), expected)


class AuthService:
    def __init__(
        self,
        user_store: InMemoryUserStore,
        secret_key: str,
        expiration_minutes: int = JWT_EXPIRATION_MINUTES,
    ) -> None:
        if not secret_key:
            raise ValueError("JWT secret key must not be empty")
        if expiration_minutes <= 0:
            raise ValueError("JWT expiration must be positive")
        self.user_store = user_store
        self.secret_key = secret_key
        self.expiration_minutes = expiration_minutes

    def authenticate(self, username: str, password: str) -> User:
        try:
            user = self.user_store.get(username)
        except UserNotFoundError:
            raise ValueError("Invalid username or password") from None
        if user.disabled or not verify_password(password, user.password_hash):
            raise ValueError("Invalid username or password")
        return user

    def issue_token(self, user: User) -> str:
        now = datetime.now(timezone.utc)
        payload = {
            "sub": user.username,
            "role": user.role,
            "iat": now,
            "exp": now + timedelta(minutes=self.expiration_minutes),
        }
        return jwt.encode(payload, self.secret_key, algorithm=JWT_ALGORITHM)

    def decode_token(self, token: str) -> User:
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[JWT_ALGORITHM],
                options={"require": ["sub", "role", "exp"]},
            )
            username = payload["sub"]
            role = payload["role"]
            if not isinstance(username, str) or not isinstance(role, str):
                raise ValueError
            user = self.user_store.get(username)
        except (jwt.InvalidTokenError, KeyError, TypeError, ValueError, UserNotFoundError):
            raise ValueError("Invalid or expired token") from None
        if user.disabled or user.role != role:
            raise ValueError("Invalid or expired token")
        return user


def create_default_auth_service() -> AuthService:
    store = InMemoryUserStore(
        [
            User("admin", hash_password("admin123"), "admin"),
            User("user", hash_password("user123"), "user"),
        ]
    )
    return AuthService(
        store,
        os.getenv("JWT_SECRET_KEY", "local-development-secret"),
    )


def _encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode("ascii")


def _decode(value: str) -> bytes:
    return base64.urlsafe_b64decode(value.encode("ascii"))
