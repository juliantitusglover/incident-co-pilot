import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from alembic.config import Config
from alembic import command

from backend.core.config import Settings
from backend.db.sessions import get_db

def override_get_settings():
    return Settings(
        DATABASE_URL="postgresql+psycopg2://jtg@localhost:5432/incident_co_pilot_test",
        OPENAI_API_KEY="test-key-not-real", 
        _env_file=None
    )

engine = create_engine(
    override_get_settings().DATABASE_URL,
    echo=True,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autoflush=True, bind=engine)

@pytest.fixture(scope="session")
def app_fixture():
    from backend.main import create_app 
    from backend.core.config import get_settings
    
    app = create_app()
    app.dependency_overrides[get_settings] = override_get_settings
    base_dir = os.path.dirname(os.path.abspath(__file__))
    ini_path = os.path.join(base_dir, "..", "alembic.ini")

    alembic_cfg = Config(ini_path)

    migrations_path = os.path.abspath(os.path.join(base_dir, "..", "db", "migrations"))

    alembic_cfg.set_main_option("script_location", migrations_path)
    alembic_cfg.set_main_option("sqlalchemy.url", override_get_settings().DATABASE_URL)

    command.upgrade(alembic_cfg, "head")

    yield app
    app.dependency_overrides = {}

@pytest.fixture
def client_fixture(app_fixture):
    yield TestClient(app_fixture)

@pytest.fixture
def db_session():
    connection = engine.connect()
    trans = connection.begin()
    with Session(bind=connection) as session:
        yield session
    trans.rollback()
    connection.close()

@pytest.fixture(autouse=True)
def db_setup(app_fixture, db_session):
    app_fixture.dependency_overrides[get_db] = lambda: db_session
    yield
    app_fixture.dependency_overrides.pop(get_db, None)

@pytest.fixture(scope="session")
def settings_fixture():
    return override_get_settings()