import pytest


@pytest.fixture(autouse=True)
def _settings_env(monkeypatch):
    """Provide deterministic env vars for every test and reset the settings cache."""
    monkeypatch.setenv("JWT_SECRET_KEY", "test-secret")
    monkeypatch.setenv("JWT_ALGORITHM", "HS256")
    monkeypatch.setenv("JWT_EXPIRES_MINUTES", "60")
    monkeypatch.setenv("DATABASE_URL", "postgresql://test/test")
    monkeypatch.setenv("PASSWORD_HASH_ITERATIONS", "10000")

    from configs.settings import get_settings

    get_settings.cache_clear()
    yield
    get_settings.cache_clear()
