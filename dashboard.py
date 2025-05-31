"""
Enhanced Dashboard for Integre+ Application
Features dynamic charts, real-time data, and modern UI
"""
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import pandas as pd
from datetime import datetime, timedelta
from database import execute_query
from theme_manager import theme_manager
import numpy as np
from typing import Dict, List, Any

class Dashboard:
    def __init__(self, parent):
        self.parent = parent
        self.colors = theme_manager.get_colors()
        self.setup_dashboard()
        
    def setup_dashboard(self):
        """Setup the main dashboard layout"""
        # Clear existing widgets
        for widget in self.parent.winfo_children():
            widget.destroy()
        
        # Main container
        main_frame = tk.Frame(self.parent, bg=self.colors['background'])
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(
            main_frame,
            text="📊 DASHBOARD INTEGRE+",
            bg=self.colors['background'],
            fg=self.colors['text'],
            font=('Arial', 20, 'bold')
        )
        title_label.pack(pady=(0, 20))
        
        # Theme toggle button
        theme_btn = theme_manager.create_styled_button(
            main_frame,
            f"🌓 Tema: {theme_manager.current_theme.title()}",
            command=self.toggle_theme,
            style='secondary'
        )
        theme_btn.pack(anchor='ne', padx=(0, 20))
        
        # Stats cards row
        stats_frame = tk.Frame(main_frame, bg=self.colors['background'])
        stats_frame.pack(fill='x', pady=(0, 20))
        
        self.create_stats_cards(stats_frame)
        
        # Charts row
        charts_frame = tk.Frame(main_frame, bg=self.colors['background'])
        charts_frame.pack(fill='both', expand=True)
        
        self.create_charts(charts_frame)
        
        # Recent activity
        activity_frame = theme_manager.create_card_frame(main_frame, "📋 Atividade Recente")
        activity_frame.pack(fill='x', pady=(20, 0))
        
        self.create_recent_activity(activity_frame)
        
    def create_stats_cards(self, parent):
        """Create statistics cards"""
        stats = self.get_dashboard_stats()
        
        cards_data = [
            ("💰", "Vendas Hoje", f"R$ {stats['vendas_hoje']:.2f}", 'success'),
            ("📦", "Produtos", str(stats['total_produtos']), 'primary'),
            ("👥", "Clientes", str(stats['total_clientes']), 'secondary'),
            ("⚠️", "Estoque Baixo", str(stats['estoque_baixo']), 'warning')
        ]
        
        for i, (icon, title, value, style) in enumerate(cards_data):
            card = self.create_stat_card(parent, icon, title, value, style)
            card.grid(row=0, column=i, padx=10, sticky='ew')
            parent.grid_columnconfigure(i, weight=1)
    
    def create_stat_card(self, parent, icon, title, value, style):
        """Create individual stat card"""
        colors = theme_manager.get_colors()
        
        card = tk.Frame(
            parent,
            bg=colors['card_bg'],
            relief='raised',
            bd=2,
            padx=20,
            pady=15
        )
        
        # Icon
        icon_label = tk.Label(
            card,
            text=icon,
            bg=colors['card_bg'],
            font=('Arial', 24)
        )
        icon_label.pack()
        
        # Value
        value_label = tk.Label(
            card,
            text=value,
            bg=colors['card_bg'],
            fg=colors[style] if style in colors else colors['text'],
            font=('Arial', 18, 'bold')
        )
        value_label.pack()
        
        # Title
        title_label = tk.Label(
            card,
            text=title,
            bg=colors['card_bg'],
            fg=colors['text'],
            font=('Arial', 10)
        )
        title_label.pack()
        
        return card
    
    def create_charts(self, parent):
        """Create dashboard charts"""
        # Left chart - Sales over time
        left_frame = theme_manager.create_card_frame(parent, "📈 Vendas dos Últimos 7 Dias")
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        self.create_sales_chart(left_frame)
        
        # Right chart - Product categories
        right_frame = theme_manager.create_card_frame(parent, "🥧 Produtos por Categoria")
        right_frame.pack(side='right', fill='both', expand=True, padx=(10, 0))
        
        self.create_category_chart(right_frame)
    
    def create_sales_chart(self, parent):
        """Create sales line chart"""
        # Get sales data for last 7 days
        sales_data = self.get_sales_data()
        
        # Create matplotlib figure
        fig = Figure(figsize=(6, 4), dpi=100)
        fig.patch.set_facecolor(self.colors['card_bg'])
        
        ax = fig.add_subplot(111)
        ax.set_facecolor(self.colors['card_bg'])
        
        if sales_data:
            dates = [item['data'] for item in sales_data]
            values = [item['total'] for item in sales_data]
            
            ax.plot(dates, values, color=self.colors['primary'], linewidth=3, marker='o')
            ax.fill_between(dates, values, alpha=0.3, color=self.colors['primary'])
        else:
            # Show placeholder when no data
            ax.text(0.5, 0.5, 'Sem dados de vendas', 
                   horizontalalignment='center', verticalalignment='center',
                   transform=ax.transAxes, fontsize=12, color=self.colors['text'])
        
        ax.set_title('Vendas Diárias', color=self.colors['text'], fontsize=12, fontweight='bold')
        ax.tick_params(colors=self.colors['text'])
        ax.spines['bottom'].set_color(self.colors['text'])
        ax.spines['top'].set_color(self.colors['text'])
        ax.spines['right'].set_color(self.colors['text'])
        ax.spines['left'].set_color(self.colors['text'])
        
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
        fig.tight_layout()
        
        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)
    
    def create_category_chart(self, parent):
        """Create category pie chart"""
        # Get category data
        category_data = self.get_category_data()
        
        # Create matplotlib figure
        fig = Figure(figsize=(6, 4), dpi=100)
        fig.patch.set_facecolor(self.colors['card_bg'])
        
        ax = fig.add_subplot(111)
        ax.set_facecolor(self.colors['card_bg'])
        
        if category_data:
            labels = [item['categoria'] for item in category_data]
            sizes = [item['quantidade'] for item in category_data]
            colors_list = [self.colors['primary'], self.colors['success'], 
                          self.colors['warning'], self.colors['error']]
            
            ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90,
                  colors=colors_list[:len(labels)])
        else:
            # Show placeholder when no data
            ax.text(0.5, 0.5, 'Sem dados de produtos', 
                   horizontalalignment='center', verticalalignment='center',
                   transform=ax.transAxes, fontsize=12, color=self.colors['text'])
        
        ax.set_title('Distribuição por Categoria', color=self.colors['text'], 
                    fontsize=12, fontweight='bold')
        
        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)
    
    def create_recent_activity(self, parent):
        """Create recent activity list"""
        activities = self.get_recent_activities()
        
        # Create scrollable frame
        canvas = tk.Canvas(parent, bg=self.colors['card_bg'], height=150)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors['card_bg'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Add activities
        for i, activity in enumerate(activities[:10]):  # Show last 10 activities
            activity_frame = tk.Frame(scrollable_frame, bg=self.colors['card_bg'])
            activity_frame.pack(fill='x', pady=2)
            
            # Time
            time_label = tk.Label(
                activity_frame,
                text=activity['time'],
                bg=self.colors['card_bg'],
                fg=self.colors['text'],
                font=('Arial', 9),
                width=12
            )
            time_label.pack(side='left')
            
            # Description
            desc_label = tk.Label(
                activity_frame,
                text=activity['description'],
                bg=self.colors['card_bg'],
                fg=self.colors['text'],
                font=('Arial', 10),
                anchor='w'
            )
            desc_label.pack(side='left', fill='x', expand=True, padx=(10, 0))
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def get_dashboard_stats(self) -> Dict[str, Any]:
        """Get dashboard statistics"""
        stats = {
            'vendas_hoje': 0.0,
            'total_produtos': 0,
            'total_clientes': 0,
            'estoque_baixo': 0
        }
        
        try:
            # Vendas hoje
            hoje = datetime.now().strftime('%Y-%m-%d')
            vendas_query = "SELECT COALESCE(SUM(total), 0) as total FROM vendas WHERE DATE(data) = ?"
            result = execute_query(vendas_query, (hoje,), fetch=True)
            if result:
                stats['vendas_hoje'] = result[0].get('total', 0) or 0
            
            # Total produtos
            produtos_query = "SELECT COUNT(*) as count FROM produtos"
            result = execute_query(produtos_query, fetch=True)
            if result:
                stats['total_produtos'] = result[0].get('count', 0) or 0
            
            # Total clientes
            clientes_query = "SELECT COUNT(*) as count FROM clientes"
            result = execute_query(clientes_query, fetch=True)
            if result:
                stats['total_clientes'] = result[0].get('count', 0) or 0
            
            # Estoque baixo
            estoque_query = "SELECT COUNT(*) as count FROM produtos WHERE quantidade <= 5"
            result = execute_query(estoque_query, fetch=True)
            if result:
                stats['estoque_baixo'] = result[0].get('count', 0) or 0
                
        except Exception as e:
            print(f"Erro ao obter estatísticas: {e}")
        
        return stats
    
    def get_sales_data(self) -> List[Dict]:
        """Get sales data for last 7 days"""
        try:
            query = """
                SELECT DATE(data) as data, COALESCE(SUM(total), 0) as total
                FROM vendas 
                WHERE data >= date('now', '-7 days')
                GROUP BY DATE(data)
                ORDER BY data
            """
            result = execute_query(query, fetch=True)
            return result or []
        except Exception as e:
            print(f"Erro ao obter dados de vendas: {e}")
            return []
    
    def get_category_data(self) -> List[Dict]:
        """Get product category distribution"""
        try:
            query = """
                SELECT COALESCE(categoria, 'Sem Categoria') as categoria, 
                       COUNT(*) as quantidade
                FROM produtos 
                GROUP BY categoria
                ORDER BY quantidade DESC
            """
            result = execute_query(query, fetch=True)
            return result or []
        except Exception as e:
            print(f"Erro ao obter dados de categoria: {e}")
            return []
    
    def get_recent_activities(self) -> List[Dict]:
        """Get recent system activities"""
        activities = []
        
        try:
            # Recent sales
            vendas_query = """
                SELECT v.data, p.nome as produto, v.quantidade, v.total
                FROM vendas v
                JOIN produtos p ON v.produto_id = p.id
                ORDER BY v.data DESC
                LIMIT 5
            """
            vendas = execute_query(vendas_query, fetch=True) or []
            
            for venda in vendas:
                activities.append({
                    'time': venda['data'][:16] if venda['data'] else '',
                    'description': f"Venda: {venda['produto']} (Qtd: {venda['quantidade']}) - R$ {venda['total']:.2f}"
                })
            
            # Recent product additions
            produtos_query = """
                SELECT nome, data_cadastro
                FROM produtos
                WHERE data_cadastro IS NOT NULL
                ORDER BY data_cadastro DESC
                LIMIT 3
            """
            produtos = execute_query(produtos_query, fetch=True) or []
            
            for produto in produtos:
                activities.append({
                    'time': produto['data_cadastro'][:16] if produto['data_cadastro'] else '',
                    'description': f"Produto cadastrado: {produto['nome']}"
                })
            
            # Sort by time
            activities.sort(key=lambda x: x['time'], reverse=True)
            
        except Exception as e:
            print(f"Erro ao obter atividades recentes: {e}")
        
        return activities
    
    def toggle_theme(self):
        """Toggle between light and dark themes"""
        theme_manager.toggle_theme()
        self.colors = theme_manager.get_colors()
        self.setup_dashboard()  # Refresh dashboard with new theme
    
    def refresh_data(self):
        """Refresh dashboard data"""
        self.setup_dashboard()
