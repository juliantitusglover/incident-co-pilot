from sqlalchemy import inspect

def test_required_tables_exist(engine, apply_migrations):
    inspector = inspect(engine)
    tables = set(inspector.get_table_names())

    assert "incidents" in tables
    assert "timeline_events" in tables