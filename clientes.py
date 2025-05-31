import sqlite3
import bcrypt
import tkinter as tk
from tkinter import messagebox, ttk, filedialog
from typing import Optional, Dict, List, Tuple, Any
from datetime import datetime, timedelta
import pandas as pd
import json
import logging
import re
from utils import THEMES, ModernButton, NotificationManager
from database import execute_query, DatabaseError
from config import get_config

# Initialize logging
logger = logging.getLogger(__name__)

class PasswordError(Exception):
    """Exception for password-related errors"""
    pass

class UserError(Exception):
    """Exception for user-related errors"""
    pass

def validar_senha(senha: str) -> bool:
    """
    Validate password strength
    Returns True if password meets requirements, False otherwise
    """
    if len(senha) < 8:
        raise PasswordError("A senha deve ter pelo menos 8 caracteres")
    if not re.search(r"[A-Z]", senha):
        raise PasswordError("A senha deve conter pelo menos uma letra maiúscula")
    if not re.search(r"[a-z]", senha):
        raise PasswordError("A senha deve conter pelo menos uma letra minúscula")
    if not re.search(r"\d", senha):
        raise PasswordError("A senha deve conter pelo menos um número")
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", senha):
        raise PasswordError("A senha deve conter pelo menos um caractere especial")
    return True

def validar_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        raise UserError("Email inválido")
    return True

def criar_tabela_usuarios() -> None:
    """Create users table with enhanced security features"""
    query = '''
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE,
        senha BLOB NOT NULL,
        permissao TEXT DEFAULT 'Funcionario',
        data_criacao TEXT NOT NULL,
        ultimo_login TEXT,
        tentativas_login INTEGER DEFAULT 0,
        bloqueado INTEGER DEFAULT 0,
        token_reset TEXT,
        expiracao_token TEXT
    )
    '''
    try:
        execute_query(query)
        logger.info("Tabela de usuários criada/verificada com sucesso")
    except DatabaseError as e:
        logger.error(f"Erro ao criar tabela de usuários: {e}")
        raise

def cadastrar_usuario(username: str, senha: str, email: str, permissao: str = 'Funcionario') -> None:
    """
    Register a new user with enhanced security
    """
    try:
        # Validate inputs
        if not username or len(username) < 3:
            raise UserError("Nome de usuário deve ter pelo menos 3 caracteres")
        
        validar_senha(senha)
        validar_email(email)
        
        # Hash password
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(senha.encode('utf-8'), salt)
        
        # Insert user
        query = '''
        INSERT INTO usuarios (
            username, password, email, permissao, data_cadastro, ultima_atualizacao
        ) VALUES (?, ?, ?, ?, ?, ?)
        '''
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        params = (
            username,
            hashed,
            email,
            permissao,
            now,
            now
        )
        
        execute_query(query, params)
        logger.info(f"Usuário cadastrado com sucesso: {username}")
        
    except sqlite3.IntegrityError:
        logger.warning(f"Tentativa de cadastro de usuário duplicado: {username}")
        raise UserError("Nome de usuário ou email já existe")
    except Exception as e:
        logger.error(f"Erro ao cadastrar usuário: {str(e)}")
        raise

def autenticar_usuario(username: str, senha: str) -> Optional[Dict[str, Any]]:
    """
    Authenticate user with enhanced security features
    """
    try:
        # Get user data
        query = '''
        SELECT id, username, senha, permissao, tentativas_login, bloqueado
        FROM usuarios 
        WHERE username = ?
        '''
        result = execute_query(query, (username,), fetch=True)
        
        if not result:
            logger.warning(f"Tentativa de login com usuário inexistente: {username}")
            return None
            
        user = result[0]
        
        # Check if account is blocked
        if user['bloqueado']:
            logger.warning(f"Tentativa de login em conta bloqueada: {username}")
            raise UserError("Conta bloqueada. Entre em contato com o administrador.")
        
        # Verify password
        if bcrypt.checkpw(senha.encode('utf-8'), user['senha']):
            # Reset login attempts and update last login
            update_query = '''
            UPDATE usuarios 
            SET tentativas_login = 0,
                ultimo_login = ?
            WHERE id = ?
            '''
            execute_query(update_query, (
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                user['id']
            ))
            
            logger.info(f"Login bem-sucedido: {username}")
            return {
                "id": user['id'],
                "username": user['username'],
                "permissao": user['permissao']
            }
        else:
            # Increment failed attempts
            attempts = user['tentativas_login'] + 1
            update_query = '''
            UPDATE usuarios 
            SET tentativas_login = ?,
                bloqueado = ?
            WHERE id = ?
            '''
            blocked = 1 if attempts >= 3 else 0
            execute_query(update_query, (attempts, blocked, user['id']))
            
            if blocked:
                logger.warning(f"Conta bloqueada após múltiplas tentativas: {username}")
                raise UserError("Conta bloqueada após múltiplas tentativas")
            
            logger.warning(f"Tentativa de login falha: {username}")
            return None
            
    except DatabaseError as e:
        logger.error(f"Erro de banco de dados na autenticação: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Erro na autenticação: {str(e)}")
        raise

