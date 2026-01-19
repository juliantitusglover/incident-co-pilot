import logging
from typing import Annotated
from fastapi import Depends
from sqlalchemy import inspect, text
from backend.core.config import Settings, get_settings
from backend.db.sessions import engine

logger = logging.getLogger(__name__)

def is_database_ready(settings: Annotated[Settings, Depends(get_settings)]
) -> dict:
    """
    Verifies connectivity AND checks if the required tables exist.
    Useful for health-check endpoints or startup scripts.
    """
    results = {"status": "unhealthy", "connectivity": False, "tables_found": []}
    
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            results["connectivity"] = True
            
            inspector = inspect(engine)
            existing_tables = inspector.get_table_names()
            results["tables_found"] = existing_tables
            
            required = {"incidents", "timeline_events"}
            if required.issubset(set(existing_tables)):
                results["status"] = "healthy"
                
    except Exception as e:
        logger.error(f"Database readiness check failed: {e}", exc_info=True)

        if settings.DEBUG:
            results["error"] = str(e)
        else:
            results["error"] = "Internal database connection error"
        
    return results