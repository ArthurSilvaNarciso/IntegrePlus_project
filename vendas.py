from database import conectar
from produtos import listar_produtos

def registrar_venda(produto_id, cliente_id, quantidade, data):
    conn = conectar()
    cursor = conn.cursor()
    
    # Atualiza estoque
    cursor.execute('SELECT quantidade FROM produtos WHERE id = ?', (produto_id,))
    estoque = cursor.fetchone()[0]
    
    if estoque < quantidade:
        conn.close()
        return "Estoque insuficiente."
    
    cursor.execute('UPDATE produtos SET quantidade = quantidade - ? WHERE id = ?', (quantidade, produto_id))
    
    # Registra venda
    cursor.execute('''
        INSERT INTO vendas (produto_id, cliente_id, quantidade, data)
        VALUES (?, ?, ?, ?)
    ''', (produto_id, cliente_id, quantidade, data))
    
    conn.commit()
    conn.close()
    return "Venda registrada com sucesso."