def listar_usuarios() -> List[Dict[str, Any]]:
    """List all users with their details"""
    query = '''
    SELECT id, username, email, permissao, 
           data_criacao, ultimo_login, bloqueado
    FROM usuarios
    '''
    try:
        result = execute_query(query, fetch=True)
        return result if result else []
    except DatabaseError as e:
        logger.error(f"Erro ao listar usuários: {str(e)}")
        raise

def alterar_senha(user_id: int, senha_atual: str, nova_senha: str) -> None:
    """Change user password with validation"""
    try:
        # Verify current password
        query = 'SELECT senha FROM usuarios WHERE id = ?'
        result = execute_query(query, (user_id,), fetch=True)
        
        if not result or not bcrypt.checkpw(senha_atual.encode('utf-8'), result[0]['senha']):
            raise PasswordError("Senha atual incorreta")
        
        # Validate and update new password
        validar_senha(nova_senha)
        hashed = bcrypt.hashpw(nova_senha.encode('utf-8'), bcrypt.gensalt())
        
        update_query = 'UPDATE usuarios SET senha = ? WHERE id = ?'
        execute_query(update_query, (hashed, user_id))
        
        logger.info(f"Senha alterada com sucesso para usuário ID: {user_id}")
    except Exception as e:
        logger.error(f"Erro ao alterar senha: {str(e)}")
        raise

def resetar_senha(email: str) -> None:
    """Initialize password reset process"""
    try:
        import os
        # Generate reset token
        token = os.urandom(32).hex()
        expiration = datetime.now() + timedelta(hours=24)
        
        # Update user record
        query = '''
        UPDATE usuarios 
        SET token_reset = ?,
            expiracao_token = ?
        WHERE email = ?
        '''
        execute_query(query, (
            token,
            expiration.strftime('%Y-%m-%d %H:%M:%S'),
            email
        ))
        
        # Send reset email (implement email sending logic)
        logger.info(f"Token de reset gerado para: {email}")
        
    except Exception as e:
        logger.error(f"Erro ao iniciar reset de senha: {str(e)}")
        raise

def listar_clientes() -> List[Dict[str, Any]]:
    """List all clients"""
    query = '''
    SELECT id, nome, cpf, email, telefone, endereco,
           data_cadastro, ultima_atualizacao
    FROM clientes
    ORDER BY nome
    '''
    try:
        result = execute_query(query, fetch=True)
        return result if result else []
    except DatabaseError as e:
        logger.error(f"Erro ao listar clientes: {str(e)}")
        raise

def buscar_clientes(termo: str) -> List[Dict[str, Any]]:
    """Search clients by name, CPF or email"""
    query = '''
    SELECT id, nome, cpf, email, telefone, endereco,
           data_cadastro, ultima_atualizacao
    FROM clientes
    WHERE nome LIKE ? OR cpf LIKE ? OR email LIKE ?
    ORDER BY nome
    '''
    try:
        params = (f'%{termo}%', f'%{termo}%', f'%{termo}%')
        result = execute_query(query, params, fetch=True)
        return result if result else []
    except DatabaseError as e:
        logger.error(f"Erro ao buscar clientes: {str(e)}")
        raise

