"""
Main entry point for Integre+ application.
Initializes the system and launches the modern interface.
"""
import sys
import logging
import logging.config
from tkinter import messagebox

from config import get_config
from database import create_tables, execute_query
from login import ModernLoginWindow

# Configure logging
logging.config.dictConfig(get_config()['logging'])
logger = logging.getLogger(__name__)

def criar_usuario_admin():
    """Create default admin user if it doesn't exist"""
    try:
        import bcrypt
        
        # Check if admin exists
        query = "SELECT id FROM usuarios WHERE username = 'admin'"
        result = execute_query(query, fetch=True)
        
        if not result:
            # Create admin user with bcrypt hash
            admin_password = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt())
            query = """
                INSERT INTO usuarios (
                    username, senha, email, permissao, 
                    bloqueado, data_cadastro, ultima_atualizacao
                ) VALUES (?, ?, ?, ?, ?, datetime('now'), datetime('now'))
            """
            execute_query(query, (
                'admin', 
                admin_password, 
                'admin@integre.com',
                'Admin',
                0
            ))
            logger.info("Default admin user created successfully")
            return True
        return False
    except Exception as e:
        logger.error(f"Error creating admin user: {e}")
        return False

def main():
    """Main application entry point"""
    try:
        # Initialize database
        logger.info("Initializing database...")
        create_tables()
        
        # Create admin user if needed
        if criar_usuario_admin():
            logger.info("Default admin user created")
        
        # Start modern login window
        logger.info("Starting modern login window...")
        login = ModernLoginWindow()
        login.run()
        
    except Exception as e:
        logger.error(f"Critical error in main: {e}")
        messagebox.showerror(
            "Erro Crítico", 
            f"Erro ao iniciar aplicação: {str(e)}\n\n"
            "Por favor, verifique os logs para mais detalhes."
        )
        sys.exit(1)

if __name__ == "__main__":
    main()
