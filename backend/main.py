from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.exception_handlers import register_exception_handlers
from backend.core.config import get_settings, Settings
from backend.api.routes import auth, health, incidents

def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()

    app = FastAPI(
        title=settings.API_TITLE,
        description=settings.API_DESCRIPTION,
        version=settings.API_VERSION,
    )

    register_exception_handlers(app)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(auth.router)
    app.include_router(health.router)
    app.include_router(incidents.router, prefix=settings.API_PREFIX)
    
    return app

app = create_app()
