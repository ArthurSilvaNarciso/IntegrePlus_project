"""
Enhanced Theme Manager for Integre+ Application
Handles theme switching and UI styling with modern components
"""
import tkinter as tk
from tkinter import ttk
import json
import os
from typing import Dict, Any
from config import THEME_COLORS

class ThemeManager:
    def __init__(self):
        self.current_theme = 'light'
        self.theme_file = 'user_theme.json'
        self.load_theme_preference()
        
    def load_theme_preference(self):
        """Load user's theme preference from file"""
        try:
            if os.path.exists(self.theme_file):
                with open(self.theme_file, 'r') as f:
                    data = json.load(f)
                    self.current_theme = data.get('theme', 'light')
        except Exception:
            self.current_theme = 'light'
    
    def save_theme_preference(self):
        """Save user's theme preference to file"""
        try:
            with open(self.theme_file, 'w') as f:
                json.dump({'theme': self.current_theme}, f)
        except Exception:
            pass
    
    def get_colors(self) -> Dict[str, str]:
        """Get current theme colors"""
        return THEME_COLORS.get(self.current_theme, THEME_COLORS['light'])
    
    def toggle_theme(self):
        """Toggle between light and dark themes"""
        self.current_theme = 'dark' if self.current_theme == 'light' else 'light'
        self.save_theme_preference()
        return self.current_theme
    
    def apply_theme_to_widget(self, widget, widget_type='frame'):
        """Apply current theme to a widget"""
        colors = self.get_colors()
        
        if widget_type == 'frame':
            widget.configure(bg=colors['background'])
        elif widget_type == 'label':
            widget.configure(bg=colors['background'], fg=colors['text'])
        elif widget_type == 'button':
            widget.configure(bg=colors['primary'], fg='white', 
                           activebackground=colors['secondary'])
        elif widget_type == 'entry':
            widget.configure(bg=colors['card_bg'], fg=colors['text'],
                           insertbackground=colors['text'])
        elif widget_type == 'text':
            widget.configure(bg=colors['card_bg'], fg=colors['text'],
                           insertbackground=colors['text'])
    
    def configure_ttk_styles(self, style: ttk.Style):
        """Configure TTK styles with current theme"""
        colors = self.get_colors()
        
        # Configure main styles
        style.theme_use('clam')
        
        # Frame styles
        style.configure('Card.TFrame',
            background=colors['card_bg'],
            relief='flat',
            borderwidth=0)
            
        style.configure('Main.TFrame',
            background=colors['background'])
        
        # Label styles
        style.configure('Title.TLabel',
            background=colors['background'],
            foreground=colors['text'],
            font=('Segoe UI', 24, 'bold'))
            
        style.configure('Heading.TLabel',
            background=colors['card_bg'],
            foreground=colors['text'],
            font=('Segoe UI', 16, 'bold'))
            
        style.configure('Body.TLabel',
            background=colors['card_bg'],
            foreground=colors['text'],
            font=('Segoe UI', 12))
        
        # Button styles
        style.configure('Modern.TButton',
            background=colors['primary'],
            foreground='white',
            font=('Segoe UI', 12, 'bold'),
            borderwidth=0,
            focuscolor='none')
            
        style.map('Modern.TButton',
            background=[('active', colors['hover']),
                       ('pressed', colors['secondary'])])
        
        # Entry styles
        style.configure('Modern.TEntry',
            fieldbackground=colors['card_bg'],
            bordercolor=colors['border'],
            lightcolor=colors['primary'],
            darkcolor=colors['primary'],
            borderwidth=2,
            font=('Segoe UI', 12))
        
        # Treeview styles
        style.configure('Modern.Treeview',
            background=colors['card_bg'],
            foreground=colors['text'],
            fieldbackground=colors['card_bg'],
            borderwidth=0,
            font=('Segoe UI', 11))
            
        style.configure('Modern.Treeview.Heading',
            background=colors['primary'],
            foreground='white',
            font=('Segoe UI', 12, 'bold'))
    
    def create_styled_button(self, parent, text, command=None, style='primary', **kwargs):
        """Create a styled button with current theme"""
        colors = self.get_colors()
        
        style_colors = {
            'primary': colors['primary'],
            'success': colors['success'],
            'warning': colors['warning'],
            'error': colors['error'],
            'secondary': colors['secondary']
        }
        
        bg_color = style_colors.get(style, colors['primary'])
        hover_color = self._get_hover_color(bg_color)
        
        button = tk.Button(
            parent,
            text=text,
            command=command,
            bg=bg_color,
            fg='white',
            font=('Segoe UI', 11, 'bold'),
            relief='flat',
            padx=kwargs.get('padx', 20),
            pady=kwargs.get('pady', 8),
            cursor='hand2',
            bd=0,
            **kwargs
        )
        
        # Add hover effects
        def on_enter(e):
            button.configure(bg=hover_color)
        
        def on_leave(e):
            button.configure(bg=bg_color)
        
        button.bind('<Enter>', on_enter)
        button.bind('<Leave>', on_leave)
        
        return button
    
    def _get_hover_color(self, color):
        """Get hover color for a given color"""
        hover_map = {
            '#2563eb': '#3b82f6',  # primary
            '#4f46e5': '#6366f1',  # secondary
            '#10b981': '#34d399',  # success
            '#f59e0b': '#fbbf24',  # warning
            '#ef4444': '#f87171',  # error
            '#3b82f6': '#60a5fa',  # blue
            '#6366f1': '#818cf8',  # indigo
        }
        return hover_map.get(color, color)
    
    def create_card_frame(self, parent, title=None, **kwargs):
        """Create a styled card frame"""
        colors = self.get_colors()
        
        card = tk.Frame(
            parent,
            bg=colors['card_bg'],
            relief='flat',
            bd=0,
            padx=kwargs.get('padx', 20),
            pady=kwargs.get('pady', 20),
            **kwargs
        )
        
        if title:
            title_label = tk.Label(
                card,
                text=title,
                bg=colors['card_bg'],
                fg=colors['text'],
                font=('Segoe UI', 16, 'bold')
            )
            title_label.pack(anchor='w', pady=(0, 15))
        
        return card
    
    def create_modern_entry(self, parent, placeholder="", **kwargs):
        """Create a modern styled entry widget"""
        colors = self.get_colors()
        
        # Remove font from kwargs if present since we set it explicitly
        kwargs.pop('font', None)
        
        entry = tk.Entry(
            parent,
            bg=colors['card_bg'],
            fg=colors['text'],
            insertbackground=colors['text'],
            relief='solid',
            bd=1,
            highlightthickness=2,
            highlightcolor=colors['primary'],
            highlightbackground=colors['border'],
            font=('Segoe UI', 12),
            **kwargs
        )
        
        # Add placeholder functionality
        if placeholder:
            entry.placeholder = placeholder
            entry.placeholder_color = colors['text_secondary']
            entry.normal_color = colors['text']
            
            entry.insert(0, placeholder)
            entry.configure(fg=entry.placeholder_color)
            
            def on_focus_in(event):
                if entry.get() == placeholder:
                    entry.delete(0, tk.END)
                    entry.configure(fg=entry.normal_color)
            
            def on_focus_out(event):
                if not entry.get():
                    entry.insert(0, placeholder)
                    entry.configure(fg=entry.placeholder_color)
            
            entry.bind('<FocusIn>', on_focus_in)
            entry.bind('<FocusOut>', on_focus_out)
        
        return entry

# Global theme manager instance
theme_manager = ThemeManager()
