from sqlalchemy import text

def test_db_starts_clean(db_session):
    count = db_session.execute(text("SELECT COUNT(*) FROM incidents")).scalar_one()
    assert count == 0

def test_db_write_is_visible_within_test_only(db_session):
    db_session.execute(
        text(
            """
            INSERT INTO incidents (title, description, severity, status, created_at, updated_at)
            VALUES ('Isolation Test', 'Should rollback', 'SEV2', 'OPEN', NOW(), NOW())
            """
        )
    )

    count = db_session.execute(text("SELECT COUNT(*) FROM incidents")).scalar_one()
    assert count == 1

def test_db_is_clean_again_in_next_test(db_session):
    count = db_session.execute(text("SELECT COUNT(*) FROM incidents")).scalar_one()
    assert count == 0