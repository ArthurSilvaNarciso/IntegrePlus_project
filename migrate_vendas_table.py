from database import conectar

def migrate_vendas_table():
    with conectar() as conn:
        cursor = conn.cursor()
        # Check columns in vendas table
        cursor.execute("PRAGMA table_info(vendas)")
        columns = [col[1] for col in cursor.fetchall()]
        if 'preco_unitario' not in columns:
            print("Adding preco_unitario column to vendas table...")
            cursor.execute("ALTER TABLE vendas ADD COLUMN preco_unitario REAL NOT NULL DEFAULT 0")
            conn.commit()
            print("Added preco_unitario column.")
        else:
            print("preco_unitario column already exists.")
        if 'total' not in columns:
            print("Adding total column to vendas table...")
            cursor.execute("ALTER TABLE vendas ADD COLUMN total REAL NOT NULL DEFAULT 0")
            conn.commit()
            print("Added total column.")
        else:
            print("total column already exists.")
        if 'cliente_id' not in columns:
            print("Adding cliente_id column to vendas table...")
            cursor.execute("ALTER TABLE vendas ADD COLUMN cliente_id INTEGER")
            conn.commit()
            print("Added cliente_id column.")
        else:
            print("cliente_id column already exists.")
        if 'forma_pagamento' not in columns:
            print("Adding forma_pagamento column to vendas table...")
            cursor.execute("ALTER TABLE vendas ADD COLUMN forma_pagamento TEXT")
            conn.commit()
            print("Added forma_pagamento column.")
        else:
            print("forma_pagamento column already exists.")

if __name__ == "__main__":
    migrate_vendas_table()
