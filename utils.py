import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable
import threading
from functools import partial
import json
import os
from config import THEME_COLORS

# Use themes from config
THEMES = {
    'claro': THEME_COLORS['light'],
    'escuro': THEME_COLORS['dark']
}

class AsyncTask:
    """Utility class for running tasks asynchronously"""
    @staticmethod
    def run(func: Callable, callback: Optional[Callable] = None, *args, **kwargs):
        def _callback(result):
            if callback:
                callback(result)

        def _run():
            try:
                result = func(*args, **kwargs)
                if callback:
                    tk.CallWrapper()._subst(None, lambda: _callback(result))
            except Exception as e:
                if callback:
                    tk.CallWrapper()._subst(None, lambda: _callback(e))

        thread = threading.Thread(target=_run)
        thread.daemon = True
        thread.start()
        return thread

class ModernButton(ttk.Button):
    """Custom button with hover effect and modern styling"""
    def __init__(self, master, **kwargs):
        self.hover_color = kwargs.pop('hover_color', '#2980b9')
        self.normal_color = kwargs.pop('background', '#3498db')
        super().__init__(master, **kwargs)
        self.bind('<Enter>', self._on_enter)
        self.bind('<Leave>', self._on_leave)

    def _on_enter(self, e):
        self.configure(style='Hover.TButton')

    def _on_leave(self, e):
        self.configure(style='TButton')

class Tooltip:
    """Create tooltips for buttons and widgets"""
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None
        self.widget.bind('<Enter>', self.show)
        self.widget.bind('<Leave>', self.hide)

    def show(self, event=None):
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20

        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")

        label = tk.Label(self.tooltip, text=self.text, 
                      justify='left',
                      background="#ffffff",
                      relief='solid',
                      borderwidth=1,
                      font=("Arial", "10", "normal"))
        label.pack(ipadx=1)

    def hide(self, event=None):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

class NotificationManager:
    """Manage popup notifications in the GUI"""
    def __init__(self, master):
        self.master = master
        self.notifications = []
        self.spacing = 10
        self.notification_height = 60

    def show_notification(self, message, type_='info', duration=3000):
        # Calculate position for new notification
        existing_count = len(self.notifications)
        y_position = self.spacing + (existing_count * (self.notification_height + self.spacing))

        # Create notification frame
        colors = {
            'info': ('#3498db', '#ffffff'),
            'success': ('#2ecc71', '#ffffff'),
            'warning': ('#f39c12', '#ffffff'),
            'error': ('#e74c3c', '#ffffff')
        }
        bg_color, fg_color = colors.get(type_, colors['info'])

        notification = tk.Frame(self.master, bg=bg_color)
        notification.place(relx=1, y=y_position, anchor='ne')

        # Add message
        tk.Label(notification, text=message, bg=bg_color, fg=fg_color,
                font=("Arial", 12), padx=20, pady=10).pack()

        self.notifications.append(notification)
        
        # Schedule removal
        self.master.after(duration, lambda: self._remove_notification(notification))

    def _remove_notification(self, notification):
        if notification in self.notifications:
            self.notifications.remove(notification)
            notification.destroy()
            self._reposition_notifications()

    def _reposition_notifications(self):
        for i, notif in enumerate(self.notifications):
            y_position = self.spacing + (i * (self.notification_height + self.spacing))
            notif.place(relx=1, y=y_position, anchor='ne')

class SearchFrame(ttk.Frame):
    """Reusable search frame with filters"""
    def __init__(self, master, search_callback, filters=None):
        super().__init__(master)
        self.search_callback = search_callback
        
        # Search entry
        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self._on_search_change())
        
        search_frame = ttk.Frame(self)
        search_frame.pack(fill='x', pady=5)
        
        ttk.Label(search_frame, text="Buscar:").pack(side='left', padx=5)
        ttk.Entry(search_frame, textvariable=self.search_var).pack(side='left', fill='x', expand=True, padx=5)
        
        # Filters if provided
        if filters:
            filter_frame = ttk.Frame(self)
            filter_frame.pack(fill='x', pady=5)
            
            ttk.Label(filter_frame, text="Filtros:").pack(side='left', padx=5)
            for filter_name, filter_options in filters.items():
                var = tk.StringVar(value='Todos')
                ttk.OptionMenu(filter_frame, var, 'Todos', *filter_options,
                             command=lambda *args: self._on_search_change()).pack(side='left', padx=5)

    def _on_search_change(self):
        if self.search_callback:
            self.search_callback(self.search_var.get())

def save_user_preferences(preferences: dict, filename: str = "user_preferences.json"):
    """Save user preferences to a JSON file"""
    try:
        with open(filename, 'w') as f:
            json.dump(preferences, f)
    except Exception as e:
        print(f"Error saving preferences: {e}")

def load_user_preferences(filename: str = "user_preferences.json") -> dict:
    """Load user preferences from a JSON file"""
    try:
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading preferences: {e}")
    return {}  # Return empty dict if file doesn't exist or there's an error

