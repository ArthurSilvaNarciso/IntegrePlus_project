import os
from database import criar_tabelas
from insert_test_data import insert_test_data

def reset_database():
    db_file = 'integre_plus.db'
    if os.path.exists(db_file):
        os.remove(db_file)
        print(f"Deleted existing database file: {db_file}")
    else:
        print(f"No existing database file found: {db_file}")
    
    criar_tabelas()
    print("Database tables recreated.")

if __name__ == "__main__":
    reset_database()
    insert_test_data()
