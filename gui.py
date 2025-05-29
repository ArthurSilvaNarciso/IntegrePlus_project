import tkinter as tk
from tkinter import messagebox, filedialog, ttk
from PIL import Image, ImageTk
import produtos, relatorios, clientes
import pandas as pd
import matplotlib.pyplot as plt
import shutil
import smtplib
from email.message import EmailMessage
from datetime import datetime, timedelta
import database

usuario_logado = None
permissao_usuario = None
tema_atual = 'escuro'

def aplicar_tema(style, tema='claro'):
    if tema == 'claro':
        style.theme_use('default')
        root.tk_setPalette(background='white', foreground='black')
        style.configure('.', background='white', foreground='black')
        style.configure('TButton', background='#3498db', foreground='white', font=("Arial", 12))
    else:
        style.theme_use('clam')
        root.tk_setPalette(background='#2c3e50', foreground='white')
        style.configure('.', background='#2c3e50', foreground='white')
        style.configure('TButton', background='#34495e', foreground='white', font=("Arial", 12))

def alternar_tema():
    global tema_atual
    tema_atual = 'escuro' if tema_atual == 'claro' else 'claro'
    aplicar_tema(estilo, tema_atual)
    root.configure(bg='white' if tema_atual == 'claro' else '#2c3e50')

def backup_banco():
    try:
        nome_backup = f'backup_integre_plus_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'
        shutil.copy('integre_plus.db', nome_backup)
        messagebox.showinfo("Backup", f"Backup criado com sucesso: {nome_backup}")
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao criar backup: {str(e)}")

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

def dashboard():
    try:
        dados = produtos.listar_produtos()
        if not dados:
            messagebox.showinfo("Dashboard", "Nenhum produto cadastrado para exibir.")
            return
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

def abrir_cadastro():
    cadastro = tk.Toplevel()
    cadastro.title("Cadastro de Usuário")
    cadastro.attributes('-fullscreen', True)
    cadastro.config(bg="#2c3e50")

    frame = tk.Frame(cadastro, bg="#34495e")
    frame.place(relx=0.5, rely=0.5, anchor="center")

    tk.Label(frame, text="Usuário", font=("Arial", 16), bg="#34495e", fg="white").pack(pady=10)
    entry_user = tk.Entry(frame, font=("Arial", 16), width=30)
    entry_user.pack(pady=10)

    tk.Label(frame, text="Senha", font=("Arial", 16), bg="#34495e", fg="white").pack(pady=10)
    entry_pass = tk.Entry(frame, show="*", font=("Arial", 16), width=30)
    entry_pass.pack(pady=10)

    tk.Label(frame, text="Permissão", font=("Arial", 16), bg="#34495e", fg="white").pack(pady=10)
    var_permissao = tk.StringVar(value="Funcionario")
    ttk.OptionMenu(frame, var_permissao, "Funcionario", "Admin", "Funcionario").pack(pady=10)

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

    tk.Button(frame, text="Cadastrar", command=efetuar_cadastro, font=("Arial", 16), bg="#3498db", fg="white", width=20).pack(pady=20)
    tk.Button(frame, text="Voltar", command=cadastro.destroy, font=("Arial", 12), bg="#95a5a6", fg="white", width=20).pack()

def atualizar_estoque():
    # Função para atualizar o painel lateral de estoque
    if 'estoque_frame' in globals():
        produtos.gui_listar_produtos(parent=estoque_frame)

