import sqlite3

DB_NAME = 'integre_plus.db'

def conectar():
    return sqlite3.connect(DB_NAME)

def criar_tabelas():
    with conectar() as conn:
        cursor = conn.cursor()
        
        # Tabela de produtos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS produtos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                quantidade INTEGER NOT NULL,
                preco REAL NOT NULL,
                validade TEXT NOT NULL
            )
        ''')
        
        # Tabela de vendas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vendas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                produto_id INTEGER,
                quantidade INTEGER NOT NULL,
                data TEXT NOT NULL,
                FOREIGN KEY (produto_id) REFERENCES produtos (id)
            )
        ''')
        
        conn.commit()

# Inicializar banco de dados
if __name__ == "__main__":
    criar_tabelas()