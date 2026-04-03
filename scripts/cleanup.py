"""
Cleanup Script
Removes old cloned projects to save storage
"""
import os
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta

DB_PATH = Path(__file__).parent.parent / "database" / "cloner.db"
CLONED_SITES_DIR = Path(__file__).parent.parent / "cloned_sites"
MAX_AGE_DAYS = 7

def cleanup():
    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()
    
    cutoff_date = datetime.now() - timedelta(days=MAX_AGE_DAYS)
    cutoff_str = cutoff_date.isoformat()
    
    c.execute("""
        DELETE FROM projects 
        WHERE created_at < ? AND status = 'completed'
    """, (cutoff_str,))
    
    deleted_count = c.rowcount
    conn.commit()
    conn.close()
    
    print(f"Cleaned up {deleted_count} old projects")

if __name__ == "__main__":
    cleanup()
