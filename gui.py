import tkinter as tk
from tkinter import messagebox, filedialog, ttk
from PIL import Image, ImageTk
import produtos, relatorios, clientes
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import shutil
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import json
import database
import os
from typing import Optional, Dict, List
import threading
import queue
from utils import (
    THEMES, AsyncTask, ModernButton, Tooltip, 
    NotificationManager, SearchFrame, 
    save_user_preferences, load_user_preferences
)

class IntegrePlusGUI:
    def __init__(self):
        self.usuario_logado = None
        self.permissao_usuario = None
        self.tema_atual = load_user_preferences().get('tema', 'claro')
        self.notification_manager = None
        self.animations_enabled = True  # New flag to enable/disable animations
        
    def aplicar_tema(self, style, tema='claro'):
        """Apply theme colors to the GUI"""
        colors = THEMES[tema]
        style.theme_use('clam')
        
        # Configure colors for different widget types
        style.configure('.',
            background=colors['background'],
            foreground=colors['text'])
            
        style.configure('TButton',
            background=colors['accent'],
            foreground=colors['menu_fg'],
            font=("Arial", 12))
            
        style.configure('Sidebar.TButton',
            background=colors['menu_bg'],
            foreground=colors['menu_fg'],
            font=("Arial", 12, "bold"))
            
        style.configure('Card.TFrame',
            background=colors['card_bg'])
            
        # Configure hover styles
        style.map('TButton',
            background=[('active', colors['secondary'])],
            foreground=[('active', colors['menu_fg'])])
            
        self.root.configure(bg=colors['background'])
        save_user_preferences({'tema': tema})

    def alternar_tema(self):
        """Toggle between light and dark themes"""
        self.tema_atual = 'escuro' if self.tema_atual == 'claro' else 'claro'
        self.aplicar_tema(self.estilo, self.tema_atual)
        self.notification_manager.show_notification(
            f"Tema alterado para {self.tema_atual}",
            type_='info'
        )
        # Animate theme change if enabled
        if self.animations_enabled:
            self._animate_theme_change()

    def _animate_theme_change(self):
        """Simple fade animation for theme change"""
        alpha = 0.0
        step = 0.1
        def fade_in():
            nonlocal alpha
            alpha += step
            if alpha > 1.0:
                self.root.attributes('-alpha', 1.0)
                return
            self.root.attributes('-alpha', alpha)
            self.root.after(50, fade_in)
        self.root.attributes('-alpha', 0.0)
        fade_in()

    def criar_dashboard(self, parent):
        """Create an embedded dashboard with charts"""
        dashboard_frame = ttk.Frame(parent, style='Card.TFrame')
        dashboard_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Create figure with subplots
        fig = plt.figure(figsize=(12, 6))
        fig.patch.set_facecolor(THEMES[self.tema_atual]['background'])
        
        # Product stock chart
        ax1 = fig.add_subplot(121)
        self.atualizar_grafico_estoque(ax1)
        
        # Sales trend chart
        ax2 = fig.add_subplot(122)
        self.atualizar_grafico_vendas(ax2)
        
        # Embed the chart
        canvas = FigureCanvasTkAgg(fig, master=dashboard_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)
        
        # Add matplotlib toolbar
        toolbar = NavigationToolbar2Tk(canvas, dashboard_frame)
        toolbar.update()
        
        # Add refresh button
        refresh_btn = ModernButton(
            dashboard_frame,
            text="↻ Atualizar Gráficos",
            command=lambda: self.atualizar_dashboard(ax1, ax2, canvas)
        )
        refresh_btn.pack(pady=10)

        # Add simple fade-in animation for dashboard if enabled
        if self.animations_enabled:
            self._fade_in_widget(dashboard_frame)
        
        return dashboard_frame

    def _fade_in_widget(self, widget, step=0.1, delay=50):
        """Fade in a widget by gradually increasing its opacity"""
        # Tkinter does not support widget opacity, so simulate with gradual packing
        # This is a placeholder for more complex animation if using other GUI frameworks
        pass

    def atualizar_grafico_estoque(self, ax):
        """Update stock level chart"""
        try:
            dados = produtos.listar_produtos()
            if dados:
                nomes = [d['nome'] for d in dados]
                qtds = [d['quantidade'] for d in dados]
                
                ax.clear()
                bars = ax.bar(nomes, qtds, color=THEMES[self.tema_atual]['accent'])
                
                # Add value labels on top of bars
                for bar in bars:
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height,
                            f'{int(height)}',
                            ha='center', va='bottom')
                
                ax.set_title('Níveis de Estoque', color=THEMES[self.tema_atual]['text'])
                ax.set_xlabel('Produtos', color=THEMES[self.tema_atual]['text'])
                ax.set_ylabel('Quantidade', color=THEMES[self.tema_atual]['text'])
                ax.tick_params(axis='both', colors=THEMES[self.tema_atual]['text'])
                ax.set_xticks(range(len(nomes)))
                ax.set_xticklabels(nomes, rotation=45, ha='right')
        except Exception as e:
            self.notification_manager.show_notification(
                f"Erro ao atualizar gráfico de estoque: {str(e)}",
                type_='error'
            )

    def atualizar_grafico_vendas(self, ax):
        """Update sales trend chart"""
        try:
            # Get sales data from database (implement this in vendas.py)
            vendas = relatorios.obter_vendas_por_periodo()
            if vendas:
                datas = [v[0] for v in vendas]
                valores = [v[1] for v in vendas]
                
                ax.clear()
                ax.plot(datas, valores, marker='o', 
                       color=THEMES[self.tema_atual]['accent'],
                       linewidth=2)
                
                ax.set_title('Tendência de Vendas', color=THEMES[self.tema_atual]['text'])
                ax.set_xlabel('Data', color=THEMES[self.tema_atual]['text'])
                ax.set_ylabel('Valor Total (R$)', color=THEMES[self.tema_atual]['text'])
                ax.tick_params(axis='both', colors=THEMES[self.tema_atual]['text'])
                ax.grid(True, linestyle='--', alpha=0.7)
                
                # Rotate x-axis labels for better readability
                ax.set_xticklabels(datas, rotation=45, ha='right')
        except Exception as e:
            self.notification_manager.show_notification(
                f"Erro ao atualizar gráfico de vendas: {str(e)}",
                type_='error'
            )

    def atualizar_dashboard(self, ax1, ax2, canvas):
        """Update both dashboard charts"""
        self.atualizar_grafico_estoque(ax1)
        self.atualizar_grafico_vendas(ax2)
        canvas.draw()
        self.notification_manager.show_notification(
            "Dashboard atualizado com sucesso!",
            type_='success'
        )

    def criar_menu_lateral(self, parent):
        """Create enhanced sidebar menu with tooltips"""
        menu_frame = ttk.Frame(parent, style='Card.TFrame')
        menu_frame.pack(side="left", fill="y")

        # Menu title
        ttk.Label(menu_frame, 
                 text="MENU PRINCIPAL",
                 font=("Arial", 16, "bold"),
                 foreground=THEMES[self.tema_atual]['text']).pack(pady=20)

        # Menu buttons with tooltips
        botoes = [
            ("📦 Produtos", lambda: self.mostrar_produtos(), "Gerenciar produtos"),
            ("👥 Clientes", lambda: self.mostrar_clientes(), "Gerenciar clientes"),
            ("💰 Vendas", lambda: self.mostrar_vendas(), "Registrar vendas"),
            ("📊 Dashboard", lambda: self.mostrar_dashboard(), "Visualizar estatísticas"),
            ("📈 Relatórios", lambda: self.mostrar_relatorios(), "Gerar relatórios"),
            ("⚙️ Configurações", lambda: self.mostrar_configuracoes(), "Configurar sistema")
        ]

        for texto, comando, tooltip in botoes:
            btn = ModernButton(
                menu_frame,
                text=texto,
                command=comando,
                style='Sidebar.TButton',
                width=20
            )
            btn.pack(pady=5, padx=10)
            Tooltip(btn, tooltip)

        return menu_frame

    def criar_barra_superior(self):
        """Create enhanced top bar with user info and quick actions"""
        cabecalho = ttk.Frame(self.root, style='Card.TFrame')
        cabecalho.pack(fill="x", pady=5)

        # Logo/Title
        ttk.Label(
            cabecalho,
            text="Integre+ Adegas e Suplementos",
            font=("Arial", 22, "bold"),
            foreground=THEMES[self.tema_atual]['text']
        ).pack(side="left", padx=30)

        # User info
        info_usuario = f"👤 {self.usuario_logado} | 🔑 {self.permissao_usuario}"
        ttk.Label(
            cabecalho,
            text=info_usuario,
            font=("Arial", 12),
            foreground=THEMES[self.tema_atual]['text']
        ).pack(side="left", padx=20)

        # Quick action buttons
        ModernButton(
            cabecalho,
            text="🎨 Tema",
            command=self.alternar_tema,
            width=10
        ).pack(side="right", padx=5)

        ModernButton(
            cabecalho,
            text="↻ Atualizar",
            command=self.atualizar_interface,
            width=10
        ).pack(side="right", padx=5)

        ModernButton(
            cabecalho,
            text="🚪 Sair",
            command=self.logout,
            width=10
        ).pack(side="right", padx=5)

    def criar_barra_status(self):
        """Create enhanced status bar with system info"""
        status_bar = ttk.Frame(self.root, style='Card.TFrame')
        status_bar.pack(side="bottom", fill="x")

        # System info
        data_atual = datetime.now().strftime("%d/%m/%Y %H:%M")
        info = f"⏰ {data_atual} | 👤 {self.usuario_logado} | 💻 Integre+ v2.0"
        ttk.Label(
            status_bar,
            text=info,
            font=("Arial", 10),
            foreground=THEMES[self.tema_atual]['text']
        ).pack(side="left", padx=10, pady=2)

        # Add memory usage or other system stats here
        # ...

    def mostrar_produtos(self):
        """Show products management interface"""
        self.limpar_conteudo()
        frame = ttk.Frame(self.conteudo_frame, style='Card.TFrame')
        frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Add search and filter
        search_frame = SearchFrame(
            frame,
            search_callback=self.filtrar_produtos,
            filters={
                'categoria': ['Todos', 'Bebidas', 'Suplementos', 'Outros'],
                'ordenar': ['Nome ↑', 'Nome ↓', 'Preço ↑', 'Preço ↓']
            }
        )
        search_frame.pack(fill='x', padx=10, pady=5)

        # Products table with image preview column
        self.tabela_produtos = ttk.Treeview(
            frame,
            columns=('ID', 'Nome', 'Quantidade', 'Preço', 'Validade', 'Categoria', 'Código de Barras', 'Fornecedor'),
            show='headings'
        )
        
        for col in self.tabela_produtos['columns']:
            self.tabela_produtos.heading(col, text=col)
            self.tabela_produtos.column(col, width=100)

        self.tabela_produtos.pack(fill='both', expand=True, padx=10, pady=5)

        # Action buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill='x', padx=10, pady=5)

        ModernButton(
            btn_frame,
            text="➕ Novo Produto",
            command=lambda: produtos.gui_cadastrar_produto(tela_cheia=True)
        ).pack(side='left', padx=5)

        ModernButton(
            btn_frame,
            text="✏️ Editar",
            command=self.editar_produto_selecionado
        ).pack(side='left', padx=5)

        ModernButton(
            btn_frame,
            text="❌ Excluir",
            command=self.excluir_produto_selecionado
        ).pack(side='left', padx=5)

        # Load initial data
        self.carregar_produtos()

    def mostrar_clientes(self):
        """Show customers management interface"""
        self.limpar_conteudo()
        frame = ttk.Frame(self.conteudo_frame, style='Card.TFrame')
        frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Add search
        search_frame = SearchFrame(
            frame,
            search_callback=self.filtrar_clientes
        )
        search_frame.pack(fill='x', padx=10, pady=5)

        # Customers table
        self.tabela_clientes = ttk.Treeview(
            frame,
            columns=('ID', 'Nome', 'Email', 'Telefone', 'Endereço'),
            show='headings'
        )
        
        for col in self.tabela_clientes['columns']:
            self.tabela_clientes.heading(col, text=col)
            self.tabela_clientes.column(col, width=100)

        self.tabela_clientes.pack(fill='both', expand=True, padx=10, pady=5)

        # Action buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill='x', padx=10, pady=5)

        ModernButton(
            btn_frame,
            text="➕ Novo Cliente",
            command=lambda: clientes.gui_cadastrar_cliente(tela_cheia=True)
        ).pack(side='left', padx=5)

        ModernButton(
            btn_frame,
            text="✏️ Editar",
            command=self.editar_cliente_selecionado
        ).pack(side='left', padx=5)

        ModernButton(
            btn_frame,
            text="❌ Excluir",
            command=self.excluir_cliente_selecionado
        ).pack(side='left', padx=5)

        # Load initial data
        self.carregar_clientes()

    def mostrar_vendas(self):
        """Show sales interface"""
        self.limpar_conteudo()
        frame = ttk.Frame(self.conteudo_frame, style='Card.TFrame')
        frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Sales form
        form_frame = ttk.LabelFrame(frame, text="Nova Venda")
        form_frame.pack(fill='x', padx=10, pady=5)

        # Cliente
        ttk.Label(form_frame, text="Cliente:").grid(row=0, column=0, padx=5, pady=5)
        self.cliente_var = tk.StringVar()
        cliente_cb = ttk.Combobox(form_frame, textvariable=self.cliente_var)
        clientes_list = clientes.listar_clientes()
        cliente_cb['values'] = [c['nome'] if isinstance(c, dict) else c[1] for c in clientes_list]
        cliente_cb.grid(row=0, column=1, padx=5, pady=5)

        # Produto
        ttk.Label(form_frame, text="Produto:").grid(row=1, column=0, padx=5, pady=5)
        self.produto_var = tk.StringVar()
        produto_cb = ttk.Combobox(form_frame, textvariable=self.produto_var)
        produtos_list = produtos.listar_produtos()
        # Defensive check for dict or tuple and handle KeyError
        produto_names = []
        for p in produtos_list:
            try:
                if isinstance(p, dict):
                    produto_names.append(p['nome'])
                else:
                    produto_names.append(p[1])
            except (KeyError, IndexError):
                continue
        produto_cb['values'] = produto_names
        produto_cb.grid(row=1, column=1, padx=5, pady=5)

        # Quantidade
        ttk.Label(form_frame, text="Quantidade:").grid(row=2, column=0, padx=5, pady=5)
        self.qtd_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.qtd_var).grid(row=2, column=1, padx=5, pady=5)

        # Register sale button
        ModernButton(
            form_frame,
            text="💰 Registrar Venda",
            command=self.registrar_venda
        ).grid(row=3, column=0, columnspan=2, pady=10)

        # Recent sales
        sales_frame = ttk.LabelFrame(frame, text="Vendas Recentes")
        sales_frame.pack(fill='both', expand=True, padx=10, pady=5)

        self.tabela_vendas = ttk.Treeview(
            sales_frame,
            columns=('ID', 'Data', 'Cliente', 'Produto', 'Quantidade', 'Total'),
            show='headings'
        )
        
        for col in self.tabela_vendas['columns']:
            self.tabela_vendas.heading(col, text=col)
            self.tabela_vendas.column(col, width=100)

        self.tabela_vendas.pack(fill='both', expand=True, padx=5, pady=5)

        # Load recent sales
        self.carregar_vendas_recentes()

    def mostrar_dashboard(self):
        """Show dashboard interface"""
        self.limpar_conteudo()
        try:
            self.criar_dashboard(self.conteudo_frame)
        except Exception as e:
            self.notification_manager.show_notification(
                f"Erro ao atualizar gráfico de estoque: {str(e)}",
                type_='error'
            )
            self.notification_manager.show_notification(
                f"Erro ao atualizar gráfico de vendas: {str(e)}",
                type_='error'
            )

    def mostrar_relatorios(self):
        """Show reports interface"""
        self.limpar_conteudo()
        frame = ttk.Frame(self.conteudo_frame, style='Card.TFrame')
        frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Report options
        options_frame = ttk.LabelFrame(frame, text="Opções de Relatório")
        options_frame.pack(fill='x', padx=10, pady=5)

        # Date range
        ttk.Label(options_frame, text="Período:").grid(row=0, column=0, padx=5, pady=5)
        self.data_inicio = ttk.Entry(options_frame)
        self.data_inicio.grid(row=0, column=1, padx=5, pady=5)
        self.data_fim = ttk.Entry(options_frame)
        self.data_fim.grid(row=0, column=2, padx=5, pady=5)

        # Report type
        ttk.Label(options_frame, text="Tipo:").grid(row=1, column=0, padx=5, pady=5)
        self.tipo_relatorio = tk.StringVar(value="vendas")
        ttk.Radiobutton(options_frame, text="Vendas", variable=self.tipo_relatorio, 
                       value="vendas").grid(row=1, column=1)
        ttk.Radiobutton(options_frame, text="Estoque", variable=self.tipo_relatorio, 
                       value="estoque").grid(row=1, column=2)

        # Generate button
        ModernButton(
            options_frame,
            text="📊 Gerar Relatório",
            command=self.gerar_relatorio
        ).grid(row=2, column=0, columnspan=3, pady=10)

        # Preview area
        preview_frame = ttk.LabelFrame(frame, text="Prévia")
        preview_frame.pack(fill='both', expand=True, padx=10, pady=5)

        self.preview_text = tk.Text(preview_frame, height=20)
        self.preview_text.pack(fill='both', expand=True, padx=5, pady=5)

    def mostrar_configuracoes(self):
        """Show settings interface"""
        self.limpar_conteudo()
        frame = ttk.Frame(self.conteudo_frame, style='Card.TFrame')
        frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Appearance settings
        appearance_frame = ttk.LabelFrame(frame, text="Aparência")
        appearance_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(appearance_frame, text="Tema:").grid(row=0, column=0, padx=5, pady=5)
        tema_var = tk.StringVar(value=self.tema_atual)
        ttk.Radiobutton(appearance_frame, text="Claro", variable=tema_var, 
                       value="claro", command=lambda: self.aplicar_tema(self.estilo, "claro")
                       ).grid(row=0, column=1)
        ttk.Radiobutton(appearance_frame, text="Escuro", variable=tema_var,
                       value="escuro", command=lambda: self.aplicar_tema(self.estilo, "escuro")
                       ).grid(row=0, column=2)

        # Backup settings
        backup_frame = ttk.LabelFrame(frame, text="Backup")
        backup_frame.pack(fill='x', padx=10, pady=5)

        ModernButton(
            backup_frame,
            text="💾 Fazer Backup",
            command=self.backup_banco
        ).pack(pady=10)

        # User settings
        if self.permissao_usuario == "Admin":
            user_frame = ttk.LabelFrame(frame, text="Usuários")
            user_frame.pack(fill='x', padx=10, pady=5)

            ModernButton(
                user_frame,
                text="👤 Gerenciar Usuários",
                command=self.gerenciar_usuarios
            ).pack(pady=10)

    def limpar_conteudo(self):
        """Clear content area"""
        for widget in self.conteudo_frame.winfo_children():
            widget.destroy()

    def atualizar_interface(self):
        """Refresh current interface"""
        if hasattr(self, 'tabela_produtos'):
            self.carregar_produtos()
        if hasattr(self, 'tabela_clientes'):
            self.carregar_clientes()
        if hasattr(self, 'tabela_vendas'):
            self.carregar_vendas_recentes()
        
        self.notification_manager.show_notification(
            "Interface atualizada com sucesso!",
            type_='success'
        )

    def carregar_produtos(self):
        """Load products into table"""
        if hasattr(self, 'tabela_produtos') and self.tabela_produtos.winfo_exists():
            try:
                for item in self.tabela_produtos.get_children():
                    self.tabela_produtos.delete(item)
                
                for produto in produtos.listar_produtos():
                    # Normalize produto to tuple of values matching columns
                    if isinstance(produto, dict):
                        values = (
                            produto.get('id', ''),
                            produto.get('nome', ''),
                            produto.get('quantidade', ''),
                            f"R$ {produto.get('preco', 0):.2f}" if produto.get('preco') is not None else '',
                            produto.get('validade', ''),
                            produto.get('categoria', ''),
                            produto.get('codigo_barras', ''),
                            produto.get('fornecedor_id', '')
                        )
                    elif isinstance(produto, (list, tuple)):
                        values = produto
                    else:
                        values = (produto,)
                    self.tabela_produtos.insert('', 'end', values=values)
            except tk.TclError:
                # Widget has been destroyed, skip loading
                pass

    def carregar_clientes(self):
        """Load customers into table"""
        if hasattr(self, 'tabela_clientes') and self.tabela_clientes.winfo_exists():
            try:
                for item in self.tabela_clientes.get_children():
                    self.tabela_clientes.delete(item)
                
                for cliente in clientes.listar_clientes():
                    # Normalize cliente to tuple of values matching columns
                    if isinstance(cliente, dict):
                        values = (
                            cliente.get('id', ''),
                            cliente.get('nome', ''),
                            cliente.get('email', ''),
                            cliente.get('telefone', ''),
                            cliente.get('endereco', '')
                        )
                    elif isinstance(cliente, (list, tuple)):
                        values = cliente
                    else:
                        values = (cliente,)
                    self.tabela_clientes.insert('', 'end', values=values)
            except tk.TclError:
                # Widget has been destroyed, skip loading
                pass

    def carregar_vendas_recentes(self):
        """Load recent sales into table"""
        if hasattr(self, 'tabela_vendas') and self.tabela_vendas.winfo_exists():
            try:
                for item in self.tabela_vendas.get_children():
                    self.tabela_vendas.delete(item)
                
                # Implement this in vendas.py
                for venda in relatorios.obter_vendas_recentes():
                    self.tabela_vendas.insert('', 'end', values=venda)
            except tk.TclError:
                # Widget has been destroyed, skip loading
                pass

    def filtrar_produtos(self, termo_busca):
        """Filter products based on search term"""
        if hasattr(self, 'tabela_produtos') and self.tabela_produtos.winfo_exists():
            try:
                for item in self.tabela_produtos.get_children():
                    self.tabela_produtos.delete(item)
                
                for produto in produtos.buscar_produtos(termo_busca):
                    self.tabela_produtos.insert('', 'end', values=produto)
            except tk.TclError:
                # Widget has been destroyed, skip filtering
                pass

    def filtrar_clientes(self, termo_busca):
        """Filter customers based on search term"""
        if hasattr(self, 'tabela_clientes') and self.tabela_clientes.winfo_exists():
            try:
                for item in self.tabela_clientes.get_children():
                    self.tabela_clientes.delete(item)
                
                for cliente in clientes.buscar_clientes(termo_busca):
                    self.tabela_clientes.insert('', 'end', values=cliente)
            except tk.TclError:
                # Widget has been destroyed, skip filtering
                pass

    def editar_produto_selecionado(self):
        """Edit selected product"""
        selection = self.tabela_produtos.selection()
        if not selection:
            self.notification_manager.show_notification(
                "Selecione um produto para editar",
                type_='warning'
            )
            return
        
        item = self.tabela_produtos.item(selection[0])
        produtos.gui_atualizar_produto(item['values'][0])

    def excluir_produto_selecionado(self):
        """Delete selected product"""
        selection = self.tabela_produtos.selection()
        if not selection:
            self.notification_manager.show_notification(
                "Selecione um produto para excluir",
                type_='warning'
            )
            return
        
        if messagebox.askyesno("Confirmar", "Deseja realmente excluir este produto?"):
            item = self.tabela_produtos.item(selection[0])
            produtos.excluir_produto(item['values'][0])
            self.carregar_produtos()
            self.notification_manager.show_notification(
                "Produto excluído com sucesso!",
                type_='success'
            )

    def editar_cliente_selecionado(self):
        """Edit selected customer"""
        selection = self.tabela_clientes.selection()
        if not selection:
            self.notification_manager.show_notification(
                "Selecione um cliente para editar",
                type_='warning'
            )
            return
        
        item = self.tabela_clientes.item(selection[0])
        clientes.gui_atualizar_cliente(item['values'][0])

    def excluir_cliente_selecionado(self):
        """Delete selected customer"""
        selection = self.tabela_clientes.selection()
        if not selection:
            self.notification_manager.show_notification(
                "Selecione um cliente para excluir",
                type_='warning'
            )
            return
        
        if messagebox.askyesno("Confirmar", "Deseja realmente excluir este cliente?"):
            item = self.tabela_clientes.item(selection[0])
            clientes.excluir_cliente(item['values'][0])
            self.carregar_clientes()
            self.notification_manager.show_notification(
                "Cliente excluído com sucesso!",
                type_='success'
            )

    def registrar_venda(self):
        """Register new sale"""
        cliente = self.cliente_var.get()
        produto = self.produto_var.get()
        quantidade = self.qtd_var.get()

        if not all([cliente, produto, quantidade]):
            self.notification_manager.show_notification(
                "Preencha todos os campos!",
                type_='warning'
            )
            return

        try:
            quantidade = int(quantidade)
            # Implement this in vendas.py
            relatorios.registrar_venda(cliente, produto, quantidade)
            self.carregar_vendas_recentes()
            self.notification_manager.show_notification(
                "Venda registrada com sucesso!",
                type_='success'
            )
            # Clear form
            self.cliente_var.set('')
            self.produto_var.set('')
            self.qtd_var.set('')
        except ValueError:
            self.notification_manager.show_notification(
                "Quantidade inválida!",
                type_='error'
            )
        except Exception as e:
            self.notification_manager.show_notification(
                f"Erro ao registrar venda: {str(e)}",
                type_='error'
            )

    def gerar_relatorio(self):
        """Generate selected report"""
        tipo = self.tipo_relatorio.get()
        data_inicio = self.data_inicio.get()
        data_fim = self.data_fim.get()

        try:
            if tipo == "vendas":
                relatorio = relatorios.gerar_relatorio_vendas(data_inicio, data_fim)
            else:
                relatorio = relatorios.gerar_relatorio_estoque()

            self.preview_text.delete('1.0', tk.END)
            self.preview_text.insert('1.0', relatorio)
            
            self.notification_manager.show_notification(
                "Relatório gerado com sucesso!",
                type_='success'
            )
        except Exception as e:
            self.notification_manager.show_notification(
                f"Erro ao gerar relatório: {str(e)}",
                type_='error'
            )

    def backup_banco(self):
        """Create database backup"""
        try:
            nome_backup = f'backup_integre_plus_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'
            shutil.copy('integre_plus.db', nome_backup)
            self.notification_manager.show_notification(
                f"Backup criado: {nome_backup}",
                type_='success'
            )
        except Exception as e:
            self.notification_manager.show_notification(
                f"Erro ao criar backup: {str(e)}",
                type_='error'
            )

    def gerenciar_usuarios(self):
        """Show user management interface"""
        if self.permissao_usuario != "Admin":
            self.notification_manager.show_notification(
                "Acesso negado!",
                type_='error'
            )
            return

        # Implement user management interface
        pass

    def logout(self):
        """Logout current user"""
        if messagebox.askyesno("Logout", "Deseja realmente sair?"):
            self.root.destroy()
            # Import and start the modern login
            import login
            login.main()

    def main_gui(self, fullscreen=False):
        """Initialize main GUI"""
        self.root = tk.Tk()
        self.root.title("Integre+ Adegas e Suplementos")
        if fullscreen:
            self.root.attributes('-fullscreen', True)
        else:
            self.root.geometry("1024x768")

        # Initialize style
        self.estilo = ttk.Style()
        self.aplicar_tema(self.estilo, self.tema_atual)

        # Initialize notification manager
        self.notification_manager = NotificationManager(self.root)

        # Create main layout
        self.criar_barra_superior()
        
        # Main content area
        corpo = ttk.Frame(self.root)
        corpo.pack(fill="both", expand=True)
        
        self.criar_menu_lateral(corpo)
        
        # Content frame
        self.conteudo_frame = ttk.Frame(corpo, style='Card.TFrame')
        self.conteudo_frame.pack(side="left", fill="both", expand=True)
        
        # Create status bar
        self.criar_barra_status()
        
        # Show initial dashboard
        self.mostrar_dashboard()
        
        # Start main loop
        self.root.mainloop()