def create_rounded_frame(parent, bg_color, corner_radius=10, **kwargs):
    """Create a frame with rounded corners effect"""
    frame = tk.Frame(parent, bg=bg_color, **kwargs)
    return frame

class ModernCard(tk.Frame):
    """Modern card component with shadow effect"""
    def __init__(self, parent, title=None, theme='light', **kwargs):
        colors = THEME_COLORS[theme]
        super().__init__(parent, 
                        bg=colors['card_bg'],
                        relief='flat',
                        bd=0,
                        padx=20,
                        pady=20,
                        **kwargs)
        
        if title:
            title_label = tk.Label(self,
                                 text=title,
                                 bg=colors['card_bg'],
                                 fg=colors['text'],
                                 font=('Segoe UI', 16, 'bold'))
            title_label.pack(anchor='w', pady=(0, 15))

class ModernEntry(tk.Entry):
    """Modern entry widget with enhanced styling"""
    def __init__(self, parent, placeholder="", theme='light', **kwargs):
        colors = THEME_COLORS[theme]
        super().__init__(parent,
                        bg=colors['card_bg'],
                        fg=colors['text'],
                        insertbackground=colors['text'],
                        relief='solid',
                        bd=1,
                        highlightthickness=2,
                        highlightcolor=colors['primary'],
                        highlightbackground=colors['border'],
                        font=('Segoe UI', 12),
                        **kwargs)
        
        self.placeholder = placeholder
        self.placeholder_color = colors['text_secondary']
        self.normal_color = colors['text']
        
        if placeholder:
            self.insert(0, placeholder)
            self.configure(fg=self.placeholder_color)
            self.bind('<FocusIn>', self._on_focus_in)
            self.bind('<FocusOut>', self._on_focus_out)
    
    def _on_focus_in(self, event):
        if self.get() == self.placeholder:
            self.delete(0, tk.END)
            self.configure(fg=self.normal_color)
    
    def _on_focus_out(self, event):
        if not self.get():
            self.insert(0, self.placeholder)
            self.configure(fg=self.placeholder_color)

class GradientFrame(tk.Canvas):
    """Frame with gradient background"""
    def __init__(self, parent, color1, color2, **kwargs):
        super().__init__(parent, **kwargs)
        self.color1 = color1
        self.color2 = color2
        self.bind('<Configure>', self._draw_gradient)
    
    def _draw_gradient(self, event=None):
        self.delete("gradient")
        width = self.winfo_width()
        height = self.winfo_height()
        
        # Simple vertical gradient simulation
        for i in range(height):
            ratio = i / height
            # Simple color interpolation
            self.create_line(0, i, width, i, fill=self.color1, tags="gradient")

class AnimatedButton(tk.Button):
    """Button with hover animations"""
    def __init__(self, parent, **kwargs):
        self.normal_bg = kwargs.get('bg', '#3498db')
        self.hover_bg = kwargs.pop('hover_bg', '#2980b9')
        self.active_bg = kwargs.pop('active_bg', '#1f5f8b')
        
        super().__init__(parent, **kwargs)
        
        self.bind('<Enter>', self._on_enter)
        self.bind('<Leave>', self._on_leave)
        self.bind('<Button-1>', self._on_click)
        self.bind('<ButtonRelease-1>', self._on_release)
    
    def _on_enter(self, event):
        self.configure(bg=self.hover_bg)
    
    def _on_leave(self, event):
        self.configure(bg=self.normal_bg)
    
    def _on_click(self, event):
        self.configure(bg=self.active_bg)
    
    def _on_release(self, event):
        self.configure(bg=self.hover_bg)

class LoadingSpinner:
    """Simple loading spinner widget"""
    def __init__(self, parent, size=50, theme='light'):
        colors = THEME_COLORS[theme]
        self.canvas = tk.Canvas(parent, width=size, height=size, 
                               bg=colors['background'], highlightthickness=0)
        self.size = size
        self.angle = 0
        self.color = colors['primary']
        self.running = False
    
    def start(self):
        self.running = True
        self._animate()
    
    def stop(self):
        self.running = False
        self.canvas.delete("all")
    
    def _animate(self):
        if not self.running:
            return
        
        self.canvas.delete("all")
        center = self.size // 2
        radius = center - 10
        
        # Draw spinning arc
        start_angle = self.angle
        extent = 90
        
        self.canvas.create_arc(
            center - radius, center - radius,
            center + radius, center + radius,
            start=start_angle, extent=extent,
            outline=self.color, width=3, style='arc'
        )
        
        self.angle = (self.angle + 10) % 360
        self.canvas.after(50, self._animate)
    
    def pack(self, **kwargs):
        self.canvas.pack(**kwargs)
    
    def grid(self, **kwargs):
        self.canvas.grid(**kwargs)
    
    def place(self, **kwargs):
        self.canvas.place(**kwargs)