def main_gui():
    global root, estilo, estoque_frame
    root = tk.Tk()
    root.title("Integre+ Adegas e Suplementos")
    root.attributes('-fullscreen', True)

    estilo = ttk.Style()
    aplicar_tema(estilo, tema_atual)

    # Cabeçalho
    cabecalho = tk.Frame(root, bg="#2980b9", height=70)
    cabecalho.pack(fill="x")
    cabecalho.pack_propagate(False)

    # Título do sistema
    tk.Label(cabecalho, text="Integre+ Adegas e Suplementos", 
             font=("Arial", 22, "bold"), bg="#2980b9", fg="white").pack(side="left", padx=30, pady=15)

    # Informações do usuário logado
    info_usuario = f"Usuário: {usuario_logado} | Permissão: {permissao_usuario}"
    tk.Label(cabecalho, text=info_usuario, 
             font=("Arial", 12), bg="#2980b9", fg="white").pack(side="left", padx=20, pady=15)

    # Botões do cabeçalho
    tk.Button(cabecalho, text="Tema Claro/Escuro", command=alternar_tema, 
              bg="#1abc9c", fg="white", font=("Arial", 12)).pack(side="right", padx=10, pady=15)
    
    tk.Button(cabecalho, text="Logout", command=lambda: (root.destroy(), gui_login()), 
              bg="#c0392b", fg="white", font=("Arial", 12)).pack(side="right", padx=10, pady=15)

    # Corpo principal
    corpo = tk.Frame(root, bg="#ecf0f1")
    corpo.pack(fill="both", expand=True)

    # Menu lateral esquerdo
    menu_frame = tk.Frame(corpo, bg="#34495e", width=250)
    menu_frame.pack(side="left", fill="y")
    menu_frame.pack_propagate(False)

    # Título do menu
    tk.Label(menu_frame, text="MENU PRINCIPAL", 
             font=("Arial", 16, "bold"), bg="#34495e", fg="white").pack(pady=20)

    # Botões do menu principal
    botoes_principais = [
        ("📦 Cadastrar Produto", lambda: produtos.gui_cadastrar_produto(tela_cheia=True)),
        ("📊 Dashboard", dashboard),
        ("📈 Relatório Validade", relatorio_validade),
        ("💾 Backup Banco", backup_banco),
        ("📥 Importar CSV", importar_produtos_csv)
    ]

    # Adicionar botões específicos para Admin
    if permissao_usuario == "Admin":
        botoes_principais.extend([
            ("👤 Cadastrar Usuário", abrir_cadastro),
            ("👥 Gerenciar Clientes", clientes.gui_listar_clientes)
        ])

    for texto, comando in botoes_principais:
        btn = tk.Button(menu_frame, text=texto, command=comando,
                       bg="#3498db", fg="white", font=("Arial", 12),
                       width=25, height=2, relief="flat")
        btn.pack(pady=5, padx=10, fill="x")

    # Área de conteúdo central
    conteudo_frame = tk.Frame(corpo, bg="#ecf0f1")
    conteudo_frame.pack(side="left", fill="both", expand=True)

    # Painel de boas-vindas
    boas_vindas = tk.Frame(conteudo_frame, bg="#ffffff", relief="raised", bd=2)
    boas_vindas.pack(fill="both", expand=True, padx=20, pady=20)

    tk.Label(boas_vindas, text=f"Bem-vindo ao Integre+, {usuario_logado}!", 
             font=("Arial", 24, "bold"), bg="#ffffff", fg="#2c3e50").pack(pady=30)

    tk.Label(boas_vindas, text="Sistema de Gestão para Adegas e Suplementos", 
             font=("Arial", 16), bg="#ffffff", fg="#7f8c8d").pack(pady=10)

    # Frame para estatísticas rápidas
    stats_frame = tk.Frame(boas_vindas, bg="#ffffff")
    stats_frame.pack(pady=30)

    try:
        # Estatísticas rápidas
        total_produtos = len(produtos.listar_produtos())
        total_usuarios = len(clientes.listar_usuarios())
        
        # Cards de estatísticas
        cards = [
            ("Total de Produtos", total_produtos, "#3498db"),
            ("Total de Usuários", total_usuarios, "#27ae60"),
            ("Produtos Baixo Estoque", len(produtos.produtos_estoque_baixo()), "#e74c3c")
        ]

        for i, (titulo, valor, cor) in enumerate(cards):
            card = tk.Frame(stats_frame, bg=cor, width=200, height=100)
            card.grid(row=0, column=i, padx=20, pady=10)
            card.pack_propagate(False)
            
            tk.Label(card, text=str(valor), font=("Arial", 28, "bold"), 
                    bg=cor, fg="white").pack(pady=10)
            tk.Label(card, text=titulo, font=("Arial", 12), 
                    bg=cor, fg="white").pack()

    except Exception as e:
        tk.Label(boas_vindas, text="Erro ao carregar estatísticas", 
                font=("Arial", 14), bg="#ffffff", fg="#e74c3c").pack(pady=20)

    # Painel lateral direito - Estoque
    estoque_frame = tk.Frame(corpo, bg="#2c3e50", width=400)
    estoque_frame.pack(side="right", fill="y")
    estoque_frame.pack_propagate(False)

    # Carregar lista de produtos no painel lateral
    produtos.gui_listar_produtos(parent=estoque_frame)

    # Barra de menu superior
    menubar = tk.Menu(root)
    
    # Menu Produtos
    menu_produtos = tk.Menu(menubar, tearoff=0)
    menu_produtos.add_command(label="Cadastrar Produto", command=lambda: produtos.gui_cadastrar_produto(tela_cheia=True))
    menu_produtos.add_command(label="Listar Produtos", command=lambda: produtos.gui_listar_produtos(tela_cheia=True))
    menu_produtos.add_command(label="Atualizar Produto", command=lambda: produtos.gui_atualizar_produto(tela_cheia=True))
    menu_produtos.add_command(label="Excluir Produto", command=lambda: produtos.gui_excluir_produto(tela_cheia=True))
    menu_produtos.add_separator()
    menu_produtos.add_command(label="Importar CSV", command=importar_produtos_csv)
    menu_produtos.add_command(label="Exportar Excel", command=produtos.exportar_produtos_para_excel)
    menubar.add_cascade(label="Produtos", menu=menu_produtos)

    # Menu Clientes
    menu_clientes = tk.Menu(menubar, tearoff=0)
    menu_clientes.add_command(label="Cadastrar Cliente", command=lambda: clientes.gui_cadastrar_cliente(tela_cheia=True))
    menu_clientes.add_command(label="Listar Clientes", command=lambda: clientes.gui_listar_clientes(tela_cheia=True))
    menu_clientes.add_command(label="Excluir Cliente", command=lambda: clientes.gui_excluir_cliente(tela_cheia=True))
    menubar.add_cascade(label="Clientes", menu=menu_clientes)

    # Menu Relatórios
    menu_relatorios = tk.Menu(menubar, tearoff=0)
    menu_relatorios.add_command(label="Relatório de Validade", command=relatorio_validade)
    menu_relatorios.add_command(label="Relatório de Clientes", command=relatorios.gerar_relatorio_clientes)
    menu_relatorios.add_command(label="Relatório por Categoria", command=relatorios.gerar_relatorio_categoria)
    menu_relatorios.add_command(label="Relatório Geral", command=relatorios.gerar_relatorio_geral)
    menu_relatorios.add_separator()
    menu_relatorios.add_command(label="Gráfico de Vendas", command=relatorios.grafico_vendas)
    menubar.add_cascade(label="Relatórios", menu=menu_relatorios)

    # Menu Sistema
    menu_sistema = tk.Menu(menubar, tearoff=0)
    menu_sistema.add_command(label="Backup do Banco", command=backup_banco)
    menu_sistema.add_command(label="Alternar Tema", command=alternar_tema)
    menu_sistema.add_separator()
    if permissao_usuario == "Admin":
        menu_sistema.add_command(label="Cadastrar Usuário", command=abrir_cadastro)
    menu_sistema.add_command(label="Logout", command=lambda: (root.destroy(), gui_login()))
    menu_sistema.add_command(label="Sair", command=root.quit)
    menubar.add_cascade(label="Sistema", menu=menu_sistema)

    # Menu Ajuda
    menu_ajuda = tk.Menu(menubar, tearoff=0)
    menu_ajuda.add_command(label="Sobre", command=lambda: messagebox.showinfo("Sobre", 
        "Integre+ v1.0\nSistema de Gestão para Adegas e Suplementos\n\nDesenvolvido com Python e Tkinter"))
    menubar.add_cascade(label="Ajuda", menu=menu_ajuda)

    root.config(menu=menubar)

    # Barra de status
    status_bar = tk.Frame(root, bg="#34495e", height=25)
    status_bar.pack(side="bottom", fill="x")
    status_bar.pack_propagate(False)

    data_atual = datetime.now().strftime("%d/%m/%Y %H:%M")
    tk.Label(status_bar, text=f"Data/Hora: {data_atual} | Usuário: {usuario_logado} | Sistema: Integre+ v1.0", 
             bg="#34495e", fg="white", font=("Arial", 10)).pack(side="left", padx=10, pady=2)

    root.mainloop()

