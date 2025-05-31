from database import conectar, criar_tabelas
import bcrypt
import sqlite3
from datetime import datetime, timedelta

def insert_test_data():
    try:
        # First create tables
        criar_tabelas()
        
        with conectar() as conn:
            cursor = conn.cursor()
            
            # Insert sample users
            usuarios = [
                ('joao.silva', 'senha123', 'Funcionario'),
                ('maria.santos', 'senha456', 'Admin'),
                ('pedro.souza', 'senha789', 'Funcionario')
            ]
            
            for username, senha, permissao in usuarios:
                hashed = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt())
                try:
                    cursor.execute('''
                        INSERT INTO usuarios (username, senha, permissao)
                        VALUES (?, ?, ?)
                    ''', (username, hashed, permissao))
                except sqlite3.IntegrityError:
                    print(f"Usuário {username} já existe, ignorando...")
            
            # Insert sample products
            hoje = datetime.now()
            validade = (hoje + timedelta(days=365)).strftime('%Y-%m-%d')
            data_cadastro = hoje.strftime('%Y-%m-%d %H:%M:%S')
            
            produtos = [
                ('Vinho Tinto', 50, 89.90, validade),
                ('Whey Protein', 30, 129.90, validade),
                ('Cerveja IPA', 100, 19.90, validade)
            ]
            
            cursor.executemany('''
                INSERT INTO produtos (nome, quantidade, preco, validade) 
                VALUES (?, ?, ?, ?)
            ''', produtos)
            
            # Insert sample sales
            vendas = []
            for i in range(15):  # Create 15 sample sales
                data = (hoje - timedelta(days=i)).strftime('%Y-%m-%d %H:%M:%S')
                cliente_id = (i % 3) + 1  # Rotate between users 1, 2, 3
                produto_id = (i % 3) + 1  # Rotate between products 1, 2, 3
                quantidade = (i % 5) + 1   # Quantities from 1 to 5
                preco_unitario = [89.90, 129.90, 19.90][produto_id - 1]  # Get price based on product
                total = quantidade * preco_unitario
                forma_pagamento = ['Dinheiro', 'Cartão de Crédito', 'PIX'][i % 3]
                
                vendas.append((
                    produto_id, quantidade, preco_unitario, total, data, 
                    cliente_id, forma_pagamento
                ))
            
            cursor.executemany('''
                INSERT INTO vendas (produto_id, quantidade, preco_unitario, total, 
                                  data, cliente_id, forma_pagamento) 
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', vendas)
            
            conn.commit()
            print("Test data inserted successfully!")
            
            # Verify the data
            print("\nVerifying inserted data:")
            print("\nUsuários:")
            cursor.execute('SELECT id, username, permissao FROM usuarios')
            print(cursor.fetchall())
            
            print("\nProdutos:")
            cursor.execute('SELECT id, nome, quantidade, preco FROM produtos')
            print(cursor.fetchall())
            
            print("\nVendas:")
            cursor.execute('''
                SELECT v.id, p.nome, v.quantidade, v.preco_unitario, v.total, v.data, v.forma_pagamento, u.username
                FROM vendas v
                JOIN produtos p ON v.produto_id = p.id
                LEFT JOIN usuarios u ON v.cliente_id = u.id
                ORDER BY v.data DESC
            ''')
            print(cursor.fetchall())
            
    except Exception as e:
        print(f"Error inserting test data: {e}")

if __name__ == "__main__":
    insert_test_data()
