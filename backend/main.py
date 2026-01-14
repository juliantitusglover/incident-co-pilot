from fastapi import FastAPI

from backend.api.routes import auth, health, incidents

app = FastAPI()

app.include_router(auth.router)
app.include_router(health.router)
app.include_router(incidents.router)
