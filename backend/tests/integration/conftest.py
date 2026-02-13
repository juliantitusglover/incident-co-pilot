import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from alembic.config import Config
from alembic import command

from backend.db.sessions import get_db

@pytest.fixture(scope="session")
def engine(settings_fixture):
    eng = create_engine(
        settings_fixture.DATABASE_URL,
        echo=False,
        pool_pre_ping=True
    )

    yield eng
    eng.dispose()

@pytest.fixture(scope="session")
def apply_migrations(settings_fixture):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    ini_path = os.path.join(base_dir, "..", "..", "alembic.ini")

    alembic_cfg = Config(ini_path)

    migrations_path = os.path.abspath(os.path.join(base_dir, "..", "..", "db", "migrations"))

    alembic_cfg.set_main_option("script_location", migrations_path)
    alembic_cfg.set_main_option("sqlalchemy.url", settings_fixture.DATABASE_URL)

    command.upgrade(alembic_cfg, "head")

@pytest.fixture
def db_session(engine, apply_migrations):
    connection = engine.connect()
    trans = connection.begin()
    session = Session(bind=connection, join_transaction_mode="create_savepoint")

    try:
        yield session
    finally:
        session.close()
        if trans.is_active:
            trans.rollback()
        connection.close()

@pytest.fixture(autouse=True)
def db_setup(app_fixture, db_session):
    app_fixture.dependency_overrides[get_db] = lambda: db_session
    yield
    app_fixture.dependency_overrides.pop(get_db, None)