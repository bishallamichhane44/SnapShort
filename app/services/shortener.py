import secrets
import string

from app.config import settings

ALPHABET = string.ascii_letters + string.digits


def generate_short_code(length: int | None = None) -> str:
    """Generate a cryptographically random URL-safe short code."""
    if length is None:
        length = settings.SHORT_CODE_LENGTH
    return "".join(secrets.choice(ALPHABET) for _ in range(length))
