from typing import Annotated
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.core.config import Settings, get_settings
from backend.api.routes import auth, health, incidents

def create_app() -> FastAPI:
    settings = get_settings() 

    app = FastAPI(
        title=settings.API_TITLE,
        description=settings.API_DESCRIPTION,
        version=settings.API_VERSION,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(auth.router)
    app.include_router(health.router)
    app.include_router(incidents.router)
    
    return app

app = create_app()
