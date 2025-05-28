import tkinter as tk
from tkinter import messagebox
from clientes import autenticar_usuario

def realizar_login():
    username = entrada_usuario.get().strip()
    senha = entrada_senha.get()

    if not username or not senha:
        messagebox.showwarning("Campos obrigatórios", "Preencha todos os campos.")
        return

    usuario = autenticar_usuario(username, senha)
    if usuario:
        messagebox.showinfo("Login bem-sucedido", f"Bem-vindo, {usuario['username']}!")
        # Aqui você pode abrir a janela principal ou redirecionar para outro módulo
        root.destroy()
    else:
        messagebox.showerror("Erro de autenticação", "Usuário ou senha incorretos.")

# --- Interface gráfica ---
root = tk.Tk()
root.title("Login - Integre+")
root.geometry("300x200")
root.resizable(False, False)

tk.Label(root, text="Usuário:").pack(pady=(20, 5))
entrada_usuario = tk.Entry(root)
entrada_usuario.pack()

tk.Label(root, text="Senha:").pack(pady=(10, 5))
entrada_senha = tk.Entry(root, show="*")
entrada_senha.pack()

tk.Button(root, text="Entrar", command=realizar_login, bg="#4CAF50", fg="white").pack(pady=15)

root.mainloop()
