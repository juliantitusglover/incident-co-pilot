import pytest
from fastapi import HTTPException, status

from backend.api.dependencies import require_api_key
from backend.core.config import Settings


def _settings(api_auth_enabled: bool, api_key: str = "configured-key") -> Settings:
    return Settings(
        _env_file=None,
        API_AUTH_ENABLED=api_auth_enabled,
        API_KEY=api_key,
    )


def test_auth_disabled_allows_missing_key():
    assert require_api_key(api_key=None, settings=_settings(False)) is None


def test_auth_disabled_allows_wrong_key():
    assert require_api_key(api_key="wrong-key", settings=_settings(False)) is None


def test_auth_enabled_allows_correct_key():
    assert (
        require_api_key(
            api_key="configured-key",
            settings=_settings(True),
        )
        is None
    )


def test_auth_enabled_rejects_missing_key():
    with pytest.raises(HTTPException) as exc_info:
        require_api_key(api_key=None, settings=_settings(True))

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc_info.value.detail == "Invalid or missing API key"


def test_auth_enabled_rejects_wrong_key():
    with pytest.raises(HTTPException) as exc_info:
        require_api_key(api_key="wrong-key", settings=_settings(True))

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc_info.value.detail == "Invalid or missing API key"


def test_auth_enabled_with_empty_configured_key_fails_safely():
    with pytest.raises(HTTPException) as exc_info:
        require_api_key(api_key="any-key", settings=_settings(True, api_key=""))

    assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert (
        exc_info.value.detail
        == "API authentication is enabled but API_KEY is not configured"
    )
