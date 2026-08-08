from datetime import datetime, timedelta, UTC

from jose import JWTError, jwt

from app.core.config.settings import settings

def create_access_token(subject: str) -> str:
    """
    Create a JWT access token.
    """

    expire = datetime.now(UTC) + timedelta(
        minutes=settings.access_token_expire_minutes
    )

    payload = {
        "sub": subject,
        "exp": expire,
    }

    return jwt.encode(
        payload,
        settings.secret_key,
        algorithm=settings.algorithm,
    )


def verify_access_token(token: str) -> str | None:
    """
    Verify a JWT access token and return the subject.
    """

    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm],
        )

        return payload.get("sub")

    except JWTError:
        return None