from database import get_connection, execute_query
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import tkinter as tk
from tkinter import ttk, messagebox
import produtos
import clientes
import pandas as pd
from decimal import Decimal

def registrar_venda(produto_id: int, quantidade: int, preco_unitario: float, 
                   cliente_id: Optional[int] = None, 
                   forma_pagamento: str = "Dinheiro") -> str:
    """Registra uma nova venda no sistema"""
    try:
        total = quantidade * preco_unitario
        
        # Verificar estoque
        estoque_query = 'SELECT quantidade FROM produtos WHERE id = ?'
        estoque_result = execute_query(estoque_query, (produto_id,), fetch=True)
        
        if not estoque_result or estoque_result[0]['quantidade'] < quantidade:
            return "Estoque insuficiente."
        
        # Registrar venda
        venda_query = '''
            INSERT INTO vendas (produto_id, quantidade, preco_unitario, total, 
                              data, cliente_id, forma_pagamento)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        '''
        execute_query(venda_query, (
            produto_id, quantidade, preco_unitario, total,
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 
            cliente_id, forma_pagamento
        ))
        
        # Atualizar estoque
        update_query = '''
            UPDATE produtos 
            SET quantidade = quantidade - ?,
                ultima_atualizacao = ?
            WHERE id = ?
        '''
        execute_query(update_query, (
            quantidade, 
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 
            produto_id
        ))
        
        return "Venda registrada com sucesso."
    except Exception as e:
        return f"Erro ao registrar venda: {str(e)}"

def listar_vendas() -> List[Dict]:
    """Retorna lista de todas as vendas com detalhes"""
    query = '''
        SELECT v.id, p.nome, v.quantidade, v.preco_unitario, v.total, 
               v.data, v.forma_pagamento, u.username as cliente
        FROM vendas v
        JOIN produtos p ON v.produto_id = p.id
        LEFT JOIN usuarios u ON v.cliente_id = u.id
        ORDER BY v.data DESC
    '''
    try:
        result = execute_query(query, fetch=True)
        return result if result else []
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao listar vendas: {str(e)}")
        return []

def exportar_vendas_excel(caminho: str = 'relatorio_vendas.xlsx') -> None:
    """Exporta todas as vendas para um arquivo Excel"""
    vendas = listar_vendas()
    if vendas:
        df = pd.DataFrame(vendas)
        df.to_excel(caminho, index=False)
        messagebox.showinfo("Exportação", 
                          f"Vendas exportadas com sucesso para '{caminho}'")
    else:
        messagebox.showinfo("Exportação", 
                          "Nenhuma venda encontrada para exportar")

def calcular_total_vendas_periodo(data_inicio: str, data_fim: str) -> float:
    """Calcula o total de vendas em um período específico"""
    query = '''
        SELECT SUM(total) FROM vendas
        WHERE data BETWEEN ? AND ?
    '''
    try:
        result = execute_query(query, (data_inicio, data_fim), fetch=True)
        return result[0]['SUM(total)'] if result and result[0]['SUM(total)'] else 0.0
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao calcular vendas: {str(e)}")
        return 0.0