def gui_login():
    global usuario_logado, permissao_usuario
    
    login = tk.Tk()
    login.title("Integre+ - Login")
    login.attributes('-fullscreen', True)
    login.config(bg="#2c3e50")

    # Frame central
    frame = tk.Frame(login, bg="#34495e", padx=40, pady=40)
    frame.place(relx=0.5, rely=0.5, anchor="center")

    # Logo/Título
    tk.Label(frame, text="INTEGRE+", font=("Arial", 32, "bold"), 
             bg="#34495e", fg="#3498db").pack(pady=20)
    
    tk.Label(frame, text="Sistema de Gestão", font=("Arial", 16), 
             bg="#34495e", fg="white").pack(pady=5)
    
    tk.Label(frame, text="Adegas e Suplementos", font=("Arial", 16), 
             bg="#34495e", fg="white").pack(pady=(0, 30))

    # Campos de login
    tk.Label(frame, text="Usuário:", font=("Arial", 14), 
             bg="#34495e", fg="white").pack(anchor="w", pady=(10, 5))
    entry_user = tk.Entry(frame, font=("Arial", 14), width=30)
    entry_user.pack(pady=(0, 10))

    tk.Label(frame, text="Senha:", font=("Arial", 14), 
             bg="#34495e", fg="white").pack(anchor="w", pady=(10, 5))
    entry_pass = tk.Entry(frame, show="*", font=("Arial", 14), width=30)
    entry_pass.pack(pady=(0, 20))

    def fazer_login():
        global usuario_logado, permissao_usuario
        user = entry_user.get().strip()
        senha = entry_pass.get()
        
        if not user or not senha:
            messagebox.showwarning("Campos obrigatórios", "Preencha todos os campos!")
            return
            
        usuario = clientes.autenticar_usuario(user, senha)
        if usuario:
            usuario_logado = user
            permissao_usuario = usuario.get('permissao', 'Funcionario') if isinstance(usuario, dict) else 'Funcionario'
            login.destroy()
            main_gui()
        else:
            messagebox.showerror("Erro", "Usuário ou senha inválidos!")
            entry_pass.delete(0, tk.END)

    # Permitir login com Enter
    def on_enter(event):
        fazer_login()
    
    entry_user.bind('<Return>', on_enter)
    entry_pass.bind('<Return>', on_enter)

    # Botões
    tk.Button(frame, text="Entrar", command=fazer_login, 
              font=("Arial", 14), bg="#27ae60", fg="white", 
              width=25, height=2).pack(pady=10)
    
    tk.Button(frame, text="Cadastrar Novo Usuário", command=abrir_cadastro, 
              font=("Arial", 14), bg="#2980b9", fg="white", 
              width=25, height=2).pack(pady=5)
    
    tk.Button(frame, text="Sair", command=login.destroy, 
              font=("Arial", 14), bg="#c0392b", fg="white", 
              width=25, height=2).pack(pady=10)

    # Focar no campo usuário
    entry_user.focus()

    login.mainloop()

if __name__ == "__main__":
    # Inicializar banco de dados
    database.criar_tabelas()
    gui_login()