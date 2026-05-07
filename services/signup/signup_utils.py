"""Password hashing helpers (PBKDF2-HMAC-SHA256)."""
import hashlib
import hmac
import secrets

from configs.settings import get_settings


def hash_password(password: str) -> str:
    """Return `salt$digest` where digest is the hex PBKDF2 of (password, salt)."""
    iterations = get_settings().PASSWORD_HASH_ITERATIONS
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        iterations,
    ).hex()
    return f"{salt}${iterations}${digest}"


def verify_password(password: str, hashed_password: str) -> bool:
    """Verify `password` against a hash produced by :func:`hash_password`.

    Backwards-compatible with the legacy two-segment `salt$digest` format
    (which assumed 150_000 iterations)."""
    parts = hashed_password.split("$")
    if len(parts) == 3:
        salt, iterations_str, expected_digest = parts
        try:
            iterations = int(iterations_str)
        except ValueError:
            return False
    elif len(parts) == 2:
        salt, expected_digest = parts
        iterations = 150_000
    else:
        return False

    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        iterations,
    ).hex()
    return hmac.compare_digest(digest, expected_digest)
