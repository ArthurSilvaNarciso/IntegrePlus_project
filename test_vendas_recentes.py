import sqlite3
from relatorios import obter_vendas_recentes
from database import conectar

def test_obter_vendas_recentes():
    """Test the recent sales retrieval functionality"""
    try:
        # Test with default limit
        print("\nTesting with default limit (10):")
        vendas = obter_vendas_recentes()
        if vendas:
            print(f"Found {len(vendas)} sales:")
            for venda in vendas:
                print(f"ID: {venda[0]}, Data: {venda[1]}, Cliente: {venda[2]}, " \
                      f"Produto: {venda[3]}, Qtd: {venda[4]}, Total: R${venda[5]:.2f}")
        else:
            print("No sales found in database")

        # Test with custom limit
        print("\nTesting with limit of 5:")
        vendas_limitadas = obter_vendas_recentes(5)
        if vendas_limitadas:
            print(f"Found {len(vendas_limitadas)} sales:")
            for venda in vendas_limitadas:
                print(f"ID: {venda[0]}, Data: {venda[1]}, Cliente: {venda[2]}, " \
                      f"Produto: {venda[3]}, Qtd: {venda[4]}, Total: R${venda[5]:.2f}")
        else:
            print("No sales found in database")

        # Test database connection error handling
        print("\nTesting error handling:")
        try:
            with conectar() as conn:
                cursor = conn.cursor()
                # Check if tables exist
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' 
                    AND name IN ('vendas', 'clientes', 'produtos')
                """)
                tables = cursor.fetchall()
                print("Available tables:", [t[0] for t in tables])
                
                # Check table structure
                for table in ['vendas', 'clientes', 'produtos']:
                    try:
                        cursor.execute(f"PRAGMA table_info({table})")
                        columns = cursor.fetchall()
                        print(f"\n{table} table structure:")
                        for col in columns:
                            print(f"  {col[1]} ({col[2]})")
                    except sqlite3.Error as e:
                        print(f"Error checking {table} structure:", e)
        except Exception as e:
            print("Database connection error:", e)

    except Exception as e:
        print("Test failed:", e)

if __name__ == "__main__":
    test_obter_vendas_recentes()
