"""
Configuration module for Integre+ application.
Contains global settings and theme definitions.
"""

# Theme definitions
THEME_COLORS = {
    'light': {
        'primary': '#2563eb',      # Modern blue
        'secondary': '#4f46e5',    # Deep purple
        'accent': '#06b6d4',       # Cyan
        'success': '#10b981',      # Emerald
        'warning': '#f59e0b',      # Amber
        'error': '#ef4444',        # Red
        'background': '#f8fafc',   # Light gray
        'card_bg': '#ffffff',      # White
        'text': '#1e293b',         # Slate 800
        'text_secondary': '#64748b', # Slate 500
        'border': '#e2e8f0',       # Slate 200
        'hover': '#3b82f6',        # Blue 500
        'menu_bg': '#1e293b',      # Slate 800
        'menu_fg': '#ffffff',      # White
    },
    'dark': {
        'primary': '#3b82f6',      # Blue 500
        'secondary': '#6366f1',    # Indigo 500
        'accent': '#06b6d4',       # Cyan
        'success': '#10b981',      # Emerald
        'warning': '#f59e0b',      # Amber
        'error': '#ef4444',        # Red
        'background': '#0f172a',   # Slate 900
        'card_bg': '#1e293b',      # Slate 800
        'text': '#f8fafc',         # Slate 50
        'text_secondary': '#94a3b8', # Slate 400
        'border': '#334155',       # Slate 700
        'hover': '#2563eb',        # Blue 600
        'menu_bg': '#0f172a',      # Slate 900
        'menu_fg': '#f8fafc',      # Slate 50
    }
}

# Database configuration
DB_CONFIG = {
    'name': 'integre_plus.db',
    'backup_dir': 'backups'
}

# Logging configuration
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        },
    },
    'handlers': {
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'app.log',
            'formatter': 'standard'
        },
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'standard'
        }
    },
    'loggers': {
        '': {  # Root logger
            'handlers': ['console', 'file'],
            'level': 'INFO',
        }
    }
}

def get_config():
    """Return complete configuration dictionary"""
    return {
        'themes': THEME_COLORS,
        'theme': THEME_COLORS,  # Add both for compatibility
        'db': DB_CONFIG,
        'logging': LOGGING_CONFIG,
        'ui': {
            'dialog': '600x500',
            'list': '1000x700',
            'main': '1200x800'
        }
    }

def criar_usuario_admin():
    """Create default admin user if it doesn't exist"""
    try:
        import bcrypt
        from database import execute_query
        from datetime import datetime
        
        # Check if admin user exists
        check_query = "SELECT id FROM usuarios WHERE username = 'admin'"
        result = execute_query(check_query, fetch=True)
        
        if not result:
            # Create admin user
            password = "admin123"
            salt = bcrypt.gensalt()
            hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
            
            insert_query = """
                INSERT INTO usuarios (username, password, email, permissao, data_cadastro, ultima_atualizacao)
                VALUES (?, ?, ?, ?, ?, ?)
            """
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            execute_query(insert_query, (
                'admin', hashed, 'admin@integreplus.com', 'Admin', now, now
            ))
            print("Admin user created successfully")
        else:
            print("Admin user already exists")
            
    except Exception as e:
        print(f"Error creating admin user: {e}")
