from database import conectar, criar_tabelas
import pandas as pd
from typing import List, Tuple
import tkinter as tk
from tkinter import messagebox, ttk

# Inicializar tabelas
criar_tabelas()

# ================= BANCO DE DADOS =================

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
            messagebox.showinfo("Exportação", f"Produtos exportados com sucesso para '{caminho}'.")
        else:
            messagebox.showinfo("Exportação", "Nenhum produto encontrado para exportar.")
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao exportar produtos: {e}")

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

# ================= INTERFACE GRÁFICA =================

def gui_cadastrar_produto(tela_cheia=False):
    def salvar():
        try:
            nome = entry_nome.get()
            quantidade = int(entry_quantidade.get())
            preco = float(entry_preco.get())
            validade = entry_validade.get()
            cadastrar_produto(nome, quantidade, preco, validade)
            messagebox.showinfo("Sucesso", "Produto cadastrado com sucesso!")
            janela.destroy()
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    janela = tk.Toplevel()
    janela.title("Cadastrar Produto")
    janela.geometry("800x600" if tela_cheia else "400x300")
    janela.configure(bg="#2c3e50")

    frame = tk.Frame(janela, bg="#34495e", pady=20, padx=20)
    frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

    campos = [
        ("Nome:", entry_nome := tk.Entry(frame, font=("Arial", 12), width=30)),
        ("Quantidade:", entry_quantidade := tk.Entry(frame, font=("Arial", 12), width=30)),
        ("Preço:", entry_preco := tk.Entry(frame, font=("Arial", 12), width=30)),
        ("Validade (dd/mm/aaaa):", entry_validade := tk.Entry(frame, font=("Arial", 12), width=30))
    ]

    for i, (label, entry) in enumerate(campos):
        tk.Label(frame, text=label, bg="#34495e", fg="white", font=("Arial", 12)).grid(row=i, column=0, padx=10, pady=8, sticky="e")
        entry.grid(row=i, column=1, padx=10, pady=8)

    tk.Button(frame, text="Salvar", command=salvar, bg="#27ae60", fg="white", font=("Arial", 12)).grid(row=len(campos), column=0, columnspan=2, pady=15)
    tk.Button(frame, text="Voltar", command=janela.destroy, bg="#34495e", fg="white", font=("Arial", 12)).grid(row=len(campos)+1, column=0, columnspan=2, pady=5)

def gui_listar_produtos(tela_cheia=False, parent=None):
    if parent:
        # Se parent for fornecido, criar dentro do frame pai
        for widget in parent.winfo_children():
            widget.destroy()
        
        tk.Label(parent, text="ESTOQUE ATUAL", bg="#2c3e50", fg="white", font=("Arial", 16, "bold")).pack(pady=10)
        
        colunas = ['ID', 'Nome', 'Qtd', 'Preço', 'Validade']
        tree = ttk.Treeview(parent, columns=colunas, show='headings', height=15)
        for col in colunas:
            tree.heading(col, text=col)
            tree.column(col, anchor=tk.CENTER, width=80)
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        for produto in listar_produtos():
            tree.insert('', tk.END, values=produto)
    else:
        # Criar janela separada
        janela = tk.Toplevel()
        janela.title("Estoque")
        janela.geometry("1000x600" if tela_cheia else "600x400")

        colunas = ['ID', 'Nome', 'Quantidade', 'Preço', 'Validade']
        tree = ttk.Treeview(janela, columns=colunas, show='headings')
        for col in colunas:
            tree.heading(col, text=col)
            tree.column(col, anchor=tk.CENTER, width=150)
        tree.pack(fill=tk.BOTH, expand=True)

        for produto in listar_produtos():
            tree.insert('', tk.END, values=produto)

        tk.Button(janela, text="Voltar", command=janela.destroy, bg="#34495e", fg="white", font=("Arial", 12)).pack(pady=10)

def gui_atualizar_produto(tela_cheia=False):
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
    janela.geometry("800x600" if tela_cheia else "400x350")
    janela.configure(bg="#2c3e50")

    frame = tk.Frame(janela, bg="#34495e", pady=20, padx=20)
    frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

    tk.Label(frame, text="ID do Produto:", bg="#34495e", fg="white", font=("Arial", 12)).grid(row=0, column=0, padx=5, pady=5)
    entry_id = tk.Entry(frame, font=("Arial", 12))
    entry_id.grid(row=0, column=1, padx=5, pady=5)
    tk.Button(frame, text="Buscar", command=buscar, bg="#3498db", fg="white", font=("Arial", 10)).grid(row=0, column=2, padx=5, pady=5)

    campos = [
        ("Nome:", entry_nome := tk.Entry(frame, font=("Arial", 12))),
        ("Quantidade:", entry_quantidade := tk.Entry(frame, font=("Arial", 12))),
        ("Preço:", entry_preco := tk.Entry(frame, font=("Arial", 12))),
        ("Validade:", entry_validade := tk.Entry(frame, font=("Arial", 12)))
    ]

    for i, (label, entry) in enumerate(campos, start=1):
        tk.Label(frame, text=label, bg="#34495e", fg="white", font=("Arial", 12)).grid(row=i, column=0, padx=5, pady=5)
        entry.grid(row=i, column=1, columnspan=2, padx=5, pady=5)

    tk.Button(frame, text="Atualizar", command=atualizar, bg="#27ae60", fg="white", font=("Arial", 12)).grid(row=6, column=0, columnspan=3, pady=15)
    tk.Button(frame, text="Voltar", command=janela.destroy, bg="#34495e", fg="white", font=("Arial", 12)).grid(row=7, column=0, columnspan=3, pady=5)

def gui_excluir_produto(tela_cheia=False):
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
    janela.geometry("500x300" if tela_cheia else "300x200")
    janela.configure(bg="#2c3e50")

    frame = tk.Frame(janela, bg="#34495e", pady=20, padx=20)
    frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

    tk.Label(frame, text="ID do Produto:", bg="#34495e", fg="white", font=("Arial", 14)).pack(pady=10)
    entry_id = tk.Entry(frame, font=("Arial", 14))
    entry_id.pack(pady=5)
    tk.Button(frame, text="Excluir", command=excluir, bg="#e74c3c", fg="white", font=("Arial", 14)).pack(pady=15)
    tk.Button(frame, text="Voltar", command=janela.destroy, bg="#34495e", fg="white", font=("Arial", 12)).pack(pady=5)