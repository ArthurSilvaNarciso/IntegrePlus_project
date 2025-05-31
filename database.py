"""
Database module for Integre+ application.
Handles database connections, schema management, and core database operations.
"""
import sqlite3
import logging
import logging.config
from datetime import datetime
import os
import shutil
from typing import Optional, List, Dict, Any, Union
from contextlib import contextmanager

from config import get_config

# Initialize logging
logging.config.dictConfig(get_config()['logging'])
logger = logging.getLogger(__name__)

class DatabaseError(Exception):
    """Base exception for database errors"""
    pass

class ConnectionError(DatabaseError):
    """Exception raised for database connection errors"""
    pass

class QueryError(DatabaseError):
    """Exception raised for query execution errors"""
    pass

@contextmanager
def get_connection():
    """
    Context manager for database connections.
    Ensures proper connection handling and error management.
    """
    config = get_config()
    conn = None
    try:
        conn = sqlite3.connect(config['db']['name'])
        conn.row_factory = sqlite3.Row  # Enable row factory for named columns
        yield conn
    except sqlite3.Error as e:
        logger.error(f"Database connection error: {e}")
        raise ConnectionError(f"Failed to connect to database: {e}")
    finally:
        if conn:
            conn.close()

def execute_query(query: str, params: tuple = None, fetch: bool = False) -> Union[List[Dict[str, Any]], None]:
    """
    Execute a SQL query with proper error handling and logging.
    
    Args:
        query: SQL query string
        params: Query parameters (optional)
        fetch: Whether to fetch and return results
    
    Returns:
        Query results if fetch=True, None otherwise
    
    Raises:
        QueryError: If query execution fails
    """
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            try:
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                
                if fetch:
                    columns = [description[0] for description in cursor.description]
                    results = cursor.fetchall()
                    # Convert Row objects to dictionaries
                    return [dict(zip(columns, row)) for row in results]
                
                conn.commit()
                return None
            except sqlite3.Error as e:
                conn.rollback()
                logger.error(f"Query execution error: {e}\nQuery: {query}\nParams: {params}")
                raise QueryError(f"Failed to execute query: {e}")
    except sqlite3.Error as e:
        logger.error(f"Query execution error: {e}\nQuery: {query}\nParams: {params}")
        raise QueryError(f"Failed to execute query: {e}")