def gui_login():
    """Show login interface"""
    login = tk.Tk()
    login.title("Integre+ - Login")
    login.attributes('-fullscreen', True)
    login.configure(bg=THEMES['claro']['background'])

    # Initialize style
    style = ttk.Style()
    style.theme_use('clam')

    # Center frame
    frame = ttk.Frame(login, style='Card.TFrame')
    frame.place(relx=0.5, rely=0.5, anchor="center")

    # Logo/Title
    ttk.Label(
        frame,
        text="INTEGRE+",
        font=("Arial", 32, "bold"),
        foreground=THEMES['claro']['primary']
    ).pack(pady=20)
    
    ttk.Label(
        frame,
        text="Sistema de Gestão",
        font=("Arial", 16),
        foreground=THEMES['claro']['text']
    ).pack(pady=5)
    
    ttk.Label(
        frame,
        text="Adegas e Suplementos",
        font=("Arial", 16),
        foreground=THEMES['claro']['text']
    ).pack(pady=(0, 30))

    # Login fields
    ttk.Label(
        frame,
        text="Usuário:",
        font=("Arial", 14),
        foreground=THEMES['claro']['text']
    ).pack(anchor="w", pady=(10, 5))
    
    entry_user = ttk.Entry(frame, font=("Arial", 14), width=30)
    entry_user.pack(pady=(0, 10))

    ttk.Label(
        frame,
        text="Senha:",
        font=("Arial", 14),
        foreground=THEMES['claro']['text']
    ).pack(anchor="w", pady=(10, 5))
    
    entry_pass = ttk.Entry(frame, show="*", font=("Arial", 14), width=30)
    entry_pass.pack(pady=(0, 20))

    def fazer_login():
        user = entry_user.get().strip()
        senha = entry_pass.get()
        
        if not user or not senha:
            messagebox.showwarning("Campos obrigatórios", "Preencha todos os campos!")
            return
            
        usuario = clientes.autenticar_usuario(user, senha)
        if usuario:
            app = IntegrePlusGUI()
            app.usuario_logado = user
            app.permissao_usuario = usuario.get('permissao', 'Funcionario') if isinstance(usuario, dict) else 'Funcionario'
            login.destroy()
            app.main_gui()
        else:
            messagebox.showerror("Erro", "Usuário ou senha inválidos!")
            entry_pass.delete(0, tk.END)

    # Enter key binding
    entry_user.bind('<Return>', lambda e: entry_pass.focus())
    entry_pass.bind('<Return>', lambda e: fazer_login())

    # Buttons
    ModernButton(
        frame,
        text="🔑 Entrar",
        command=fazer_login,
        width=25
    ).pack(pady=10)
    
    ModernButton(
        frame,
        text="❌ Sair",
        command=login.destroy,
        width=25
    ).pack(pady=10)

    # Add close button to login screen
    ModernButton(
        frame,
        text="❌ Fechar Aplicativo",
        command=login.destroy,
        width=25
    ).pack(pady=10)

    # Focus username
    entry_user.focus()

    # Start login loop
    login.mainloop()

if __name__ == "__main__":
    # Initialize database
    database.create_tables()
    gui_login()
