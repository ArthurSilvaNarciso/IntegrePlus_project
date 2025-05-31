import sqlite3
import logging
from database import execute_query

logger = logging.getLogger(__name__)

def migrate_usuarios_table():
    """
    Migrate the usuarios table to include new security and user management fields
    """
    try:
        # Backup existing data
        backup_query = '''
        CREATE TABLE IF NOT EXISTS usuarios_backup AS 
        SELECT * FROM usuarios
        '''
        execute_query(backup_query)
        logger.info("Created backup of usuarios table")

        # Drop existing table
        drop_query = 'DROP TABLE IF EXISTS usuarios'
        execute_query(drop_query)
        logger.info("Dropped old usuarios table")

        # Create new table with updated schema
        create_query = '''
        CREATE TABLE usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE,
            senha BLOB NOT NULL,
            permissao TEXT DEFAULT 'Funcionario',
            data_criacao TEXT NOT NULL,
            ultimo_login TEXT,
            tentativas_login INTEGER DEFAULT 0,
            bloqueado INTEGER DEFAULT 0,
            token_reset TEXT,
            expiracao_token TEXT
        )
        '''
        execute_query(create_query)
        logger.info("Created new usuarios table with updated schema")

        # Migrate existing data
        migrate_query = '''
        INSERT INTO usuarios (username, senha, permissao, data_criacao)
        SELECT 
            username,
            senha,
            'Funcionario' as permissao,
            DATETIME('now') as data_criacao
        FROM usuarios_backup
        '''
        execute_query(migrate_query)
        logger.info("Migrated existing data to new table")

        # Drop backup table
        drop_backup_query = 'DROP TABLE IF EXISTS usuarios_backup'
        execute_query(drop_backup_query)
        logger.info("Dropped backup table")

        # Create default admin user if none exists
        insert_admin_query = '''
        INSERT OR IGNORE INTO usuarios (
            username,
            email,
            senha,
            permissao,
            data_criacao
        ) VALUES (
            'admin',
            'admin@example.com',
            ?,
            'Admin',
            DATETIME('now')
        )
        '''
        import bcrypt
        admin_password = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt())
        execute_query(insert_admin_query, (admin_password,))
        logger.info("Created default admin user if not exists")

        return True

    except Exception as e:
        logger.error(f"Error migrating usuarios table: {str(e)}")
        # Restore from backup if something went wrong
        try:
            execute_query('DROP TABLE IF EXISTS usuarios')
            execute_query('ALTER TABLE usuarios_backup RENAME TO usuarios')
            logger.info("Restored from backup after error")
        except Exception as restore_error:
            logger.error(f"Error restoring from backup: {str(restore_error)}")
        return False

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    if migrate_usuarios_table():
        print("Migration completed successfully")
    else:
        print("Migration failed")
