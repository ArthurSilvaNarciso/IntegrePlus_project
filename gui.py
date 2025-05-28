import tkinter as tk
from tkinter import messagebox, filedialog
from tkinter import ttk
import produtos, relatorios, clientes
import pandas as pd
import matplotlib.pyplot as plt
import shutil
import smtplib
from email.message import EmailMessage
from datetime import datetime, timedelta
import database

# Variáveis globais para controle de usuário
usuario_logado = None
permissao_usuario = None

# Função para criar backup do banco de dados
def backup_banco():
    try:
        nome_backup = f'backup_integre_plus_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'
        shutil.copy('integre_plus.db', nome_backup)
        messagebox.showinfo("Backup", f"Backup criado com sucesso: {nome_backup}")
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao criar backup: {str(e)}")

# Verificação de estoque baixo
def verificar_estoque_baixo():
    try:
        for prod in produtos.listar_produtos():
            if prod[2] < 5:
                messagebox.showwarning("Estoque Baixo", f"Produto '{prod[1]}' com estoque baixo: {prod[2]}")
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao verificar estoque: {str(e)}")

# Geração de relatório de validade
def relatorio_validade():
    try:
        proximos = []
        for prod in produtos.listar_produtos():
            try:
                validade = datetime.strptime(prod[4], '%d/%m/%Y')
                if validade <= datetime.now() + timedelta(days=30):
                    proximos.append(prod)
            except ValueError:
                continue
        df = pd.DataFrame(proximos, columns=["ID", "Nome", "Qtd", "Preço", "Validade"])
        df.to_excel('produtos_vencimento.xlsx', index=False)
        messagebox.showinfo("Relatório", "Relatório de validade gerado com sucesso!")
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao gerar relatório: {str(e)}")

# Exibe gráfico com estoque atual
def dashboard():
    try:
        dados = produtos.listar_produtos()
        nomes = [d[1] for d in dados]
        quantidades = [d[2] for d in dados]
        plt.figure(figsize=(10, 6))
        plt.bar(nomes, quantidades, color='skyblue')
        plt.xlabel('Produtos')
        plt.ylabel('Quantidade')
        plt.title('Estoque Atual')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao gerar dashboard: {str(e)}")

# Importação de produtos via CSV
def importar_produtos_csv():
    caminho = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if caminho:
        try:
            df = pd.read_csv(caminho)
            for _, row in df.iterrows():
                produtos.cadastrar_produto(row['Nome'], int(row['Qtd']), float(row['Preço']), row['Validade'])
            messagebox.showinfo("Importação", "Produtos importados com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro na importação: {str(e)}")

# Envia relatório por e-mail
def enviar_email_relatorio(destinatario, arquivo):
    try:
        msg = EmailMessage()
        msg['Subject'] = 'Relatório Integre+'
        msg['From'] = 'seuemail@gmail.com'
        msg['To'] = destinatario
        msg.set_content('Segue em anexo o relatório.')

        with open(arquivo, 'rb') as f:
            msg.add_attachment(f.read(), maintype='application', subtype='octet-stream', filename=arquivo)

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login('seuemail@gmail.com', 'suasenha')
            smtp.send_message(msg)

        messagebox.showinfo("Email", "Relatório enviado com sucesso!")
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao enviar e-mail: {str(e)}")

# Tela de cadastro de novo usuário
def abrir_cadastro():
    def efetuar_cadastro():
        user = entry_user.get()
        senha = entry_pass.get()
        permissao = var_permissao.get()
        if not user or not senha:
            messagebox.showerror("Erro", "Preencha todos os campos!")
            return
        try:
            clientes.cadastrar_usuario(user, senha, permissao)
            messagebox.showinfo("Sucesso", "Usuário cadastrado com sucesso!")
            cadastro.destroy()
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    cadastro = tk.Toplevel()
    cadastro.title("Cadastro de Usuário")
    cadastro.geometry("400x300")
    cadastro.config(bg="#2c3e50")

    frame = tk.Frame(cadastro, bg="#2c3e50")
    frame.pack(expand=True)

    tk.Label(frame, text="Usuário", bg="#2c3e50", fg="white", font=("Arial", 14)).pack(pady=5)
    entry_user = tk.Entry(frame, font=("Arial", 14))
    entry_user.pack(pady=5)

    tk.Label(frame, text="Senha", bg="#2c3e50", fg="white", font=("Arial", 14)).pack(pady=5)
    entry_pass = tk.Entry(frame, show='*', font=("Arial", 14))
    entry_pass.pack(pady=5)

    tk.Label(frame, text="Permissão", bg="#2c3e50", fg="white", font=("Arial", 14)).pack(pady=5)
    var_permissao = tk.StringVar(value="Funcionario")
    tk.OptionMenu(frame, var_permissao, "Admin", "Funcionario").pack(pady=5)

    tk.Button(frame, text="Cadastrar", command=efetuar_cadastro, bg="#2980b9", fg="white", font=("Arial", 14)).pack(pady=10)

