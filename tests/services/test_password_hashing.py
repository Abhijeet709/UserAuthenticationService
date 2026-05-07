from services.signup.signup_utils import hash_password, verify_password


def test_hash_password_produces_three_segment_format():
    hashed = hash_password("Password123")
    assert hashed.count("$") == 2  # salt$iterations$digest


def test_verify_password_accepts_correct_password():
    hashed = hash_password("Password123")
    assert verify_password("Password123", hashed) is True


def test_verify_password_rejects_wrong_password():
    hashed = hash_password("Password123")
    assert verify_password("password123", hashed) is False
    assert verify_password("Password1234", hashed) is False


def test_verify_password_supports_legacy_two_segment_format():
    """Hashes produced by the previous version (no embedded iteration count)
    must still verify correctly."""
    import hashlib
    import secrets

    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256", b"LegacyPass1", salt.encode(), 150_000
    ).hex()
    legacy = f"{salt}${digest}"

    assert verify_password("LegacyPass1", legacy) is True
    assert verify_password("wrong", legacy) is False


def test_verify_password_handles_malformed_input():
    assert verify_password("anything", "not-a-valid-hash") is False
    assert verify_password("anything", "") is False