def gui_registrar_venda(tela_cheia: bool = False) -> None:
    """Modernized interface gráfica para registrar vendas com cálculo de total e troco"""
    def salvar():
        try:
            produto_nome = combo_produto.get()
            cliente_nome = combo_cliente.get()
            quantidade = int(entry_quantidade.get())
            forma_pagamento = var_pagamento.get()
            
            # Buscar produto pelo nome para obter id e preço
            produtos_lista = produtos.listar_produtos()
            produto = next((p for p in produtos_lista if p[1] == produto_nome), None)
            if not produto:
                messagebox.showerror("Erro", "Produto não encontrado!")
                return
            
            produto_id = produto[0]
            preco_unitario = produto[3]
            estoque = produto[2]
            
            if estoque < quantidade:
                messagebox.showerror("Erro", "Quantidade insuficiente em estoque!")
                return
            
            # Buscar cliente pelo nome para obter id
            clientes_lista = clientes.listar_clientes()
            cliente = next((c for c in clientes_lista if c[1] == cliente_nome), None)
            cliente_id = cliente[0] if cliente else None
            
            total = quantidade * preco_unitario
            valor_pago = float(entry_valor_pago.get())
            troco = valor_pago - total
            
            if troco < 0:
                messagebox.showerror("Erro", "Valor pago insuficiente!")
                return
            
            resultado = registrar_venda(produto_id, quantidade, preco_unitario, 
                                       cliente_id, forma_pagamento)
            if resultado == "Venda registrada com sucesso.":
                messagebox.showinfo("Sucesso", f"{resultado}\nTroco: R$ {troco:.2f}")
                janela.destroy()
            else:
                messagebox.showerror("Erro", resultado)
            
        except ValueError:
            messagebox.showerror("Erro", "Por favor, insira valores válidos!")
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    janela = tk.Toplevel()
    janela.title("Registrar Venda")
    janela.geometry("800x600" if tela_cheia else "400x400")
    janela.configure(bg="#2c3e50")

    frame = tk.Frame(janela, bg="#34495e", pady=20, padx=20)
    frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

    # Combobox de produtos
    produtos_lista = produtos.listar_produtos()
    produtos_nomes = [p[1] for p in produtos_lista]

    tk.Label(frame, text="Produto:", bg="#34495e", fg="white", font=("Arial", 12)).pack(pady=5)
    combo_produto = ttk.Combobox(frame, values=produtos_nomes, font=("Arial", 12))
    combo_produto.pack(pady=5)

    # Combobox de clientes
    clientes_lista = clientes.listar_clientes()
    clientes_nomes = [c[1] for c in clientes_lista]

    tk.Label(frame, text="Cliente (opcional):", bg="#34495e", fg="white", font=("Arial", 12)).pack(pady=5)
    combo_cliente = ttk.Combobox(frame, values=clientes_nomes, font=("Arial", 12))
    combo_cliente.pack(pady=5)

    # Quantidade
    tk.Label(frame, text="Quantidade:", bg="#34495e", fg="white", font=("Arial", 12)).pack(pady=5)
    entry_quantidade = tk.Entry(frame, font=("Arial", 12))
    entry_quantidade.pack(pady=5)

    # Valor pago
    tk.Label(frame, text="Valor Pago (R$):", bg="#34495e", fg="white", font=("Arial", 12)).pack(pady=5)
    entry_valor_pago = tk.Entry(frame, font=("Arial", 12))
    entry_valor_pago.pack(pady=5)

    # Forma de pagamento
    tk.Label(frame, text="Forma de Pagamento:", bg="#34495e", fg="white", font=("Arial", 12)).pack(pady=5)
    var_pagamento = tk.StringVar(value="Dinheiro")
    opcoes = ["Dinheiro", "Cartão de Crédito", "Cartão de Débito", "PIX"]
    menu = ttk.OptionMenu(frame, var_pagamento, *opcoes)
    menu.pack(pady=5)

    # Botões
    tk.Button(frame, text="Registrar", command=salvar, bg="#27ae60", fg="white", font=("Arial", 12)).pack(pady=15)
    tk.Button(frame, text="Voltar", command=janela.destroy, bg="#34495e", fg="white", font=("Arial", 12)).pack(pady=5)

def gui_listar_vendas(tela_cheia: bool = False) -> None:
    """Interface gráfica para listar vendas"""
    janela = tk.Toplevel()
    janela.title("Histórico de Vendas")
    janela.geometry("1200x600" if tela_cheia else "800x400")

    frame_principal = tk.Frame(janela)
    frame_principal.pack(fill='both', expand=True)

    # Frame superior para filtros e botões
    frame_superior = tk.Frame(frame_principal, bg="#34495e", pady=10)
    frame_superior.pack(fill='x')

    # Botões de exportação e filtros
    tk.Button(frame_superior, text="Exportar Excel", 
              command=lambda: exportar_vendas_excel(),
              bg="#27ae60", fg="white").pack(side='left', padx=5)

    # TreeView para vendas
    colunas = ("ID", "Produto", "Quantidade", "Preço Unit.", "Total", 
               "Data", "Pagamento", "Cliente")
    tree = ttk.Treeview(frame_principal, columns=colunas, show='headings')
    
    for col in colunas:
        tree.heading(col, text=col)
        tree.column(col, anchor=tk.CENTER, width=150)
    
    # Scrollbar
    scrollbar = ttk.Scrollbar(frame_principal, orient="vertical", 
                             command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    
    scrollbar.pack(side="right", fill="y")
    tree.pack(fill='both', expand=True, padx=10, pady=10)

    # Carregar vendas
    for venda in listar_vendas():
        valores = (
            venda['id'],
            venda['produto'],
            venda['quantidade'],
            f"R$ {venda['preco_unitario']:.2f}",
            f"R$ {venda['total']:.2f}",
            venda['data'],
            venda['forma_pagamento'],
            venda['cliente'] or "N/A"
        )
        tree.insert('', 'end', values=valores)

    # Frame inferior para totais
    frame_inferior = tk.Frame(frame_principal, bg="#34495e", pady=10)
    frame_inferior.pack(fill='x')

    # Calcular e mostrar totais
    total_vendas = sum(v['total'] for v in listar_vendas())
    tk.Label(frame_inferior, 
             text=f"Total de Vendas: R$ {total_vendas:.2f}", 
             bg="#34495e", fg="white", 
             font=("Arial", 12, "bold")).pack(side='left', padx=10)

    tk.Button(frame_inferior, text="Voltar", 
              command=janela.destroy, 
              bg="#c0392b", fg="white").pack(side='right', padx=10)
