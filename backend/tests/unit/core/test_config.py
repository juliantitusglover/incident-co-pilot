from backend.core.config import Settings


def test_auth_settings_default_to_disabled():
    settings = Settings(_env_file=None)

    assert settings.API_AUTH_ENABLED is False
    assert settings.API_KEY == ""


def test_auth_settings_accept_explicit_overrides():
    settings = Settings(
        _env_file=None,
        API_AUTH_ENABLED=True,
        API_KEY="test-key",
    )

    assert settings.API_AUTH_ENABLED is True
    assert settings.API_KEY == "test-key"