def cadastrar_cliente(nome: str, cpf: str, email: str, telefone: str = None, endereco: str = None) -> None:
    """Register a new client"""
    try:
        query = '''
        INSERT INTO clientes (
            nome, cpf, email, telefone, endereco, 
            data_cadastro, ultima_atualizacao
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        '''
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        params = (nome, cpf, email, telefone, endereco, now, now)
        execute_query(query, params)
        logger.info(f"Cliente cadastrado: {nome}")
    except sqlite3.IntegrityError:
        logger.warning(f"Tentativa de cadastro duplicado: {cpf}")
        raise UserError("CPF ou email já cadastrado")
    except Exception as e:
        logger.error(f"Erro ao cadastrar cliente: {str(e)}")
        raise

def atualizar_cliente(cliente_id: int, nome: str, cpf: str, email: str, 
                     telefone: str = None, endereco: str = None) -> None:
    """Update client information"""
    try:
        query = '''
        UPDATE clientes 
        SET nome = ?, cpf = ?, email = ?, telefone = ?, 
            endereco = ?, ultima_atualizacao = ?
        WHERE id = ?
        '''
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        params = (nome, cpf, email, telefone, endereco, now, cliente_id)
        execute_query(query, params)
        logger.info(f"Cliente atualizado: ID {cliente_id}")
    except sqlite3.IntegrityError:
        logger.warning(f"Conflito na atualização do cliente: {cpf}")
        raise UserError("CPF ou email já existe")
    except Exception as e:
        logger.error(f"Erro ao atualizar cliente: {str(e)}")
        raise

def excluir_cliente(cliente_id: int) -> None:
    """Delete a client"""
    try:
        query = 'DELETE FROM clientes WHERE id = ?'
        execute_query(query, (cliente_id,))
        logger.info(f"Cliente excluído: ID {cliente_id}")
    except Exception as e:
        logger.error(f"Erro ao excluir cliente: {str(e)}")
        raise

def confirmar_reset_senha(token: str, nova_senha: str) -> None:
    """Complete password reset process"""
    try:
        # Verify token
        query = '''
        SELECT id FROM usuarios 
        WHERE token_reset = ? 
        AND expiracao_token > ?
        AND bloqueado = 0
        '''
        result = execute_query(query, (
            token,
            datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ), fetch=True)
        
        if not result:
            raise UserError("Token inválido ou expirado")
        
        # Update password
        validar_senha(nova_senha)
        hashed = bcrypt.hashpw(nova_senha.encode('utf-8'), bcrypt.gensalt())
        
        update_query = '''
        UPDATE usuarios 
        SET senha = ?,
            token_reset = NULL,
            expiracao_token = NULL,
            tentativas_login = 0
        WHERE id = ?
        '''
        execute_query(update_query, (hashed, result[0]['id']))
        
        logger.info(f"Senha resetada com sucesso para usuário ID: {result[0]['id']}")
    except Exception as e:
        logger.error(f"Erro ao confirmar reset de senha: {str(e)}")
        raise

def desbloquear_usuario(user_id: int) -> None:
    """Unblock a user account"""
    try:
        query = '''
        UPDATE usuarios 
        SET bloqueado = 0,
            tentativas_login = 0
        WHERE id = ?
        '''
        execute_query(query, (user_id,))
        logger.info(f"Usuário desbloqueado: ID {user_id}")
    except Exception as e:
        logger.error(f"Erro ao desbloquear usuário: {str(e)}")
        raise

# === GUI ===

def voltar(janela):
    janela.destroy()

