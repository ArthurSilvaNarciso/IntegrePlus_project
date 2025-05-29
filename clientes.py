import sqlite3
import bcrypt
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Optional, Dict, List

DB_NAME = 'integre_plus.db'

def conectar() -> sqlite3.Connection:
    return sqlite3.connect(DB_NAME)

def criar_tabela_usuarios() -> None:
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                senha BLOB NOT NULL,
                permissao TEXT DEFAULT 'Funcionario'
            )
        ''')
        conn.commit()

def cadastrar_usuario(username: str, senha: str, permissao: str = 'Funcionario') -> None:
    criar_tabela_usuarios()
    hashed = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt())
    with conectar() as conn:
        try:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO usuarios (username, senha, permissao)
                VALUES (?, ?, ?)
            ''', (username, hashed, permissao))
            conn.commit()
        except sqlite3.IntegrityError:
            raise Exception("Usuário já existe. Escolha outro nome de usuário.")

def autenticar_usuario(username: str, senha: str) -> Optional[Dict[str, str]]:
    criar_tabela_usuarios()
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id, username, senha, permissao FROM usuarios WHERE username = ?', (username,))
        resultado = cursor.fetchone()
        if resultado and bcrypt.checkpw(senha.encode('utf-8'), resultado[2]):
            return {
                "id": resultado[0],
                "username": resultado[1],
                "permissao": resultado[3]
            }
    return None

def listar_usuarios() -> List[tuple]:
    criar_tabela_usuarios()
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id, username, permissao FROM usuarios')
        return cursor.fetchall()

def listar_clientes() -> List[tuple]:
    # Função compatível com relatórios - retorna usuários como clientes
    return listar_usuarios()

# === GUI ===

def voltar(janela):
    janela.destroy()

def gui_cadastrar_cliente(tela_cheia=True):
    def salvar_cliente():
        nome = entry_nome.get().strip()
        senha = entry_senha.get().strip()
        permissao = var_permissao.get()
        if not nome or not senha:
            messagebox.showerror("Erro", "Preencha todos os campos.")
            return
        try:
            cadastrar_usuario(nome, senha, permissao)
            messagebox.showinfo("Sucesso", "Cliente cadastrado com sucesso.")
            janela.destroy()
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    janela = tk.Toplevel()
    janela.title("Cadastrar Cliente")
    janela.geometry("800x600" if tela_cheia else "400x350")
    janela.configure(bg="#1e1e1e")

    frame = tk.Frame(janela, bg="#1e1e1e")
    frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

    campos = [
        ("Nome de Usuário", entry_nome := tk.Entry(frame, font=("Arial", 14))),
        ("Senha", entry_senha := tk.Entry(frame, show='*', font=("Arial", 14)))
    ]

    for texto, entry in campos:
        tk.Label(frame, text=texto, bg="#1e1e1e", fg="white", font=("Arial", 14)).pack(pady=5)
        entry.pack(pady=5)

    tk.Label(frame, text="Permissão", bg="#1e1e1e", fg="white", font=("Arial", 14)).pack(pady=5)
    var_permissao = tk.StringVar(value="Funcionario")
    menu = tk.OptionMenu(frame, var_permissao, "Funcionario", "Admin")
    menu.config(font=("Arial", 12))
    menu.pack(pady=5)

    tk.Button(frame, text="Cadastrar", command=salvar_cliente, bg="#27ae60", fg="white", font=("Arial", 14)).pack(pady=10)
    tk.Button(frame, text="Voltar", command=lambda: voltar(janela), bg="#34495e", fg="white", font=("Arial", 12)).pack(pady=5)

def gui_listar_clientes(tela_cheia=True):
    janela = tk.Toplevel()
    janela.title("Listar Clientes")
    janela.geometry("800x600" if tela_cheia else "500x400")

    tree = ttk.Treeview(janela, columns=("ID", "Usuário", "Permissão"), show='headings')
    for col in ("ID", "Usuário", "Permissão"):
        tree.heading(col, text=col)
        tree.column(col, anchor=tk.CENTER, width=150)
    tree.pack(fill='both', expand=True, padx=10, pady=10)

    for row in listar_usuarios():
        tree.insert('', 'end', values=row)

    tk.Button(janela, text="Voltar", command=lambda: voltar(janela), bg="#34495e", fg="white", font=("Arial", 12)).pack(pady=10)

def gui_excluir_cliente(tela_cheia=True):
    def excluir():
        id_user = entry_id.get()
        if not id_user.isdigit():
            messagebox.showerror("Erro", "ID inválido.")
            return
        with conectar() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM usuarios WHERE id = ?", (id_user,))
            conn.commit()
            if cursor.rowcount > 0:
                messagebox.showinfo("Sucesso", "Cliente excluído com sucesso.")
                janela.destroy()
            else:
                messagebox.showwarning("Atenção", "Cliente não encontrado.")

    janela = tk.Toplevel()
    janela.title("Excluir Cliente")
    janela.geometry("600x400" if tela_cheia else "300x200")
    janela.configure(bg="#1e1e1e")

    frame = tk.Frame(janela, bg="#1e1e1e")
    frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

    tk.Label(frame, text="ID do Cliente", bg="#1e1e1e", fg="white", font=("Arial", 14)).pack(pady=10)
    entry_id = tk.Entry(frame, font=("Arial", 14))
    entry_id.pack(pady=10)

    tk.Button(frame, text="Excluir", command=excluir, bg="#e74c3c", fg="white", font=("Arial", 14)).pack(pady=10)
    tk.Button(frame, text="Voltar", command=lambda: voltar(janela), bg="#34495e", fg="white", font=("Arial", 12)).pack(pady=5)