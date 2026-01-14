from fastapi import FastAPI

from backend.core.config import get_settings
from backend.api.routes import auth, health, incidents

app = FastAPI(
    title=get_settings().API_TITLE,
    description=get_settings().API_DESCRIPTION,
    version=get_settings().API_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.include_router(auth.router)
app.include_router(health.router)
app.include_router(incidents.router)
