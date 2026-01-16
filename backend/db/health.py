from sqlalchemy import inspect, text
from backend.db.sessions import engine

def is_database_ready() -> dict:
    """
    Verifies connectivity AND checks if the required tables exist.
    Useful for health-check endpoints or startup scripts.
    """
    results = {"status": "unhealthy", "connectivity": False, "tables_found": []}
    
    try:
        with engine.connect() as conn:
            # 1. Check Connection
            conn.execute(text("SELECT 1"))
            results["connectivity"] = True
            
            # 2. Check Schema (Readiness)
            inspector = inspect(engine)
            existing_tables = inspector.get_table_names()
            results["tables_found"] = existing_tables
            
            # Validate if your specific tables are there
            required = {"incidents", "timeline_events"}
            if required.issubset(set(existing_tables)):
                results["status"] = "healthy"
                
    except Exception as e:
        results["error"] = str(e)
        
    return results