# Interface principal do sistema
def main_gui():
    root = tk.Tk()
    root.title("Integre+ - Sistema de Gestão")
    root.geometry("800x600")
    root.configure(bg="#ecf0f1")

    menubar = tk.Menu(root)

    menu_arquivo = tk.Menu(menubar, tearoff=0)
    menu_arquivo.add_command(label="Backup Banco de Dados", command=backup_banco)
    menu_arquivo.add_command(label="Importar Produtos CSV", command=importar_produtos_csv)
    menu_arquivo.add_separator()
    menu_arquivo.add_command(label="Sair", command=root.quit)
    menubar.add_cascade(label="Arquivo", menu=menu_arquivo)

    menu_relatorios = tk.Menu(menubar, tearoff=0)
    menu_relatorios.add_command(label="Relatório de Validade", command=relatorio_validade)
    menu_relatorios.add_command(label="Dashboard Estoque", command=dashboard)
    menu_relatorios.add_command(label="Relatório de Clientes", command=relatorios.gerar_relatorio_clientes)
    menu_relatorios.add_command(label="Relatório por Categoria", command=relatorios.gerar_relatorio_categoria)
    menubar.add_cascade(label="Relatórios", menu=menu_relatorios)

    menu_ajuda = tk.Menu(menubar, tearoff=0)
    menu_ajuda.add_command(label="Sobre", command=lambda: messagebox.showinfo("Sobre", "Sistema Integre+ - v1.0"))
    menubar.add_cascade(label="Ajuda", menu=menu_ajuda)

    if permissao_usuario == 'Admin':
        menubar.add_command(label="Cadastrar Usuário", command=abrir_cadastro)

    root.config(menu=menubar)

    tk.Label(root, text=f"Bem-vindo, {usuario_logado}", font=("Arial", 18, "bold"), bg="#ecf0f1", fg="#2c3e50").pack(pady=20)

    botoes_frame = tk.Frame(root, bg="#ecf0f1")
    botoes_frame.pack(pady=10)

    botoes = [
        ("Verificar Estoque Baixo", verificar_estoque_baixo),
        ("Cadastrar Produto", produtos.gui_cadastrar_produto),
        ("Listar Produtos", produtos.gui_listar_produtos),
        ("Atualizar Produto", produtos.gui_atualizar_produto),
        ("Excluir Produto", produtos.gui_excluir_produto),
        ("Gerar Todos os Relatórios", relatorios.gerar_relatorio_geral),
        ("Cadastrar Cliente", clientes.gui_cadastrar_cliente),
        ("Listar Clientes", clientes.gui_listar_clientes),
        ("Excluir Cliente", clientes.gui_excluir_cliente),
    ]

    for texto, comando in botoes:
        tk.Button(botoes_frame, text=texto, command=comando, bg="#3498db", fg="white", font=("Arial", 14), width=30).pack(pady=5)

    root.mainloop()

# Tela de login inicial
def gui_login():
    login = tk.Tk()
    login.title("Integre+ - Login")
    login.geometry("500x400")
    login.config(bg="#2c3e50")

    frame = tk.Frame(login, bg="#34495e", bd=10, relief="ridge")
    frame.place(relx=0.5, rely=0.5, anchor='center')

    tk.Label(frame, text="Integre+", font=("Arial", 28, "bold"), bg="#34495e", fg="white").pack(pady=10)

    entry_user = tk.Entry(frame, font=("Arial", 16))
    entry_user.pack(pady=10)
    entry_user.insert(0, "Usuário")

    entry_pass = tk.Entry(frame, show='*', font=("Arial", 16))
    entry_pass.pack(pady=10)
    entry_pass.insert(0, "Senha")

    def fazer_login():
        user = entry_user.get()
        senha = entry_pass.get()
        u = clientes.autenticar_usuario(user, senha)
        if u:
            global usuario_logado, permissao_usuario
            usuario_logado = user
            try:
                if isinstance(u, dict):
                    permissao_usuario = u.get('permissao', 'Funcionario')
                elif isinstance(u, (list, tuple)):
                    permissao_usuario = u[3] if len(u) > 3 else 'Funcionario'
                else:
                    permissao_usuario = 'Funcionario'
            except Exception:
                messagebox.showerror("Erro", "Formato de usuário inválido!")
                return
            login.destroy()
            main_gui()
        else:
            messagebox.showerror("Erro", "Usuário ou senha inválidos!")

    tk.Button(frame, text="Login", command=fazer_login, bg="#27ae60", fg="white", font=("Arial", 14), width=20).pack(pady=5)
    tk.Button(frame, text="Cadastrar", command=abrir_cadastro, bg="#2980b9", fg="white", font=("Arial", 14), width=20).pack(pady=5)

    login.mainloop()

# Execução principal
if __name__ == "__main__":
    gui_login()
