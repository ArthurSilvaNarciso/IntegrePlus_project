from database import conectar
import pandas as pd
from typing import List, Tuple
import tkinter as tk
from tkinter import messagebox, ttk

def cadastrar_produto(nome: str, quantidade: int, preco: float, validade: str) -> None:
    if not nome or quantidade < 0 or preco < 0:
        raise ValueError("Dados inválidos para cadastro de produto.")
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO produtos (nome, quantidade, preco, validade)
            VALUES (?, ?, ?, ?)
        ''', (nome, quantidade, preco, validade))
        conn.commit()

def listar_produtos() -> List[Tuple]:
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM produtos')
        return cursor.fetchall()

def atualizar_produto(produto_id: int, nome: str, quantidade: int, preco: float, validade: str) -> None:
    if not nome or quantidade < 0 or preco < 0:
        raise ValueError("Dados inválidos para atualização de produto.")
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE produtos 
            SET nome = ?, quantidade = ?, preco = ?, validade = ?
            WHERE id = ?
        ''', (nome, quantidade, preco, validade, produto_id))
        conn.commit()

def excluir_produto(produto_id: int) -> None:
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM produtos WHERE id = ?', (produto_id,))
        conn.commit()

def exportar_produtos_para_excel(caminho: str = 'produtos_exportados.xlsx') -> None:
    try:
        produtos = listar_produtos()
        if produtos:
            df = pd.DataFrame(produtos, columns=['ID', 'Nome', 'Quantidade', 'Preço', 'Validade'])
            df.to_excel(caminho, index=False)
            print(f"Produtos exportados para '{caminho}'.")
        else:
            print("Nenhum produto encontrado para exportar.")
    except Exception as e:
        print(f"Erro ao exportar produtos: {e}")

def buscar_produtos_por_nome(nome: str) -> List[Tuple]:
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM produtos WHERE nome LIKE ?", ('%' + nome + '%',))
        return cursor.fetchall()

def produtos_estoque_baixo(limite: int = 5) -> List[Tuple]:
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM produtos WHERE quantidade <= ?", (limite,))
        return cursor.fetchall()

# Funções de interface gráfica

def gui_cadastrar_produto():
    def salvar():
        nome = entry_nome.get()
        quantidade = entry_quantidade.get()
        preco = entry_preco.get()
        validade = entry_validade.get()
        try:
            cadastrar_produto(nome, int(quantidade), float(preco), validade)
            messagebox.showinfo("Sucesso", "Produto cadastrado com sucesso!")
            janela.destroy()
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    janela = tk.Toplevel()
    janela.title("Cadastrar Produto")

    tk.Label(janela, text="Nome:").grid(row=0, column=0, padx=5, pady=5)
    entry_nome = tk.Entry(janela)
    entry_nome.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(janela, text="Quantidade:").grid(row=1, column=0, padx=5, pady=5)
    entry_quantidade = tk.Entry(janela)
    entry_quantidade.grid(row=1, column=1, padx=5, pady=5)

    tk.Label(janela, text="Preço:").grid(row=2, column=0, padx=5, pady=5)
    entry_preco = tk.Entry(janela)
    entry_preco.grid(row=2, column=1, padx=5, pady=5)

    tk.Label(janela, text="Validade (dd/mm/aaaa):").grid(row=3, column=0, padx=5, pady=5)
    entry_validade = tk.Entry(janela)
    entry_validade.grid(row=3, column=1, padx=5, pady=5)

    tk.Button(janela, text="Salvar", command=salvar).grid(row=4, column=0, columnspan=2, pady=10)

def gui_listar_produtos():
    janela = tk.Toplevel()
    janela.title("Listar Produtos")

    colunas = ['ID', 'Nome', 'Quantidade', 'Preço', 'Validade']
    tree = ttk.Treeview(janela, columns=colunas, show='headings')
    for col in colunas:
        tree.heading(col, text=col)
        tree.column(col, width=100)
    tree.pack(fill=tk.BOTH, expand=True)

    for produto in listar_produtos():
        tree.insert('', tk.END, values=produto)

def gui_atualizar_produto():
    def buscar():
        try:
            produto_id = int(entry_id.get())
            with conectar() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM produtos WHERE id = ?", (produto_id,))
                produto = cursor.fetchone()
                if produto:
                    entry_nome.delete(0, tk.END)
                    entry_nome.insert(0, produto[1])
                    entry_quantidade.delete(0, tk.END)
                    entry_quantidade.insert(0, produto[2])
                    entry_preco.delete(0, tk.END)
                    entry_preco.insert(0, produto[3])
                    entry_validade.delete(0, tk.END)
                    entry_validade.insert(0, produto[4])
                else:
                    messagebox.showerror("Erro", "Produto não encontrado.")
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def atualizar():
        try:
            produto_id = int(entry_id.get())
            nome = entry_nome.get()
            quantidade = int(entry_quantidade.get())
            preco = float(entry_preco.get())
            validade = entry_validade.get()
            atualizar_produto(produto_id, nome, quantidade, preco, validade)
            messagebox.showinfo("Sucesso", "Produto atualizado com sucesso!")
            janela.destroy()
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    janela = tk.Toplevel()
    janela.title("Atualizar Produto")

    tk.Label(janela, text="ID do Produto:").grid(row=0, column=0, padx=5, pady=5)
    entry_id = tk.Entry(janela)
    entry_id.grid(row=0, column=1, padx=5, pady=5)

    tk.Button(janela, text="Buscar", command=buscar).grid(row=0, column=2, padx=5, pady=5)

    tk.Label(janela, text="Nome:").grid(row=1, column=0, padx=5, pady=5)
    entry_nome = tk.Entry(janela)
    entry_nome.grid(row=1, column=1, padx=5, pady=5)

    tk.Label(janela, text="Quantidade:").grid(row=2, column=0, padx=5, pady=5)
    entry_quantidade = tk.Entry(janela)
    entry_quantidade.grid(row=2, column=1, padx=5, pady=5)

    tk.Label(janela, text="Preço:").grid(row=3, column=0, padx=5, pady=5)
    entry_preco = tk.Entry(janela)
    entry_preco.grid(row=3, column=1, padx=5, pady=5)

    tk.Label(janela, text="Validade (dd/mm/aaaa):").grid(row=4, column=0, padx=5, pady=5)
    entry_validade = tk.Entry(janela)
    entry_validade.grid(row=4, column=1, padx=5, pady=5)

    tk.Button(janela, text="Atualizar", command=atualizar).grid(row=5, column=0, columnspan=3, pady=10)

def gui_excluir_produto():
    def excluir():
        try:
            produto_id = int(entry_id.get())
            excluir_produto(produto_id)
            messagebox.showinfo("Sucesso", "Produto excluído com sucesso!")
            janela.destroy()
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    janela = tk.Toplevel()
    janela.title("Excluir Produto")

    tk.Label(janela, text="ID do Produto:").grid(row=0, column=0, padx=5, pady=5)
    entry_id = tk.Entry(janela)
    entry_id.grid(row=0, column=1, padx=5, pady=5)

    tk.Button(janela, text="Excluir", command=excluir).grid(row=1, column=0, columnspan=2, pady=10)