def gui_cadastrar_cliente(tela_cheia=True):
    """Enhanced GUI for registering a new client"""
    config = get_config()
    theme = config['theme']['light']
    
    def salvar_cliente():
        nome = entry_nome.get().strip()
        cpf = entry_cpf.get().strip()
        email = entry_email.get().strip()
        telefone = entry_telefone.get().strip()
        endereco = entry_endereco.get().strip()
        
        if not all([nome, cpf, email]):
            notification_manager.show_notification(
                "Nome, CPF e Email são obrigatórios",
                type_='warning'
            )
            return
            
        try:
            cadastrar_cliente(
                nome=nome,
                cpf=cpf,
                email=email,
                telefone=telefone if telefone else None,
                endereco=endereco if endereco else None
            )
            notification_manager.show_notification(
                "Cliente cadastrado com sucesso!",
                type_='success'
            )
            janela.after(1500, janela.destroy)
        except UserError as e:
            notification_manager.show_notification(str(e), type_='error')
        except Exception as e:
            logger.error(f"Erro inesperado ao cadastrar cliente: {str(e)}")
            notification_manager.show_notification(
                "Erro interno do sistema",
                type_='error'
            )

    janela = tk.Toplevel()
    janela.title("Cadastrar Cliente")
    janela.geometry("500x600")
    janela.configure(bg=theme['background'])
    
    # Initialize notification manager
    notification_manager = NotificationManager(janela)

    # Main frame
    main_frame = ttk.Frame(janela)
    main_frame.pack(fill='both', expand=True, padx=30, pady=30)

    # Title
    ttk.Label(main_frame,
        text="Cadastrar Novo Cliente",
        font=('Arial', 18, 'bold')).pack(pady=(0, 20))

    # Form frame
    form_frame = ttk.Frame(main_frame)
    form_frame.pack(fill='x')

    # Form fields
    ttk.Label(form_frame, text="Nome:").pack(anchor='w', pady=(0, 5))
    entry_nome = ttk.Entry(form_frame, width=40, font=('Arial', 12))
    entry_nome.pack(fill='x', pady=(0, 15))

    ttk.Label(form_frame, text="CPF:").pack(anchor='w', pady=(0, 5))
    entry_cpf = ttk.Entry(form_frame, width=40, font=('Arial', 12))
    entry_cpf.pack(fill='x', pady=(0, 15))

    ttk.Label(form_frame, text="Email:").pack(anchor='w', pady=(0, 5))
    entry_email = ttk.Entry(form_frame, width=40, font=('Arial', 12))
    entry_email.pack(fill='x', pady=(0, 15))

    ttk.Label(form_frame, text="Telefone (opcional):").pack(anchor='w', pady=(0, 5))
    entry_telefone = ttk.Entry(form_frame, width=40, font=('Arial', 12))
    entry_telefone.pack(fill='x', pady=(0, 15))

    ttk.Label(form_frame, text="Endereço (opcional):").pack(anchor='w', pady=(0, 5))
    entry_endereco = ttk.Entry(form_frame, width=40, font=('Arial', 12))
    entry_endereco.pack(fill='x', pady=(0, 20))

    # Buttons
    button_frame = ttk.Frame(form_frame)
    button_frame.pack(fill='x', pady=10)

    ModernButton(button_frame,
        text="Cadastrar",
        command=salvar_cliente,
        width=15).pack(side='left', padx=(0, 10))

    ModernButton(button_frame,
        text="Cancelar",
        command=janela.destroy,
        width=15).pack(side='left')

    # Focus on first field
    entry_nome.focus()

