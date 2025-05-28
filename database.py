import sqlite3

DB_NAME = 'integre_plus.db'

def conectar():
    return sqlite3.connect(DB_NAME)

def criar_tabelas():
    with conectar() as conn:
        cursor = conn.cursor()

        # Tabela de usuários
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                senha BLOB NOT NULL,
                permissao TEXT DEFAULT 'Funcionario'
            )
        ''')

        # Tabela de produtos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS produtos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                quantidade INTEGER NOT NULL,
                preco REAL NOT NULL,
                validade TEXT
            )
        ''')

        conn.commit()
       