def create_tables():
    """Create all database tables with proper constraints and indices"""
    queries = [
        # Products table
        """
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            quantidade INTEGER NOT NULL CHECK (quantidade >= 0),
            preco REAL NOT NULL CHECK (preco >= 0),
            validade TEXT NOT NULL,
            categoria TEXT,
            codigo_barras TEXT UNIQUE,
            fornecedor_id INTEGER,
            imagem BLOB,
            data_cadastro TEXT NOT NULL,
            ultima_atualizacao TEXT NOT NULL,
            FOREIGN KEY (fornecedor_id) REFERENCES fornecedores(id)
                ON DELETE SET NULL
                ON UPDATE CASCADE
        )
        """,
        
        # Price history table
        """
        CREATE TABLE IF NOT EXISTS historico_precos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            produto_id INTEGER NOT NULL,
            preco REAL NOT NULL CHECK (preco >= 0),
            data TEXT NOT NULL,
            FOREIGN KEY (produto_id) REFERENCES produtos(id)
                ON DELETE CASCADE
                ON UPDATE CASCADE
        )
        """,
        
        # Sales table
        """
        CREATE TABLE IF NOT EXISTS vendas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            produto_id INTEGER NOT NULL,
            quantidade INTEGER NOT NULL CHECK (quantidade > 0),
            preco_unitario REAL NOT NULL CHECK (preco_unitario >= 0),
            total REAL NOT NULL CHECK (total >= 0),
            data TEXT NOT NULL,
            cliente_id INTEGER,
            forma_pagamento TEXT NOT NULL,
            FOREIGN KEY (produto_id) REFERENCES produtos(id)
                ON DELETE RESTRICT
                ON UPDATE CASCADE,
            FOREIGN KEY (cliente_id) REFERENCES usuarios(id)
                ON DELETE SET NULL
                ON UPDATE CASCADE
        )
        """,
        
        # Suppliers table
        """
        CREATE TABLE IF NOT EXISTS fornecedores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            cnpj TEXT UNIQUE,
            telefone TEXT,
            email TEXT,
            endereco TEXT,
            data_cadastro TEXT NOT NULL
        )
        """,
        
        # Categories table
        """
        CREATE TABLE IF NOT EXISTS categorias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT UNIQUE NOT NULL,
            descricao TEXT
        )
        """,
        
        # Users table with role-based access
        """
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL,
            email TEXT UNIQUE,
            permissao TEXT NOT NULL DEFAULT 'Funcionario',
            ultimo_login TEXT,
            tentativas_login INTEGER DEFAULT 0,
            bloqueado INTEGER DEFAULT 0,
            data_cadastro TEXT NOT NULL,
            ultima_atualizacao TEXT NOT NULL
        )
        """,
        
        # Clients table
        """
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            cpf TEXT UNIQUE,
            email TEXT UNIQUE,
            telefone TEXT,
            endereco TEXT,
            data_cadastro TEXT NOT NULL,
            ultima_atualizacao TEXT NOT NULL
        )
        """,
        
        # User preferences table
        """
        CREATE TABLE IF NOT EXISTS preferencias_usuario (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER UNIQUE NOT NULL,
            tema TEXT DEFAULT 'light',
            notificacoes INTEGER DEFAULT 1,
            ultima_atualizacao TEXT NOT NULL,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
                ON DELETE CASCADE
                ON UPDATE CASCADE
        )
        """,
        
        # Audit log table
        """
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER,
            acao TEXT NOT NULL,
            tabela TEXT NOT NULL,
            registro_id INTEGER,
            dados_antigos TEXT,
            dados_novos TEXT,
            data TEXT NOT NULL,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
                ON DELETE SET NULL
                ON UPDATE CASCADE
        )
        """
    ]
    
    # Create indices for better performance
    indices = [
        "CREATE INDEX IF NOT EXISTS idx_produtos_nome ON produtos(nome)",
        "CREATE INDEX IF NOT EXISTS idx_produtos_categoria ON produtos(categoria)",
        "CREATE INDEX IF NOT EXISTS idx_vendas_data ON vendas(data)",
        "CREATE INDEX IF NOT EXISTS idx_vendas_cliente ON vendas(cliente_id)",
        "CREATE INDEX IF NOT EXISTS idx_historico_precos_produto ON historico_precos(produto_id)",
        "CREATE INDEX IF NOT EXISTS idx_audit_log_usuario ON audit_log(usuario_id)",
        "CREATE INDEX IF NOT EXISTS idx_audit_log_data ON audit_log(data)"
    ]
    
    try:
        for query in queries + indices:
            execute_query(query)
        logger.info("Database tables and indices created successfully")
    except QueryError as e:
        logger.error(f"Failed to create database schema: {e}")
        raise

def create_backup():
    """Create a backup of the database file"""
    config = get_config()
    try:
        # Ensure backup directory exists
        backup_dir = config['db']['backup_dir']
        os.makedirs(backup_dir, exist_ok=True)
        
        # Create backup filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = os.path.join(
            backup_dir, 
            f"backup_{os.path.basename(config['db']['name'])}_{timestamp}"
        )
        
        # Copy database file
        shutil.copy2(config['db']['name'], backup_file)
        logger.info(f"Database backup created: {backup_file}")
        return backup_file
    except Exception as e:
        logger.error(f"Failed to create database backup: {e}")
        raise DatabaseError(f"Backup creation failed: {e}")

def restore_backup(backup_file: str):
    """Restore database from a backup file"""
    config = get_config()
    try:
        # Verify backup file exists
        if not os.path.exists(backup_file):
            raise DatabaseError(f"Backup file not found: {backup_file}")
        
        # Create a backup of current database before restore
        create_backup()
        
        # Close all connections
        with get_connection() as conn:
            conn.close()
        
        # Restore from backup
        shutil.copy2(backup_file, config['db']['name'])
        logger.info(f"Database restored from backup: {backup_file}")
    except Exception as e:
        logger.error(f"Failed to restore database from backup: {e}")
        raise DatabaseError(f"Restore failed: {e}")

def log_audit(usuario_id: Optional[int], acao: str, tabela: str, 
              registro_id: Optional[int], dados_antigos: Optional[str], 
              dados_novos: Optional[str]):
    """Log an audit entry for database changes"""
    try:
        query = """
            INSERT INTO audit_log 
            (usuario_id, acao, tabela, registro_id, dados_antigos, dados_novos, data)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            usuario_id, acao, tabela, registro_id, 
            dados_antigos, dados_novos,
            datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )
        execute_query(query, params)
        logger.debug(f"Audit log created: {acao} on {tabela}")
    except QueryError as e:
        logger.error(f"Failed to create audit log: {e}")
        # Don't raise the error to avoid interrupting the main operation
        pass

# Initialize database
if __name__ == "__main__":
    create_tables()
