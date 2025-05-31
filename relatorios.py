import pandas as pd
import matplotlib.pyplot as plt
from tkinter import messagebox
from database import get_connection
import clientes
import produtos

def gerar_relatorio_vendas(caminho: str = 'relatorio_vendas.xlsx') -> None:
    try:
        with get_connection() as conn:
            df = pd.read_sql_query('SELECT * FROM vendas', conn)
        if df.empty:
            messagebox.showinfo("Relatório", "Nenhuma venda registrada.")
            return
        df.to_excel(caminho, index=False)
        messagebox.showinfo("Relatório", f"Relatório de vendas exportado como '{caminho}'.")
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao gerar relatório de vendas: {e}")

def gerar_relatorio_clientes(caminho: str = 'relatorio_clientes.xlsx') -> None:
    try:
        lista = clientes.listar_clientes()
        df = pd.DataFrame(lista, columns=["ID", "Nome", "CPF", "Email"])
        if df.empty:
            messagebox.showinfo("Relatório", "Nenhum cliente cadastrado.")
            return
        df.to_excel(caminho, index=False)
        messagebox.showinfo("Relatório", f"Relatório de clientes exportado como '{caminho}'.")
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao gerar relatório de clientes: {str(e)}")

def gerar_relatorio_categoria(caminho: str = 'relatorio_categoria.xlsx') -> None:
    try:
        lista = produtos.listar_produtos()
        if not lista:
            messagebox.showinfo("Relatório", "Nenhum produto cadastrado.")
            return
        df = pd.DataFrame(lista, columns=["ID", "Nome", "Quantidade", "Preço", "Validade"])
        df['Categoria'] = df['Nome'].apply(lambda nome: nome.split()[0] if isinstance(nome, str) else 'Indefinido')
        agrupado = df.groupby('Categoria').agg({
            'Quantidade': 'sum',
            'Preço': 'mean'
        }).reset_index()
        agrupado.to_excel(caminho, index=False)
        messagebox.showinfo("Relatório", f"Relatório por categoria exportado como '{caminho}'.")
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao gerar relatório por categoria: {str(e)}")

def grafico_vendas() -> None:
    try:
        with get_connection() as conn:
            df = pd.read_sql_query('''
                SELECT data, SUM(quantidade) AS total_vendido 
                FROM vendas 
                GROUP BY data
            ''', conn)
        if df.empty:
            messagebox.showinfo("Gráfico", "Nenhuma venda encontrada para gerar gráfico.")
            return
        df['data'] = pd.to_datetime(df['data'])
        plt.style.use('seaborn-vignette')
        plt.figure(figsize=(10, 6))
        plt.plot(df['data'], df['total_vendido'], marker='o', color='#007acc', linewidth=2)
        plt.title('Vendas ao Longo do Tempo', fontsize=16)
        plt.xlabel('Data', fontsize=12)
        plt.ylabel('Quantidade Vendida', fontsize=12)
        plt.grid(visible=True, linestyle='--', alpha=0.5)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao gerar gráfico de vendas: {e}")

def gerar_relatorio_geral():
    try:
        gerar_relatorio_vendas('relatorio_vendas_geral.xlsx')
        gerar_relatorio_clientes('relatorio_clientes_geral.xlsx')
        gerar_relatorio_categoria('relatorio_categoria_geral.xlsx')
        messagebox.showinfo("Relatório Geral", "Todos os relatórios foram gerados com sucesso!")
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao gerar relatório geral: {e}")

def obter_vendas_recentes(limite: int = 10):
    """Retorna as vendas mais recentes do banco de dados"""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT v.id, v.data, u.username as cliente, p.nome as produto, 
                       v.quantidade, v.total
                FROM vendas v
                JOIN usuarios u ON v.cliente_id = u.id
                JOIN produtos p ON v.produto_id = p.id
                ORDER BY v.data DESC
                LIMIT ?
            ''', (limite,))
            return cursor.fetchall()
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao obter vendas recentes: {e}")
        return []

def obter_vendas_por_periodo(data_inicio=None, data_fim=None):
    """Retorna vendas agregadas por data dentro do período especificado"""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            query = '''
                SELECT data, SUM(total) as total_vendas
                FROM vendas
                WHERE (? IS NULL OR data >= ?)
                  AND (? IS NULL OR data <= ?)
                GROUP BY data
                ORDER BY data
            '''
            cursor.execute(query, (data_inicio, data_inicio, data_fim, data_fim))
            return cursor.fetchall()
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao obter vendas por período: {e}")
        return []
