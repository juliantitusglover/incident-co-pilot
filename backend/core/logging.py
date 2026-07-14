from __future__ import annotations

import logging


LOG_FORMAT = "%(asctime)s %(levelname)s [%(name)s] %(message)s"


def configure_logging(level: str) -> None:
    resolved_level = _resolve_level(level)

    logging.basicConfig(format=LOG_FORMAT)
    backend_logger = logging.getLogger("backend")
    backend_logger.disabled = False
    backend_logger.setLevel(resolved_level)

    for logger_name, existing_logger in logging.Logger.manager.loggerDict.items():
        if logger_name.startswith("backend.") and isinstance(
            existing_logger,
            logging.Logger,
        ):
            existing_logger.disabled = False


def _resolve_level(level: str) -> int:
    normalized_level = level.upper()
    resolved_level = getattr(logging, normalized_level, logging.INFO)

    if isinstance(resolved_level, int):
        return resolved_level

    return logging.INFO
