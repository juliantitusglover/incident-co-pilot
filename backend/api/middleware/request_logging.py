from __future__ import annotations

import logging
from time import perf_counter

from starlette.types import ASGIApp, Message, Receive, Scope, Send

logger = logging.getLogger("backend.api.request")


class RequestLoggingMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        start_time = perf_counter()
        status_code = 500

        async def send_with_status_capture(message: Message) -> None:
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message["status"]
            await send(message)

        try:
            await self.app(scope, receive, send_with_status_capture)
        except Exception:
            self._log_request(scope, status_code, start_time)
            raise

        self._log_request(scope, status_code, start_time)

    def _log_request(
        self,
        scope: Scope,
        status_code: int,
        start_time: float,
    ) -> None:
        duration_ms = (perf_counter() - start_time) * 1000
        request_id = scope.get("state", {}).get("request_id", "-")

        logger.info(
            "request completed request_id=%s method=%s path=%s "
            "status_code=%s duration_ms=%.2f",
            request_id,
            scope["method"],
            scope["path"],
            status_code,
            duration_ms,
        )
