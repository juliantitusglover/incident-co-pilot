from __future__ import annotations

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse, PlainTextResponse

from backend.api.middleware import REQUEST_ID_HEADER
from backend.services.errors import NotFoundError, ValidationError


def _json_detail(status_code: int, detail: str) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"detail": detail})

def _request_id_headers(request: Request) -> dict[str, str]:
    request_id = getattr(request.state, "request_id", None)
    return {REQUEST_ID_HEADER: request_id} if request_id else {}

def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(NotFoundError)
    async def not_found_handler(request: Request, exc: NotFoundError) -> JSONResponse:
        return _json_detail(status.HTTP_404_NOT_FOUND, str(exc))

    @app.exception_handler(ValidationError)
    async def validation_handler(request: Request, exc: ValidationError) -> JSONResponse:
        return _json_detail(status.HTTP_400_BAD_REQUEST, str(exc))

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request,
        exc: Exception,
    ) -> PlainTextResponse:
        return PlainTextResponse(
            "Internal Server Error",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            headers=_request_id_headers(request),
        )
