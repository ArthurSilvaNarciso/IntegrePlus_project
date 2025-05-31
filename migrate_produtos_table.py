"""
Migration script to add missing columns to produtos table
"""
import sqlite3
from database import execute_query
import logging

logger = logging.getLogger(__name__)

def migrate_produtos_table():
    """Add missing columns to produtos table"""
    try:
        # Add categoria column if it doesn't exist
        execute_query("""
            ALTER TABLE produtos 
            ADD COLUMN categoria TEXT DEFAULT 'Outros'
        """)
        logger.info("Successfully added categoria column to produtos table")

        # Add codigo_barras column if it doesn't exist
        execute_query("""
            ALTER TABLE produtos 
            ADD COLUMN codigo_barras TEXT
        """)
        logger.info("Successfully added codigo_barras column to produtos table")

        # Add fornecedor column if it doesn't exist
        execute_query("""
            ALTER TABLE produtos 
            ADD COLUMN fornecedor TEXT
        """)
        logger.info("Successfully added fornecedor column to produtos table")

        return True
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            logger.info("Column already exists in produtos table")
            return True
        logger.error(f"Error adding columns: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during migration: {e}")
        return False

if __name__ == "__main__":
    migrate_produtos_table()
