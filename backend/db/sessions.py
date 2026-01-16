from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

from backend.core.config import get_settings
from backend.db.base import Base

engine = create_engine(
    get_settings().DATABASE_URL,
    echo=True,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autoflush=True, bind=engine)

def get_db() -> Generator[Session, None, None]:
    with SessionLocal() as session:
        yield session

def create_tables():
    Base.metadata.create_all(bind=engine)
