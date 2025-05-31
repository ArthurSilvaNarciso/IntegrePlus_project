from database import conectar

def migrate_clientes_table():
    with conectar() as conn:
        cursor = conn.cursor()
        
        # Create clientes table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                cpf TEXT UNIQUE,
                email TEXT,
                telefone TEXT,
                endereco TEXT,
                data_cadastro TEXT
            )
        ''')
        
        # Check if we need to modify the vendas table to reference clientes
        cursor.execute("PRAGMA foreign_keys = ON")
        
        # Check if foreign key constraint exists
        cursor.execute('''
            SELECT sql FROM sqlite_master 
            WHERE type='table' AND name='vendas'
        ''')
        vendas_schema = cursor.fetchone()[0]
        
        if 'FOREIGN KEY' not in vendas_schema:
            print("Adding foreign key constraints to vendas table...")
            # Create new vendas table with constraints
            cursor.execute('''
                CREATE TABLE vendas_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    produto_id INTEGER,
                    quantidade INTEGER NOT NULL,
                    preco_unitario REAL NOT NULL,
                    total REAL NOT NULL,
                    data TEXT NOT NULL,
                    cliente_id INTEGER,
                    forma_pagamento TEXT,
                    FOREIGN KEY (produto_id) REFERENCES produtos (id),
                    FOREIGN KEY (cliente_id) REFERENCES clientes (id)
                )
            ''')
            
            # Copy data from old to new table
            cursor.execute('''
                INSERT INTO vendas_new (
                    id, produto_id, quantidade, preco_unitario, 
                    total, data, cliente_id, forma_pagamento
                )
                SELECT id, produto_id, quantidade, preco_unitario, 
                       total, data, cliente_id, forma_pagamento
                FROM vendas
            ''')
            
            # Drop old table and rename new one
            cursor.execute('DROP TABLE vendas')
            cursor.execute('ALTER TABLE vendas_new RENAME TO vendas')
            print("Vendas table updated with foreign key constraints.")
        
        # Insert some sample clients if table is empty
        cursor.execute('SELECT COUNT(*) FROM clientes')
        if cursor.fetchone()[0] == 0:
            print("Inserting sample clients...")
            sample_clients = [
                ('João Silva', '123.456.789-00', 'joao@email.com', '(11) 99999-9999', 'Rua A, 123'),
                ('Maria Santos', '987.654.321-00', 'maria@email.com', '(11) 88888-8888', 'Av B, 456'),
                ('Pedro Souza', '456.789.123-00', 'pedro@email.com', '(11) 77777-7777', 'Rua C, 789')
            ]
            cursor.executemany('''
                INSERT INTO clientes (nome, cpf, email, telefone, endereco)
                VALUES (?, ?, ?, ?, ?)
            ''', sample_clients)
            print("Sample clients inserted.")
        
        conn.commit()
        print("Migration completed successfully!")

if __name__ == "__main__":
    migrate_clientes_table()
