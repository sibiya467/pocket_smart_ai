
from datetime import datetime, timedelta, timezone

import jwt
from passlib.context import CryptContext

from app.config import settings


# ============================================================
# PASSWORD HASHING
# ============================================================

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    """
    Hash a user password using bcrypt.

    Bcrypt supports a maximum of 72 bytes.
    """

    if not isinstance(password, str):
        raise ValueError("Password must be a string")

    password_bytes = password.encode("utf-8")

    if len(password_bytes) > 72:
        raise ValueError(
            "Password must be 72 bytes or less"
        )

    return pwd_context.hash(password)


def verify_password(
    password: str,
    hashed_password: str
) -> bool:
    """
    Check whether the password matches the stored hash.
    """

    try:
        if not password or not hashed_password:
            return False

        return pwd_context.verify(
            password,
            hashed_password
        )

    except Exception:
        return False


# ============================================================
# JWT ACCESS TOKEN
# ============================================================

def create_access_token(
    subject: str,
    minutes: int = 1440
) -> str:
    """
    Create a JWT access token.

    Default expiration:
    1440 minutes = 24 hours
    """

    now = datetime.now(timezone.utc)

    payload = {
        "sub": str(subject),
        "iat": now,
        "exp": now + timedelta(minutes=minutes)
    }

    token = jwt.encode(
        payload,
        settings.secret_key,
        algorithm=ALGORITHM
    )

    return token


# ============================================================
# DECODE JWT TOKEN
# ============================================================

def decode_token(token: str) -> dict:
    """
    Decode and verify a JWT token.

    Raises an exception if the token is invalid
    or expired.
    """

    return jwt.decode(
        token,
        settings.secret_key,
        algorithms=[ALGORITHM]
    )

