"""
Enhanced GUI for Integre+ Application
Features modern design, dynamic theming, and improved user experience
"""
import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
from typing import Optional, Callable
from theme_manager import theme_manager
from dashboard import Dashboard
from config import get_ui_config
import produtos
import vendas
import clientes
import relatorios

class ModernGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.current_user = None
        self.dashboard = None
        self.setup_window()
        self.setup_styles()
        
    def setup_window(self):
        """Setup main window properties"""
        self.root.title("Integre+ - Sistema de Gestão")
        # Set fullscreen mode
        self.root.attributes('-fullscreen', True)
        
        # Configure window background
        self.root.configure(bg=theme_manager.get_colors()['background'])
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def center_window(self):
        """Center the window on screen"""
        # Not needed in fullscreen mode, so pass
        pass
        
    def setup_styles(self):
        """Setup ttk styles for consistent theming"""
        style = ttk.Style()
        colors = theme_manager.get_colors()
        
        # Configure ttk styles
        style.configure('Modern.TButton',
                       background=colors['primary'],
                       foreground='white',
                       font=('Arial', 10, 'bold'),
                       padding=(10, 5))
        
        style.configure('Success.TButton',
                       background=colors['success'],
                       foreground='white',
                       font=('Arial', 10, 'bold'),
                       padding=(10, 5))
        
        style.configure('Warning.TButton',
                       background=colors['warning'],
                       foreground='white',
                       font=('Arial', 10, 'bold'),
                       padding=(10, 5))
        
    def create_main_interface(self, username: str):
        """Create the main application interface"""
        self.current_user = username
        
        # Clear existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Create main layout
        self.create_header()
        self.create_sidebar()
        self.create_main_content()
        
        # Show dashboard by default
        self.show_dashboard()
        
    def create_header(self):
        """Create application header"""
        colors = theme_manager.get_colors()
        
        header_frame = tk.Frame(
            self.root,
            bg=colors['primary'],
            height=60
        )
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        # Logo and title
        title_frame = tk.Frame(header_frame, bg=colors['primary'])
        title_frame.pack(side='left', padx=20, pady=10)
        
        logo_label = tk.Label(
            title_frame,
            text="🏪",
            bg=colors['primary'],
            fg='white',
            font=('Arial', 24)
        )
        logo_label.pack(side='left')
        
        title_label = tk.Label(
            title_frame,
            text="INTEGRE+",
            bg=colors['primary'],
            fg='white',
            font=('Arial', 18, 'bold')
        )
        title_label.pack(side='left', padx=(10, 0))
        
        # User info and controls
        user_frame = tk.Frame(header_frame, bg=colors['primary'])
        user_frame.pack(side='right', padx=20, pady=10)
        
        # Theme toggle
        theme_btn = tk.Button(
            user_frame,
            text="🌓",
            command=self.toggle_theme,
            bg=colors['secondary'],
            fg='white',
            font=('Arial', 12),
            relief='flat',
            padx=10,
            cursor='hand2'
        )
        theme_btn.pack(side='right', padx=(10, 0))
        
        # User info
        user_label = tk.Label(
            user_frame,
            text=f"👤 {self.current_user}",
            bg=colors['primary'],
            fg='white',
            font=('Arial', 12)
        )
        user_label.pack(side='right')
        
        # Logout button
        logout_btn = tk.Button(
            user_frame,
            text="Sair",
            command=self.logout,
            bg=colors['error'],
            fg='white',
            font=('Arial', 10),
            relief='flat',
            padx=15,
            cursor='hand2'
        )
        logout_btn.pack(side='right', padx=(0, 10))
        
    def create_sidebar(self):
        """Create navigation sidebar"""
        colors = theme_manager.get_colors()
        
        self.sidebar_frame = tk.Frame(
            self.root,
            bg=colors['card_bg'],
            width=250,
            relief='raised',
            bd=1
        )
        self.sidebar_frame.pack(side='left', fill='y')
        self.sidebar_frame.pack_propagate(False)
        
        # Navigation title
        nav_title = tk.Label(
            self.sidebar_frame,
            text="📋 NAVEGAÇÃO",
            bg=colors['card_bg'],
            fg=colors['text'],
            font=('Arial', 14, 'bold'),
            pady=20
        )
        nav_title.pack(fill='x')
        
        # Navigation buttons
        nav_buttons = [
            ("📊", "Dashboard", self.show_dashboard),
            ("📦", "Produtos", self.show_produtos),
            ("💰", "Vendas", self.show_vendas),
            ("👥", "Clientes", self.show_clientes),
            ("📈", "Relatórios", self.show_relatorios),
            ("⚙️", "Configurações", self.show_configuracoes)
        ]
        
        self.nav_buttons = {}
        for icon, text, command in nav_buttons:
            btn = self.create_nav_button(icon, text, command)
            self.nav_buttons[text] = btn
        
        # Footer info
        footer_frame = tk.Frame(self.sidebar_frame, bg=colors['card_bg'])
        footer_frame.pack(side='bottom', fill='x', pady=20)
        
        version_label = tk.Label(
            footer_frame,
            text="Integre+ v2.0\n© 2024",
            bg=colors['card_bg'],
            fg=colors['text'],
            font=('Arial', 9),
            justify='center'
        )
        version_label.pack()
        
    def create_nav_button(self, icon: str, text: str, command: Callable):
        """Create a navigation button"""
        colors = theme_manager.get_colors()
        
        btn_frame = tk.Frame(self.sidebar_frame, bg=colors['card_bg'])
        btn_frame.pack(fill='x', padx=10, pady=2)
        
        btn = tk.Button(
            btn_frame,
            text=f"{icon} {text}",
            command=command,
            bg=colors['card_bg'],
            fg=colors['text'],
            font=('Arial', 12),
            relief='flat',
            anchor='w',
            padx=20,
            pady=10,
            cursor='hand2'
        )
        btn.pack(fill='x')
        
        # Hover effects
        def on_enter(e):
            btn.configure(bg=colors['primary'], fg='white')
        
        def on_leave(e):
            btn.configure(bg=colors['card_bg'], fg=colors['text'])
        
        btn.bind('<Enter>', on_enter)
        btn.bind('<Leave>', on_leave)
        
        return btn
        
    def create_main_content(self):
        """Create main content area"""
        colors = theme_manager.get_colors()
        
        self.content_frame = tk.Frame(
            self.root,
            bg=colors['background']
        )
        self.content_frame.pack(side='right', fill='both', expand=True)
        
    def show_dashboard(self):
        """Show dashboard"""
        self.highlight_nav_button("Dashboard")
        self.dashboard = Dashboard(self.content_frame)
        
    def show_produtos(self):
        """Show products management"""
        self.highlight_nav_button("Produtos")
        self.clear_content()
        
        # Create products interface
        produtos_frame = theme_manager.create_card_frame(
            self.content_frame, 
            "📦 GESTÃO DE PRODUTOS"
        )
        produtos_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Action buttons
        btn_frame = tk.Frame(produtos_frame, bg=theme_manager.get_colors()['card_bg'])
        btn_frame.pack(fill='x', pady=(0, 20))
        
        buttons = [
            ("➕ Cadastrar", produtos.gui_cadastrar_produto, 'success'),
            ("📋 Listar", produtos.gui_listar_produtos, 'primary'),
            ("✏️ Atualizar", produtos.gui_atualizar_produto, 'warning'),
            ("🗑️ Excluir", produtos.gui_excluir_produto, 'error')
        ]
        
        for text, command, style in buttons:
            btn = theme_manager.create_styled_button(
                btn_frame, text, command, style
            )
            btn.pack(side='left', padx=10)
        
        # Products list
        produtos.gui_listar_produtos(parent=produtos_frame)
        
    def show_vendas(self):
        """Show sales management"""
        self.highlight_nav_button("Vendas")
        self.clear_content()
        
        # Create sales interface
        vendas_frame = theme_manager.create_card_frame(
            self.content_frame,
            "💰 GESTÃO DE VENDAS"
        )
        vendas_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Action buttons
        btn_frame = tk.Frame(vendas_frame, bg=theme_manager.get_colors()['card_bg'])
        btn_frame.pack(fill='x', pady=(0, 20))
        
        buttons = [
            ("➕ Nova Venda", vendas.gui_registrar_venda, 'success'),
            ("📋 Histórico", vendas.gui_listar_vendas, 'primary'),
            ("📊 Exportar", lambda: vendas.exportar_vendas_excel(), 'warning')
        ]
        
        for text, command, style in buttons:
            btn = theme_manager.create_styled_button(
                btn_frame, text, command, style
            )
            btn.pack(side='left', padx=10)
        
        # Recent sales
        self.show_recent_sales(vendas_frame)
        
    def show_clientes(self):
        """Show clients management"""
        self.highlight_nav_button("Clientes")
        self.clear_content()
        
        # Create clients interface
        clientes_frame = theme_manager.create_card_frame(
            self.content_frame,
            "👥 GESTÃO DE CLIENTES"
        )
        clientes_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Action buttons
        btn_frame = tk.Frame(clientes_frame, bg=theme_manager.get_colors()['card_bg'])
        btn_frame.pack(fill='x', pady=(0, 20))
        
        buttons = [
            ("➕ Cadastrar", clientes.gui_cadastrar_cliente, 'success'),
            ("📋 Listar", clientes.gui_listar_clientes, 'primary'),
            ("✏️ Atualizar", clientes.gui_atualizar_cliente, 'warning'),
            ("🗑️ Excluir", clientes.gui_excluir_cliente, 'error')
        ]
        
        for text, command, style in buttons:
            btn = theme_manager.create_styled_button(
                btn_frame, text, command, style
            )
            btn.pack(side='left', padx=10)
        
        # Clients list
        self.show_clients_list(clientes_frame)
        
    def show_relatorios(self):
        """Show reports"""
        self.highlight_nav_button("Relatórios")
        self.clear_content()
        
        # Create reports interface
        relatorios_frame = theme_manager.create_card_frame(
            self.content_frame,
            "📈 RELATÓRIOS"
        )
        relatorios_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Report buttons
        btn_frame = tk.Frame(relatorios_frame, bg=theme_manager.get_colors()['card_bg'])
        btn_frame.pack(fill='x', pady=(0, 20))
        
        buttons = [
            ("📊 Vendas", relatorios.gui_relatorio_vendas, 'primary'),
            ("📦 Estoque", relatorios.gui_relatorio_estoque, 'success'),
            ("👥 Clientes", relatorios.gui_relatorio_clientes, 'warning'),
            ("💰 Financeiro", relatorios.gui_relatorio_financeiro, 'secondary')
        ]
        
        for text, command, style in buttons:
            btn = theme_manager.create_styled_button(
                btn_frame, text, command, style
            )
            btn.pack(side='left', padx=10)
        
    def show_configuracoes(self):
        """Show settings"""
        self.highlight_nav_button("Configurações")
        self.clear_content()
        
        # Create settings interface
        config_frame = theme_manager.create_card_frame(
            self.content_frame,
            "⚙️ CONFIGURAÇÕES"
        )
        config_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Settings options
        settings_options = [
            ("🌓 Alternar Tema", self.toggle_theme),
            ("🔄 Atualizar Dashboard", self.refresh_dashboard),
            ("📊 Backup Dados", self.backup_data),
            ("ℹ️ Sobre o Sistema", self.show_about)
        ]
        
        for text, command in settings_options:
            btn = theme_manager.create_styled_button(
                config_frame, text, command, 'secondary'
            )
            btn.pack(pady=10, anchor='w')
        
    def show_recent_sales(self, parent):
        """Show recent sales in the sales section"""
        recent_frame = tk.Frame(parent, bg=theme_manager.get_colors()['card_bg'])
        recent_frame.pack(fill='both', expand=True, pady=(20, 0))
        
        title_label = tk.Label(
            recent_frame,
            text="📋 Vendas Recentes",
            bg=theme_manager.get_colors()['card_bg'],
            fg=theme_manager.get_colors()['text'],
            font=('Arial', 14, 'bold')
        )
        title_label.pack(anchor='w', pady=(0, 10))
        
        # Create treeview for recent sales
        columns = ('Data', 'Produto', 'Quantidade', 'Total')
        tree = ttk.Treeview(recent_frame, columns=columns, show='headings', height=8)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, anchor='center', width=150)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(recent_frame, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack widgets
        tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Load recent sales data
        try:
            vendas_recentes = vendas.listar_vendas()[:10]  # Last 10 sales
            for venda in vendas_recentes:
                tree.insert('', 'end', values=(
                    venda['data'][:16] if venda['data'] else '',
                    venda['produto'],
                    venda['quantidade'],
                    f"R$ {venda['total']:.2f}"
                ))
        except Exception as e:
            print(f"Erro ao carregar vendas recentes: {e}")
    
    def show_clients_list(self, parent):
        """Show clients list in the clients section"""
        clients_frame = tk.Frame(parent, bg=theme_manager.get_colors()['card_bg'])
        clients_frame.pack(fill='both', expand=True, pady=(20, 0))
        
        title_label = tk.Label(
            clients_frame,
            text="📋 Lista de Clientes",
            bg=theme_manager.get_colors()['card_bg'],
            fg=theme_manager.get_colors()['text'],
            font=('Arial', 14, 'bold')
        )
        title_label.pack(anchor='w', pady=(0, 10))
        
        # Create treeview for clients
        columns = ('ID', 'Nome', 'Email', 'Telefone')
        tree = ttk.Treeview(clients_frame, columns=columns, show='headings', height=10)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, anchor='center', width=150)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(clients_frame, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack widgets
        tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Load clients data
        try:
            clientes_list = clientes.listar_clientes()
            for cliente in clientes_list:
                tree.insert('', 'end', values=(
                    cliente.get('id', ''),
                    cliente.get('nome', ''),
                    cliente.get('email', ''),
                    cliente.get('telefone', '')
                ))
        except Exception as e:
            print(f"Erro ao carregar clientes: {e}")
    
    def highlight_nav_button(self, active_button: str):
        """Highlight the active navigation button"""
        colors = theme_manager.get_colors()
        
        for name, btn in self.nav_buttons.items():
            if name == active_button:
                btn.configure(bg=colors['primary'], fg='white')
            else:
                btn.configure(bg=colors['card_bg'], fg=colors['text'])
    
    def clear_content(self):
        """Clear the main content area"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def toggle_theme(self):
        """Toggle application theme"""
        theme_manager.toggle_theme()
        self.setup_styles()
        
        # Refresh current view
        if hasattr(self, 'dashboard') and self.dashboard:
            self.show_dashboard()
        else:
            # Recreate the interface with new theme
            self.create_main_interface(self.current_user)
    
    def refresh_dashboard(self):
        """Refresh dashboard data"""
        if hasattr(self, 'dashboard') and self.dashboard:
            self.dashboard.refresh_data()
            messagebox.showinfo("Sucesso", "Dashboard atualizado com sucesso!")
    
    def backup_data(self):
        """Create data backup"""
        try:
            # Simple backup implementation
            import shutil
            from datetime import datetime
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"backup_integre_plus_{timestamp}.db"
            shutil.copy2("integre_plus.db", backup_name)
            
            messagebox.showinfo("Sucesso", f"Backup criado: {backup_name}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao criar backup: {str(e)}")
    
    def show_about(self):
        """Show about dialog"""
        about_text = """
        Integre+ v2.0
        Sistema de Gestão Empresarial
        
        Desenvolvido com Python e Tkinter
        
        Funcionalidades:
        • Gestão de Produtos
        • Controle de Vendas
        • Cadastro de Clientes
        • Relatórios Dinâmicos
        • Dashboard Interativo
        • Temas Personalizáveis
        
        © 2024 - Todos os direitos reservados
        """
        
        messagebox.showinfo("Sobre o Integre+", about_text)
    
    def logout(self):
        """Logout user and return to login"""
        if messagebox.askyesno("Confirmar", "Deseja realmente sair do sistema?"):
            self.root.destroy()
            # Restart login - this would typically restart the application
            os.system("python main.py")
    
    def on_closing(self):
        """Handle window closing"""
        if messagebox.askyesno("Sair", "Deseja realmente fechar o sistema?"):
            self.root.destroy()
            sys.exit()
    
    def run(self):
        """Start the GUI application"""
        self.root.mainloop()

# Create global GUI instance
gui = ModernGUI()
