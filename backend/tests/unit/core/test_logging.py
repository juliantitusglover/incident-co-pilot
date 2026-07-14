import logging

from backend.core.logging import configure_logging


def test_configure_logging_applies_debug_to_backend_logger():
    configure_logging("debug")

    assert logging.getLogger("backend").level == logging.DEBUG


def test_configure_logging_falls_back_to_info_for_invalid_level():
    configure_logging("invalid")

    assert logging.getLogger("backend").level == logging.INFO
