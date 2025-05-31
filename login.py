"""
Modern login interface for Integre+ application.
Handles user authentication with beautiful fullscreen design.
"""
import tkinter as tk
from tkinter import ttk, messagebox
import logging
import json
import os
import bcrypt
from datetime import datetime

from database import execute_query
from theme_manager import theme_manager
from utils import (
    ModernCard, ModernEntry, AnimatedButton, 
    NotificationManager, LoadingSpinner, THEME_COLORS
)

logger = logging.getLogger(__name__)

def verificar_credenciais(username: str, password: str) -> dict:
    """Verify user credentials and return user data"""
    try:
        # First get the stored hash for the username
        get_hash_query = """
            SELECT id, username, email, permissao, ultimo_login, senha, bloqueado
            FROM usuarios 
            WHERE username = ? AND bloqueado = 0
        """
        result = execute_query(get_hash_query, (username,), fetch=True)
        
        if not result:
            # Increment failed attempts
            increment_query = """
                UPDATE usuarios 
                SET tentativas_login = tentativas_login + 1 
                WHERE username = ?
            """
            execute_query(increment_query, (username,))
            return None
            
        user_data = result[0]
        stored_hash = user_data['senha']
        
        # Verify the password
        if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
            # Update last login
            update_query = """
                UPDATE usuarios 
                SET ultimo_login = ?, tentativas_login = 0 
                WHERE id = ?
            """
            execute_query(update_query, (datetime.now().isoformat(), user_data['id']))
            return user_data
        else:
            # Increment failed attempts
            increment_query = """
                UPDATE usuarios 
                SET tentativas_login = tentativas_login + 1 
                WHERE username = ?
            """
            execute_query(increment_query, (username,))
            return None
            
    except Exception as e:
        logger.error(f"Error verifying credentials: {e}")
        return None

class ModernLoginWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.current_theme = theme_manager.current_theme
        self.colors = theme_manager.get_colors()
        
        self.setup_window()
        self.create_interface()
        
        # Initialize notification manager
        self.notification_manager = NotificationManager(self.root)
        
        # Bind keyboard shortcuts
        self.root.bind('<Return>', lambda e: self.fazer_login())
        self.root.bind('<Escape>', lambda e: self.toggle_fullscreen())
        self.root.bind('<F11>', lambda e: self.toggle_fullscreen())
        
        # Load saved preferences
        self.load_preferences()
        
    def setup_window(self):
        """Configure the main window"""
        self.root.title("Integre+ - Sistema de Gestão Empresarial")
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg=self.colors['background'])
        
        # Set window icon if available
        try:
            self.root.iconbitmap('icon.ico')
        except:
            pass
    
    def toggle_fullscreen(self):
        """Toggle fullscreen mode"""
        current_state = self.root.attributes('-fullscreen')
        self.root.attributes('-fullscreen', not current_state)
        
    def create_interface(self):
        """Create the modern login interface"""
        # Main container with gradient background
        main_container = tk.Frame(self.root, bg=self.colors['background'])
        main_container.pack(fill='both', expand=True)
        
        # Left side - Branding and features
        self.create_branding_section(main_container)
        
        # Right side - Login form
        self.create_login_section(main_container)
        
        # Top bar with controls
        self.create_top_bar(main_container)
        
        # Bottom status bar
        self.create_status_bar(main_container)
    
    def create_top_bar(self, parent):
        """Create top control bar"""
        top_bar = tk.Frame(parent, bg=self.colors['background'], height=50)
        top_bar.pack(side='top', fill='x')
        top_bar.pack_propagate(False)
        
        # Theme toggle button
        theme_btn = AnimatedButton(
            top_bar,
            text=f"🌓 {self.current_theme.title()}",
            bg=self.colors['secondary'],
            fg='white',
            font=('Segoe UI', 10, 'bold'),
            relief='flat',
            padx=15,
            pady=5,
            command=self.toggle_theme,
            hover_bg=self.colors['primary']
        )
        theme_btn.pack(side='right', padx=20, pady=10)
        
        # Fullscreen toggle
        fullscreen_btn = AnimatedButton(
            top_bar,
            text="⛶ Tela Cheia",
            bg=self.colors['secondary'],
            fg='white',
            font=('Segoe UI', 10, 'bold'),
            relief='flat',
            padx=15,
            pady=5,
            command=self.toggle_fullscreen,
            hover_bg=self.colors['primary']
        )
        fullscreen_btn.pack(side='right', padx=5, pady=10)
        
        # Close button
        close_btn = AnimatedButton(
            top_bar,
            text="✕ Fechar",
            bg=self.colors['error'],
            fg='white',
            font=('Segoe UI', 10, 'bold'),
            relief='flat',
            padx=15,
            pady=5,
            command=self.root.quit,
            hover_bg='#c0392b'
        )
        close_btn.pack(side='right', padx=5, pady=10)
    
    def create_branding_section(self, parent):
        """Create the left branding section"""
        branding_frame = tk.Frame(parent, bg=self.colors['background'])
        branding_frame.pack(side='left', fill='both', expand=True)
        
        # Center content
        center_frame = tk.Frame(branding_frame, bg=self.colors['background'])
        center_frame.place(relx=0.5, rely=0.5, anchor='center')
        
        # Logo and title
        logo_frame = tk.Frame(center_frame, bg=self.colors['background'])
        logo_frame.pack(pady=(0, 30))
        
        # Animated logo
        logo_label = tk.Label(
            logo_frame,
            text="🏪",
            bg=self.colors['background'],
            fg=self.colors['primary'],
            font=('Segoe UI', 80, 'bold')
        )
        logo_label.pack()
        
        # Main title with gradient effect
        title_label = tk.Label(
            logo_frame,
            text="INTEGRE+",
            bg=self.colors['background'],
            fg=self.colors['primary'],
            font=('Segoe UI', 48, 'bold')
        )
        title_label.pack(pady=(10, 5))
        
        # Subtitle
        subtitle_label = tk.Label(
            logo_frame,
            text="Sistema de Gestão Empresarial",
            bg=self.colors['background'],
            fg=self.colors['text_secondary'],
            font=('Segoe UI', 18)
        )
        subtitle_label.pack(pady=(0, 5))
        
        # Version
        version_label = tk.Label(
            logo_frame,
            text="Versão 2.0 - Edição Profissional",
            bg=self.colors['background'],
            fg=self.colors['text_secondary'],
            font=('Segoe UI', 12)
        )
        version_label.pack()
        
        # Features showcase
        features_frame = ModernCard(center_frame, theme=self.current_theme)
        features_frame.pack(pady=30, padx=20)
        
        features_title = tk.Label(
            features_frame,
            text="✨ Funcionalidades Principais",
            bg=self.colors['card_bg'],
            fg=self.colors['text'],
            font=('Segoe UI', 16, 'bold')
        )
        features_title.pack(pady=(0, 15))
        
        features = [
            "📊 Dashboard Interativo e Analítico",
            "📦 Gestão Completa de Produtos",
            "👥 Controle de Clientes e Fornecedores",
            "💰 Sistema de Vendas Integrado",
            "📈 Relatórios Dinâmicos e Exportação",
            "🔒 Sistema de Segurança Avançado",
            "🎨 Interface Moderna e Responsiva",
            "☁️ Backup Automático de Dados"
        ]
        
        for feature in features:
            feature_label = tk.Label(
                features_frame,
                text=feature,
                bg=self.colors['card_bg'],
                fg=self.colors['text'],
                font=('Segoe UI', 12),
                anchor='w'
            )
            feature_label.pack(fill='x', pady=3)
    
    def create_login_section(self, parent):
        """Create the right login section"""
        login_frame = tk.Frame(parent, bg=self.colors['card_bg'], width=500)
        login_frame.pack(side='right', fill='y')
        login_frame.pack_propagate(False)
        
        # Login card
        login_card = tk.Frame(login_frame, bg=self.colors['card_bg'])
        login_card.place(relx=0.5, rely=0.5, anchor='center', width=400)
        
        # Header
        header_frame = tk.Frame(login_card, bg=self.colors['card_bg'])
        header_frame.pack(fill='x', pady=(0, 40))
        
        # Login title
        title_label = tk.Label(
            header_frame,
            text="Acesso ao Sistema",
            bg=self.colors['card_bg'],
            fg=self.colors['text'],
            font=('Segoe UI', 28, 'bold')
        )
        title_label.pack()
        
        subtitle_label = tk.Label(
            header_frame,
            text="Entre com suas credenciais",
            bg=self.colors['card_bg'],
            fg=self.colors['text_secondary'],
            font=('Segoe UI', 14)
        )
        subtitle_label.pack(pady=(5, 0))
        
        # Form fields
        form_frame = tk.Frame(login_card, bg=self.colors['card_bg'])
        form_frame.pack(fill='x', pady=(0, 30))
        
        # Username field
        user_label = tk.Label(
            form_frame,
            text="👤 Usuário",
            bg=self.colors['card_bg'],
            fg=self.colors['text'],
            font=('Segoe UI', 12, 'bold')
        )
        user_label.pack(anchor='w', pady=(0, 8))
        
        self.username_entry = ModernEntry(
            form_frame,
            placeholder="Digite seu usuário",
            theme=self.current_theme,
            width=30
        )
        self.username_entry.pack(fill='x', ipady=12, pady=(0, 20))
        
        # Password field
        pass_label = tk.Label(
            form_frame,
            text="🔒 Senha",
            bg=self.colors['card_bg'],
            fg=self.colors['text'],
            font=('Segoe UI', 12, 'bold')
        )
        pass_label.pack(anchor='w', pady=(0, 8))
        
        self.password_entry = ModernEntry(
            form_frame,
            placeholder="Digite sua senha",
            theme=self.current_theme,
            show="•",
            width=30
        )
        self.password_entry.pack(fill='x', ipady=12, pady=(0, 20))
        
        # Remember me checkbox
        remember_frame = tk.Frame(form_frame, bg=self.colors['card_bg'])
        remember_frame.pack(fill='x', pady=(0, 25))
        
        self.remember_var = tk.BooleanVar(value=True)
        remember_check = tk.Checkbutton(
            remember_frame,
            text="Lembrar usuário",
            variable=self.remember_var,
            bg=self.colors['card_bg'],
            fg=self.colors['text_secondary'],
            selectcolor=self.colors['card_bg'],
            activebackground=self.colors['card_bg'],
            activeforeground=self.colors['text'],
            font=('Segoe UI', 11),
            bd=0
        )
        remember_check.pack(anchor='w')
        
        # Buttons
        buttons_frame = tk.Frame(form_frame, bg=self.colors['card_bg'])
        buttons_frame.pack(fill='x')
        
        # Login button
        self.login_btn = AnimatedButton(
            buttons_frame,
            text="🚀 ENTRAR",
            bg=self.colors['primary'],
            fg='white',
            font=('Segoe UI', 14, 'bold'),
            relief='flat',
            command=self.fazer_login,
            hover_bg=self.colors['hover']
        )
        self.login_btn.pack(fill='x', ipady=15, pady=(0, 15))
        
        # Register button
        register_btn = AnimatedButton(
            buttons_frame,
            text="👤 Criar Nova Conta",
            bg=self.colors['secondary'],
            fg='white',
            font=('Segoe UI', 12),
            relief='flat',
            command=self.abrir_cadastro,
            hover_bg=self.colors['primary']
        )
        register_btn.pack(fill='x', ipady=12, pady=(0, 20))

        # Exit application button
        exit_btn = AnimatedButton(
            buttons_frame,
            text="❌ Sair do Aplicativo",
            bg=self.colors['error'],
            fg='white',
            font=('Segoe UI', 12, 'bold'),
            relief='flat',
            command=self.root.quit,
            hover_bg='#c0392b'
        )
        exit_btn.pack(fill='x', ipady=12, pady=(0, 20))
        
        # Info section
        info_frame = ModernCard(login_card, theme=self.current_theme)
        info_frame.pack(fill='x', pady=(20, 0))
        
        info_title = tk.Label(
            info_frame,
            text="ℹ️ Credenciais Padrão",
            bg=self.colors['card_bg'],
            fg=self.colors['text'],
            font=('Segoe UI', 12, 'bold')
        )
        info_title.pack()
        
        info_text = tk.Label(
            info_frame,
            text="Usuário: admin\nSenha: admin123",
            bg=self.colors['card_bg'],
            fg=self.colors['text_secondary'],
            font=('Segoe UI', 11),
            justify='center'
        )
        info_text.pack(pady=(5, 0))
        
        # Focus on username
        self.username_entry.focus()
        
        # Bind Enter key to password field
        self.password_entry.bind('<Return>', lambda e: self.fazer_login())
    
    def create_status_bar(self, parent):
        """Create bottom status bar"""
        status_bar = tk.Frame(parent, bg=self.colors['card_bg'], height=40)
        status_bar.pack(side='bottom', fill='x')
        status_bar.pack_propagate(False)
        
        # Status info
        status_text = f"⏰ {datetime.now().strftime('%d/%m/%Y %H:%M')} | 💻 Integre+ v2.0 | 🎨 Tema: {self.current_theme.title()}"
        status_label = tk.Label(
            status_bar,
            text=status_text,
            bg=self.colors['card_bg'],
            fg=self.colors['text_secondary'],
            font=('Segoe UI', 10)
        )
        status_label.pack(side='left', padx=20, pady=10)
        
        # Loading spinner (hidden by default)
        self.loading_spinner = LoadingSpinner(status_bar, size=30, theme=self.current_theme)
        self.loading_spinner.place(relx=1, rely=0.5, anchor='e', x=-50)
    
    def toggle_theme(self):
        """Toggle between light and dark themes"""
        theme_manager.toggle_theme()
        self.current_theme = theme_manager.current_theme
        self.colors = theme_manager.get_colors()
        
        # Recreate interface with new theme
        for widget in self.root.winfo_children():
            widget.destroy()
        
        self.create_interface()
        self.notification_manager = NotificationManager(self.root)
        self.load_preferences()
        
        self.show_notification(f"Tema alterado para {self.current_theme.title()}", 'success')
    
    def fazer_login(self):
        """Handle login attempt"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        # Remove placeholder text if present
        if username == "Digite seu usuário":
            username = ""
        if password == "Digite sua senha":
            password = ""
        
        if not username or not password:
            self.show_notification("Por favor, preencha todos os campos", 'warning')
            return
        
        # Show loading
        self.login_btn.configure(text="🔄 Verificando...", state='disabled')
        self.loading_spinner.start()
        
        # Cancel any previous pending login callbacks
        if hasattr(self, '_login_after_id'):
            self.root.after_cancel(self._login_after_id)
        
        # Simulate async login (in real app, use threading)
        self._login_after_id = self.root.after(1000, lambda: self._process_login(username, password))
    
    def _process_login(self, username, password):
        """Process login credentials"""
        try:
            user_data = verificar_credenciais(username, password)
            
            if user_data:
                logger.info(f"Successful login for user: {username}")
                
                # Save preferences if remember is checked
                if self.remember_var.get():
                    self.save_preferences(username)
                else:
                    self.save_preferences("")
                
                self.show_notification(f"Bem-vindo, {user_data['username']}!", 'success')
                
                # Cancel any previous pending open app callbacks
                if hasattr(self, '_open_app_after_id'):
                    self.root.after_cancel(self._open_app_after_id)
                
                # Start main application after delay
                self._open_app_after_id = self.root.after(1500, lambda: self.abrir_aplicacao_principal(user_data))
                
            else:
                logger.warning(f"Failed login attempt for user: {username}")
                self.show_notification("Usuário ou senha incorretos", 'error')
                self.password_entry.delete(0, tk.END)
                self.password_entry.focus()
                
        except Exception as e:
            logger.error(f"Login error: {e}")
            self.show_notification("Erro interno do sistema", 'error')
        
        finally:
            # Hide loading
            self.login_btn.configure(text="🚀 ENTRAR", state='normal')
            self.loading_spinner.stop()
    
    def abrir_aplicacao_principal(self, user_data):
        """Open main application"""
        try:
            from gui import IntegrePlusGUI
            
            # Hide login window
            self.root.withdraw()
            
            # Create main application
            app = IntegrePlusGUI()
            app.usuario_logado = user_data['username']
            app.permissao_usuario = user_data.get('permissao', 'Funcionario')
            
            # Start main GUI
            app.main_gui()
            
            # Close login window
            self.root.destroy()
            
        except Exception as e:
            logger.error(f"Error opening main application: {e}")
            self.show_notification("Erro ao abrir aplicação principal", 'error')
            self.root.deiconify()
    
    def abrir_cadastro(self):
        """Open user registration"""
        try:
            import tkinter as tk
            from tkinter import ttk, messagebox
            from clientes import cadastrar_usuario, UserError, PasswordError, validar_email, validar_senha
            from utils import ModernButton

            def salvar_usuario():
                username = entry_username.get().strip()
                email = entry_email.get().strip()
                senha = entry_password.get().strip()
                senha_confirm = entry_password_confirm.get().strip()

                if not username or not email or not senha or not senha_confirm:
                    messagebox.showwarning("Aviso", "Todos os campos são obrigatórios.")
                    return

                if senha != senha_confirm:
                    messagebox.showerror("Erro", "As senhas não coincidem.")
                    return

                try:
                    validar_email(email)
                    validar_senha(senha)
                    cadastrar_usuario(username, senha, email)
                    messagebox.showinfo("Sucesso", "Usuário cadastrado com sucesso!")
                    janela.destroy()
                except UserError as ue:
                    messagebox.showerror("Erro", str(ue))
                except PasswordError as pe:
                    messagebox.showerror("Erro", str(pe))
                except Exception as e:
                    messagebox.showerror("Erro", f"Erro ao cadastrar usuário: {e}")

            janela = tk.Toplevel(self.root)
            janela.title("Cadastro de Usuário")
            janela.geometry("400x400")
            janela.configure(bg=self.colors['background'])

            frame = ttk.Frame(janela, padding=20)
            frame.pack(fill='both', expand=True)

            ttk.Label(frame, text="Nome de Usuário:").pack(anchor='w', pady=(0, 5))
            entry_username = ttk.Entry(frame, width=30)
            entry_username.pack(pady=(0, 15))

            ttk.Label(frame, text="Email:").pack(anchor='w', pady=(0, 5))
            entry_email = ttk.Entry(frame, width=30)
            entry_email.pack(pady=(0, 15))

            ttk.Label(frame, text="Senha:").pack(anchor='w', pady=(0, 5))
            entry_password = ttk.Entry(frame, width=30, show="*")
            entry_password.pack(pady=(0, 15))

            ttk.Label(frame, text="Confirmar Senha:").pack(anchor='w', pady=(0, 5))
            entry_password_confirm = ttk.Entry(frame, width=30, show="*")
            entry_password_confirm.pack(pady=(0, 15))

            ModernButton(frame, text="Cadastrar", command=salvar_usuario, width=20).pack(pady=(10, 5))
            ModernButton(frame, text="Cancelar", command=janela.destroy, width=20).pack()

        except Exception as e:
            logger.error(f"Error opening registration: {e}")
            self.show_notification("Erro ao abrir cadastro", 'error')
    
    def show_notification(self, message, type_='info'):
        """Show notification message"""
        self.notification_manager.show_notification(message, type_)
    
    def save_preferences(self, username):
        """Save user preferences"""
        try:
            preferences = {
                'last_username': username,
                'theme': self.current_theme,
                'last_login': datetime.now().isoformat()
            }
            
            with open('user_preferences.json', 'w') as f:
                json.dump(preferences, f)
                
        except Exception as e:
            logger.error(f"Error saving preferences: {e}")
    
    def load_preferences(self):
        """Load saved preferences"""
        try:
            if os.path.exists('user_preferences.json'):
                with open('user_preferences.json', 'r') as f:
                    preferences = json.load(f)
                    
                    # Load last username
                    last_username = preferences.get('last_username', '')
                    if last_username and hasattr(self, 'username_entry'):
                        self.username_entry.delete(0, tk.END)
                        self.username_entry.insert(0, last_username)
                        if hasattr(self, 'password_entry'):
                            self.password_entry.focus()
                            
        except Exception as e:
            logger.error(f"Error loading preferences: {e}")
    
    def run(self):
        """Start the login window"""
        self.root.mainloop()

def main():
    """Main entry point for login"""
    try:
        # Initialize database
        from database import create_tables
        create_tables()
        
        # Create and run login window
        login = ModernLoginWindow()
        login.run()
        
    except Exception as e:
        logger.error(f"Critical error in login: {e}")
        messagebox.showerror("Erro Crítico", f"Erro ao iniciar login: {str(e)}")

if __name__ == "__main__":
    main()