def gui_listar_clientes(tela_cheia=True):
    """Enhanced GUI for listing clients"""
    config = get_config()
    theme = config['theme']['light']
    
    janela = tk.Toplevel()
    janela.title("Lista de Clientes")
    janela.geometry("900x600")
    janela.configure(bg=theme['background'])

    # Main frame
    main_frame = ttk.Frame(janela)
    main_frame.pack(fill='both', expand=True, padx=20, pady=20)

    # Title
    ttk.Label(main_frame,
        text="Lista de Clientes",
        font=('Arial', 18, 'bold')).pack(pady=(0, 20))

    # Search frame
    search_frame = ttk.Frame(main_frame)
    search_frame.pack(fill='x', pady=(0, 10))

    ttk.Label(search_frame, text="Buscar:").pack(side='left', padx=(0, 5))
    search_var = tk.StringVar()
    search_entry = ttk.Entry(search_frame, textvariable=search_var, width=30)
    search_entry.pack(side='left', padx=(0, 10))

    def buscar_clientes_gui():
        termo = search_var.get().strip()
        # Clear existing items
        for item in tree.get_children():
            tree.delete(item)
        
        # Load filtered results
        try:
            if termo:
                clientes = buscar_clientes(termo)
            else:
                clientes = listar_clientes()
            
            for cliente in clientes:
                tree.insert('', 'end', values=(
                    cliente['id'],
                    cliente['nome'],
                    cliente['cpf'],
                    cliente.get('email', 'N/A'),
                    cliente.get('telefone', 'N/A'),
                    cliente.get('endereco', 'N/A')
                ))
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao buscar clientes: {str(e)}")

    ModernButton(search_frame,
        text="Buscar",
        command=buscar_clientes_gui,
        width=10).pack(side='left')

    # Treeview
    columns = ("ID", "Nome", "CPF", "Email", "Telefone", "Endereço")
    tree = ttk.Treeview(main_frame, columns=columns, show='headings', height=15)
    
    # Configure columns
    col_widths = {"ID": 50, "Nome": 150, "CPF": 120, "Email": 200, "Telefone": 120, "Endereço": 200}
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, anchor=tk.CENTER, width=col_widths.get(col, 100))

    # Scrollbars
    v_scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=tree.yview)
    h_scrollbar = ttk.Scrollbar(main_frame, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

    # Grid layout
    tree.grid(row=1, column=0, sticky='nsew')
    v_scrollbar.grid(row=1, column=1, sticky='ns')
    h_scrollbar.grid(row=2, column=0, sticky='ew')

    main_frame.grid_rowconfigure(1, weight=1)
    main_frame.grid_columnconfigure(0, weight=1)

    # Load initial data
    buscar_clientes_gui()

    # Buttons
    button_frame = ttk.Frame(main_frame)
    button_frame.grid(row=3, column=0, columnspan=2, pady=10, sticky='ew')

    ModernButton(button_frame,
        text="Atualizar",
        command=buscar_clientes_gui,
        width=12).pack(side='left', padx=(0, 10))

    ModernButton(button_frame,
        text="Fechar",
        command=janela.destroy,
        width=12).pack(side='left')

    # Bind search on enter
    search_entry.bind('<Return>', lambda e: buscar_clientes_gui())

def gui_atualizar_cliente(cliente_id: int):
    """GUI for updating client information"""
    config = get_config()
    theme = config['theme']['light']
    
    def carregar_dados():
        try:
            query = 'SELECT nome, cpf, email, telefone, endereco FROM clientes WHERE id = ?'
            result = execute_query(query, (cliente_id,), fetch=True)
            if result:
                cliente = result[0]
                entry_nome.delete(0, tk.END)
                entry_nome.insert(0, cliente['nome'])
                entry_cpf.delete(0, tk.END)
                entry_cpf.insert(0, cliente['cpf'])
                entry_email.delete(0, tk.END)
                entry_email.insert(0, cliente.get('email', ''))
                entry_telefone.delete(0, tk.END)
                entry_telefone.insert(0, cliente.get('telefone', ''))
                entry_endereco.delete(0, tk.END)
                entry_endereco.insert(0, cliente.get('endereco', ''))
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar dados: {str(e)}")
    
    def salvar_alteracoes():
        nome = entry_nome.get().strip()
        cpf = entry_cpf.get().strip()
        email = entry_email.get().strip()
        telefone = entry_telefone.get().strip()
        endereco = entry_endereco.get().strip()
        
        if not all([nome, cpf, email]):
            notification_manager.show_notification(
                "Nome, CPF e Email são obrigatórios",
                type_='warning'
            )
            return
            
        try:
            validar_email(email)
            atualizar_cliente(
                cliente_id=cliente_id,
                nome=nome,
                cpf=cpf,
                email=email,
                telefone=telefone if telefone else None,
                endereco=endereco if endereco else None
            )
            notification_manager.show_notification(
                "Cliente atualizado com sucesso!",
                type_='success'
            )
            janela.after(1500, janela.destroy)
        except UserError as e:
            notification_manager.show_notification(str(e), type_='error')
        except Exception as e:
            logger.error(f"Erro ao atualizar cliente: {str(e)}")
            notification_manager.show_notification(
                "Erro interno do sistema",
                type_='error'
            )

    janela = tk.Toplevel()
    janela.title("Atualizar Cliente")
    janela.geometry("500x500")
    janela.configure(bg=theme['background'])
    
    # Initialize notification manager
    notification_manager = NotificationManager(janela)

    # Main frame
    main_frame = ttk.Frame(janela)
    main_frame.pack(fill='both', expand=True, padx=30, pady=30)

    # Title
    ttk.Label(main_frame,
        text="Atualizar Cliente",
        font=('Arial', 18, 'bold')).pack(pady=(0, 20))

    # Form frame
    form_frame = ttk.Frame(main_frame)
    form_frame.pack(fill='x')

    # Form fields
    ttk.Label(form_frame, text="Nome:").pack(anchor='w', pady=(0, 5))
    entry_nome = ttk.Entry(form_frame, width=40, font=('Arial', 12))
    entry_nome.pack(fill='x', pady=(0, 15))

    ttk.Label(form_frame, text="CPF:").pack(anchor='w', pady=(0, 5))
    entry_cpf = ttk.Entry(form_frame, width=40, font=('Arial', 12))
    entry_cpf.pack(fill='x', pady=(0, 15))

    ttk.Label(form_frame, text="Email:").pack(anchor='w', pady=(0, 5))
    entry_email = ttk.Entry(form_frame, width=40, font=('Arial', 12))
    entry_email.pack(fill='x', pady=(0, 15))

    ttk.Label(form_frame, text="Telefone (opcional):").pack(anchor='w', pady=(0, 5))
    entry_telefone = ttk.Entry(form_frame, width=40, font=('Arial', 12))
    entry_telefone.pack(fill='x', pady=(0, 15))

    ttk.Label(form_frame, text="Endereço (opcional):").pack(anchor='w', pady=(0, 5))
    entry_endereco = ttk.Entry(form_frame, width=40, font=('Arial', 12))
    entry_endereco.pack(fill='x', pady=(0, 20))

    # Buttons
    button_frame = ttk.Frame(form_frame)
    button_frame.pack(fill='x', pady=10)

    ModernButton(button_frame,
        text="Salvar",
        command=salvar_alteracoes,
        width=15).pack(side='left', padx=(0, 10))

    ModernButton(button_frame,
        text="Cancelar",
        command=janela.destroy,
        width=15).pack(side='left')

    # Load existing data
    carregar_dados()

def gui_excluir_cliente(tela_cheia=True):
    """Enhanced GUI for deleting a client"""
    config = get_config()
    theme = config['theme']['light']
    
    def excluir():
        id_user = entry_id.get()
        if not id_user.isdigit():
            notification_manager.show_notification(
                "ID inválido",
                type_='error'
            )
            return
            
        if not messagebox.askyesno("Confirmar", 
            "Tem certeza que deseja excluir este cliente? Esta ação não pode ser desfeita."):
            return
            
        try:
            excluir_cliente(int(id_user))
            notification_manager.show_notification(
                "Cliente excluído com sucesso!",
                type_='success'
            )
            janela.after(1500, janela.destroy)
        except Exception as e:
            logger.error(f"Erro ao excluir cliente: {str(e)}")
            notification_manager.show_notification(
                "Erro ao excluir cliente",
                type_='error'
            )

    janela = tk.Toplevel()
    janela.title("Excluir Cliente")
    janela.geometry("400x300")
    janela.configure(bg=theme['background'])
    
    # Initialize notification manager
    notification_manager = NotificationManager(janela)

    # Main frame
    main_frame = ttk.Frame(janela)
    main_frame.pack(fill='both', expand=True, padx=30, pady=30)

    # Title
    ttk.Label(main_frame,
        text="Excluir Cliente",
        font=('Arial', 18, 'bold')).pack(pady=(0, 20))

    # Warning message
    ttk.Label(main_frame,
        text="Atenção: Esta ação não pode ser desfeita!",
        foreground='red',
        font=('Arial', 10, 'bold')).pack(pady=(0, 20))

    # Form frame
    form_frame = ttk.Frame(main_frame)
    form_frame.pack(fill='x')

    ttk.Label(form_frame, text="ID do Cliente:").pack(anchor='w', pady=(0, 5))
    entry_id = ttk.Entry(form_frame, width=20, font=('Arial', 12))
    entry_id.pack(fill='x', pady=(0, 20))

    # Buttons
    button_frame = ttk.Frame(form_frame)
    button_frame.pack(fill='x', pady=10)

    ModernButton(button_frame,
        text="Excluir",
        command=excluir,
        width=15).pack(side='left', padx=(0, 10))

    ModernButton(button_frame,
        text="Cancelar",
        command=janela.destroy,
        width=15).pack(side='left')

    # Focus on entry
    entry_id.focus()
