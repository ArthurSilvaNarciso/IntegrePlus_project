import tkinter as tk
from tkinter import messagebox, ttk
from clientes import autenticar_usuario
from utils import THEMES, ModernButton, NotificationManager
import json
import os
from datetime import datetime
import logging

# Initialize logging
logger = logging.getLogger(__name__)

class LoginWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Login - Integre+")
        self.root.geometry("400x500")
        self.root.resizable(False, False)
        
        # Load theme
        self.theme = THEMES['claro']
        self.root.configure(bg=self.theme['background'])
        
        # Initialize notification manager
        self.notification_manager = NotificationManager(self.root)
        
        # Create and configure style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.configure_styles()
        
        self.create_widgets()
        self.load_last_username()
        
        # Center window
        self.center_window()
        
        # Bind enter key
        self.root.bind('<Return>', lambda e: self.realizar_login())

    def configure_styles(self):
        """Configure ttk styles"""
        self.style.configure('TLabel',
            background=self.theme['background'],
            foreground=self.theme['text'],
            font=('Arial', 12))
            
        self.style.configure('TEntry',
            fieldbackground=self.theme['card_bg'],
            font=('Arial', 12))
            
        self.style.configure('Login.TFrame',
            background=self.theme['background'])

    def create_widgets(self):
        """Create all login window widgets"""
        # Main frame
        main_frame = ttk.Frame(self.root, style='Login.TFrame')
        main_frame.pack(fill='both', expand=True, padx=50, pady=50)
        
        # Logo/Title
        title_frame = ttk.Frame(main_frame, style='Login.TFrame')
        title_frame.pack(fill='x', pady=(0, 30))
        
        ttk.Label(title_frame,
            text="INTEGRE+",
            font=('Arial', 24, 'bold'),
            foreground=self.theme['primary']).pack()
            
        ttk.Label(title_frame,
            text="Sistema de Gestão",
            font=('Arial', 14)).pack()
            
        # Login form
        form_frame = ttk.Frame(main_frame, style='Login.TFrame')
        form_frame.pack(fill='x')
        
        ttk.Label(form_frame, text="Usuário:").pack(anchor='w', pady=(0, 5))
        self.entrada_usuario = ttk.Entry(form_frame, width=30)
        self.entrada_usuario.pack(fill='x', pady=(0, 15))
        
        ttk.Label(form_frame, text="Senha:").pack(anchor='w', pady=(0, 5))
        self.entrada_senha = ttk.Entry(form_frame, show="•", width=30)
        self.entrada_senha.pack(fill='x', pady=(0, 5))
        
        # Remember me checkbox
        self.lembrar_usuario = tk.BooleanVar(value=True)
        ttk.Checkbutton(form_frame,
            text="Lembrar usuário",
            variable=self.lembrar_usuario,
            style='TCheckbutton').pack(anchor='w', pady=(0, 15))
        
        # Buttons
        button_frame = ttk.Frame(form_frame, style='Login.TFrame')
        button_frame.pack(fill='x', pady=(0, 10))

        ModernButton(button_frame,
            text="Entrar",
            command=self.realizar_login,
            width=20).pack(pady=(0, 10))
            
        ModernButton(button_frame,
            text="Cadastrar",
            command=self.abrir_cadastro,
            width=20).pack(pady=(0, 10))
            
        ModernButton(button_frame,
            text="Sair",
            command=self.root.destroy,
            width=20).pack()

    def center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def realizar_login(self):
        """Handle login attempt"""
        username = self.entrada_usuario.get().strip()
        senha = self.entrada_senha.get()

        if not username or not senha:
            self.notification_manager.show_notification(
                "Preencha todos os campos",
                type_='warning'
            )
            return

        try:
            usuario = autenticar_usuario(username, senha)
            if usuario:
                logger.info(f"Login bem-sucedido: {username}")
                self.save_last_username(username if self.lembrar_usuario.get() else '')
                self.notification_manager.show_notification(
                    f"Bem-vindo, {usuario['username']}!",
                    type_='success'
                )
                self.root.after(1500, self.root.destroy)  # Delay to show notification
            else:
                logger.warning(f"Tentativa de login falha: {username}")
                self.notification_manager.show_notification(
                    "Usuário ou senha incorretos",
                    type_='error'
                )
                self.entrada_senha.delete(0, tk.END)
        except Exception as e:
            logger.error(f"Erro no login: {str(e)}")
            self.notification_manager.show_notification(
                "Erro ao realizar login",
                type_='error'
            )

    def save_last_username(self, username):
        """Save last used username if 'remember me' is checked"""
        try:
            with open('user_preferences.json', 'r+') as f:
                try:
                    prefs = json.load(f)
                except json.JSONDecodeError:
                    prefs = {}
                prefs['last_username'] = username
                f.seek(0)
                f.truncate()
                json.dump(prefs, f)
        except Exception as e:
            logger.error(f"Erro ao salvar preferências: {str(e)}")

    def load_last_username(self):
        """Load last used username if available"""
        try:
            if os.path.exists('user_preferences.json'):
                with open('user_preferences.json', 'r') as f:
                    prefs = json.load(f)
                    if 'last_username' in prefs:
                        self.entrada_usuario.insert(0, prefs['last_username'])
        except Exception as e:
            logger.error(f"Erro ao carregar preferências: {str(e)}")

    def abrir_cadastro(self):
        """Open the client registration window"""
        from clientes import gui_cadastrar_cliente
        gui_cadastrar_cliente()

    def run(self):
        """Start the login window"""
        self.root.mainloop()

if __name__ == "__main__":
    login = LoginWindow()
    login.run()
