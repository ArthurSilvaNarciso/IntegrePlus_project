"""
Product management module for Integre+ application.
Handles product CRUD operations and GUI interfaces.
"""
from database import execute_query, create_tables
import pandas as pd
from typing import List, Tuple, Optional, Dict, Any
import tkinter as tk
from tkinter import messagebox, ttk, filedialog
from PIL import Image, ImageTk
import io
import qrcode
from datetime import datetime
import logging
from config import get_config

# Initialize logging
logger = logging.getLogger(__name__)

# Initialize tables
create_tables()

def cadastrar_produto(nome: str, quantidade: int, preco: float, validade: str, categoria: Optional[str] = None, codigo_barras: Optional[str] = None, fornecedor_id: Optional[int] = None, imagem: Optional[bytes] = None) -> None:
    if not nome or quantidade < 0 or preco < 0:
        raise ValueError("Dados inválidos para cadastro de produto.")
    query = '''
        INSERT INTO produtos (nome, quantidade, preco, validade, categoria, codigo_barras, fornecedor_id, imagem, data_cadastro, ultima_atualizacao)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    '''
    params = (nome, quantidade, preco, validade, categoria, codigo_barras, fornecedor_id, imagem, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    execute_query(query, params)

def listar_produtos() -> List[Dict]:
    query = '''
        SELECT id, nome, quantidade, preco, validade, 
               COALESCE(categoria, 'N/A') as categoria,
               COALESCE(codigo_barras, '') as codigo_barras,
               COALESCE(fornecedor_id, 0) as fornecedor_id,
               imagem
        FROM produtos
    '''
    try:
        result = execute_query(query, fetch=True)
        return result if result else []
    except Exception as e:
        logger.error(f"Error listing products: {e}")
        return []

def atualizar_produto(produto_id: int, nome: str, quantidade: int, preco: float, validade: str, categoria: Optional[str] = None, codigo_barras: Optional[str] = None, fornecedor_id: Optional[int] = None, imagem: Optional[bytes] = None) -> None:
    if not nome or quantidade < 0 or preco < 0:
        raise ValueError("Dados inválidos para atualização de produto.")
    query = '''
        UPDATE produtos 
        SET nome = ?, quantidade = ?, preco = ?, validade = ?, categoria = ?, codigo_barras = ?, fornecedor_id = ?, imagem = ?, ultima_atualizacao = ?
        WHERE id = ?
    '''
    params = (nome, quantidade, preco, validade, categoria, codigo_barras, fornecedor_id, imagem, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), produto_id)
    execute_query(query, params)

def excluir_produto(produto_id: int) -> None:
    query = 'DELETE FROM produtos WHERE id = ?'
    execute_query(query, (produto_id,))

def exportar_produtos_para_excel(caminho: str = 'produtos_exportados.xlsx') -> None:
    try:
        produtos = listar_produtos()
        if produtos:
            df = pd.DataFrame(produtos, columns=['ID', 'Nome', 'Quantidade', 'Preço', 'Validade'])
            df.to_excel(caminho, index=False)
            messagebox.showinfo("Exportação", f"Produtos exportados com sucesso para '{caminho}'.")
        else:
            messagebox.showinfo("Exportação", "Nenhum produto encontrado para exportar.")
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao exportar produtos: {e}")

def buscar_produtos_por_nome(nome: str) -> List[Dict]:
    query = '''
        SELECT id, nome, quantidade, preco, validade,
               COALESCE(categoria, 'N/A') as categoria,
               COALESCE(codigo_barras, '') as codigo_barras,
               COALESCE(fornecedor_id, 0) as fornecedor_id,
               imagem
        FROM produtos 
        WHERE nome LIKE ?
    '''
    result = execute_query(query, ('%' + nome + '%',), fetch=True) or []
    columns = ['id', 'nome', 'quantidade', 'preco', 'validade', 'categoria', 'codigo_barras', 'fornecedor_id', 'imagem']
    return [dict(zip(columns, row)) for row in result]

def produtos_estoque_baixo(limite: int = 5) -> List[Dict]:
    query = '''
        SELECT id, nome, quantidade, preco, validade,
               COALESCE(categoria, 'N/A') as categoria,
               COALESCE(codigo_barras, '') as codigo_barras,
               COALESCE(fornecedor_id, 0) as fornecedor_id,
               imagem
        FROM produtos 
        WHERE quantidade <= ?
    '''
    result = execute_query(query, (limite,), fetch=True) or []
    columns = ['id', 'nome', 'quantidade', 'preco', 'validade', 'categoria', 'codigo_barras', 'fornecedor_id', 'imagem']
    return [dict(zip(columns, row)) for row in result]

def validar_dados_produto(nome: str, quantidade: str, preco: str, validade: str) -> tuple[bool, str]:
    """Validate product data input"""
    if not nome.strip():
        return False, "Nome do produto é obrigatório."
    try:
        qtd = int(quantidade)
        if qtd < 0:
            return False, "Quantidade não pode ser negativa."
    except ValueError:
        return False, "Quantidade deve ser um número inteiro."
    try:
        prc = float(preco)
        if prc < 0:
            return False, "Preço não pode ser negativo."
    except ValueError:
        return False, "Preço deve ser um número válido."
    if not validade.strip():
        return False, "Data de validade é obrigatória."
    try:
        datetime.strptime(validade, '%d/%m/%Y')
    except ValueError:
        return False, "Data de validade deve estar no formato dd/mm/aaaa"
    return True, ""

# ================= INTERFACE GRÁFICA =================

def gui_cadastrar_produto(tela_cheia=False):
    """Modernized GUI for creating a new product with improved layout and validation feedback"""
    config = get_config()
    theme = config['themes']['light']
    
    def salvar():
        try:
            nome = entry_nome.get().strip()
            quantidade = entry_quantidade.get().strip()
            preco = entry_preco.get().strip()
            validade = entry_validade.get().strip()
            
            valido, msg = validar_dados_produto(nome, quantidade, preco, validade)
            if not valido:
                messagebox.showerror("Erro", msg)
                return
                
            cadastrar_produto(
                nome=nome,
                quantidade=int(quantidade),
                preco=float(preco),
                validade=validade,
                categoria=var_categoria.get() if var_categoria.get() != "Selecione..." else None,
                codigo_barras=entry_codigo_barras.get().strip() or None,
                fornecedor_id=int(entry_fornecedor.get().strip()) if entry_fornecedor.get().strip().isdigit() else None
            )
            logger.info(f"Produto cadastrado: {nome}")
            messagebox.showinfo("Sucesso", "Produto cadastrado com sucesso!")
            janela.destroy()
        except Exception as e:
            logger.error(f"Erro ao cadastrar produto: {e}")
            messagebox.showerror("Erro", str(e))

    janela = tk.Toplevel()
    janela.title("Cadastrar Produto")
    janela.geometry(config['ui']['dialog'])
    janela.configure(bg=theme['background'])

    frame = tk.Frame(janela, bg=theme['card_bg'], pady=20, padx=20)
    frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

    # Add category selection
    categorias = ["Selecione...", "Bebidas", "Suplementos", "Outros"]
    var_categoria = tk.StringVar(value=categorias[0])

    entry_nome = tk.Entry(frame, font=("Arial", 12), width=30)
    entry_quantidade = tk.Entry(frame, font=("Arial", 12), width=30)
    entry_preco = tk.Entry(frame, font=("Arial", 12), width=30)
    entry_validade = tk.Entry(frame, font=("Arial", 12), width=30)
    entry_codigo_barras = tk.Entry(frame, font=("Arial", 12), width=30)
    entry_fornecedor = tk.Entry(frame, font=("Arial", 12), width=30)

    campos = [
        ("Nome:", entry_nome),
        ("Quantidade:", entry_quantidade),
        ("Preço:", entry_preco),
        ("Validade (dd/mm/aaaa):", entry_validade),
        ("Código de Barras:", entry_codigo_barras),
        ("Fornecedor ID:", entry_fornecedor),
        ("Categoria:", ttk.OptionMenu(frame, var_categoria, *categorias))
    ]

    for i, (label, widget) in enumerate(campos):
        tk.Label(
            frame,
            text=label,
            bg=theme['card_bg'],
            fg=theme['text'],
            font=("Arial", 12)
        ).grid(row=i, column=0, padx=10, pady=8, sticky="e")
        widget.grid(row=i, column=1, padx=10, pady=8)

    ttk.Button(
        frame,
        text="Salvar",
        command=salvar
    ).grid(row=len(campos), column=0, columnspan=2, pady=15)
    
    ttk.Button(
        frame,
        text="Voltar",
        command=janela.destroy
    ).grid(row=len(campos)+1, column=0, columnspan=2, pady=5)

def gui_listar_produtos(tela_cheia=False, parent=None):
    """GUI for listing products"""
    config = get_config()
    theme = config['themes']['light']
    
    def criar_treeview(container):
        """Create and configure treeview with scrollbars"""
        # Create frame to hold treeview and scrollbars
        frame = tk.Frame(container)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create scrollbars
        vsb = ttk.Scrollbar(frame, orient="vertical")
        hsb = ttk.Scrollbar(frame, orient="horizontal")
        
        # Configure treeview
        colunas = ['ID', 'Nome', 'Quantidade', 'Preço', 'Validade', 'Categoria']
        tree = ttk.Treeview(
            frame, 
            columns=colunas,
            show='headings',
            height=15,
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set
        )
        
        # Configure column headings and widths
        col_widths = {
            'ID': 50,
            'Nome': 200,
            'Quantidade': 100,
            'Preço': 100,
            'Validade': 100,
            'Categoria': 100
        }
        
        for col in colunas:
            tree.heading(col, text=col, command=lambda c=col: sort_treeview(tree, c, False))
            tree.column(col, anchor=tk.CENTER, width=col_widths.get(col, 100))
        
        # Configure scrollbars
        vsb.config(command=tree.yview)
        hsb.config(command=tree.xview)
        
        # Grid layout
        tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(0, weight=1)
        
        return tree
    
    def sort_treeview(tree, col, reverse):
        """Sort treeview by column"""
        items = [(tree.set(item, col), item) for item in tree.get_children('')]
        
        # Convert values for proper sorting
        def convert_value(value):
            try:
                if col in ['Quantidade']:
                    return int(value)
                elif col in ['Preço']:
                    return float(value.replace('R$', '').strip())
                return value.lower()
            except:
                return value
        
        items.sort(key=lambda x: convert_value(x[0]), reverse=reverse)
        
        for index, (_, item) in enumerate(items):
            tree.move(item, '', index)
        
        tree.heading(col, command=lambda: sort_treeview(tree, col, not reverse))
    
    if parent:
        # Se parent for fornecido, criar dentro do frame pai
        for widget in parent.winfo_children():
            widget.destroy()
        
        tk.Label(
            parent,
            text="ESTOQUE ATUAL",
            bg=theme['background'],
            fg=theme['text'],
            font=("Arial", 16, "bold")
        ).pack(pady=10)
        
        tree = criar_treeview(parent)
        
    else:
        # Criar janela separada
        janela = tk.Toplevel()
        janela.title("Estoque")
        janela.geometry(config['ui']['list'])
        janela.configure(bg=theme['background'])
        
        tree = criar_treeview(janela)
        
        ttk.Button(
            janela,
            text="Voltar",
            command=janela.destroy
        ).pack(pady=10)
    
    # Populate treeview
    produtos = listar_produtos()
    for produto in produtos:
        values = [
            produto['id'],
            produto['nome'],
            produto['quantidade'],
            f"R$ {produto['preco']:.2f}",
            produto['validade'],
            produto['categoria'] or "N/A"
        ]
        tree.insert('', tk.END, values=values)

def buscar_produto(produto_id: int) -> Optional[Dict[str, Any]]:
    """Find a product by ID"""
    query = '''
        SELECT id, nome, quantidade, preco, validade,
               COALESCE(categoria, 'N/A') as categoria,
               COALESCE(codigo_barras, '') as codigo_barras,
               COALESCE(fornecedor_id, 0) as fornecedor_id,
               imagem
        FROM produtos 
        WHERE id = ?
    '''
    result = execute_query(query, (produto_id,), fetch=True)
    if not result:
        return None
    
    columns = ['id', 'nome', 'quantidade', 'preco', 'validade', 'categoria', 'codigo_barras', 'fornecedor_id', 'imagem']
    return dict(zip(columns, result[0]))

def gui_atualizar_produto(tela_cheia=False):
    """GUI for updating a product"""
    config = get_config()
    theme = config['themes']['light']
    
    def buscar():
        try:
            produto_id = int(entry_id.get())
            produto = buscar_produto(produto_id)
            if produto:
                entry_nome.delete(0, tk.END)
                entry_nome.insert(0, produto['nome'])
                entry_quantidade.delete(0, tk.END)
                entry_quantidade.insert(0, str(produto['quantidade']))
                entry_preco.delete(0, tk.END)
                entry_preco.insert(0, str(produto['preco']))
                entry_validade.delete(0, tk.END)
                entry_validade.insert(0, produto['validade'])
                var_categoria.set(produto['categoria'] or "Selecione...")
            else:
                messagebox.showerror("Erro", "Produto não encontrado.")
        except ValueError:
            messagebox.showerror("Erro", "ID do produto deve ser um número.")
        except Exception as e:
            logger.error(f"Erro ao buscar produto: {e}")
            messagebox.showerror("Erro", str(e))

    def atualizar():
        try:
            produto_id = int(entry_id.get())
            nome = entry_nome.get().strip()
            quantidade = entry_quantidade.get().strip()
            preco = entry_preco.get().strip()
            validade = entry_validade.get().strip()
            
            valido, msg = validar_dados_produto(nome, quantidade, preco, validade)
            if not valido:
                messagebox.showerror("Erro", msg)
                return
                
            atualizar_produto(
                produto_id=produto_id,
                nome=nome,
                quantidade=int(quantidade),
                preco=float(preco),
                validade=validade,
                categoria=var_categoria.get() if var_categoria.get() != "Selecione..." else None
            )
            logger.info(f"Produto atualizado: {nome} (ID: {produto_id})")
            messagebox.showinfo("Sucesso", "Produto atualizado com sucesso!")
            janela.destroy()
        except Exception as e:
            logger.error(f"Erro ao atualizar produto: {e}")
            messagebox.showerror("Erro", str(e))

    janela = tk.Toplevel()
    janela.title("Atualizar Produto")
    janela.geometry(config['ui']['dialog'])
    janela.configure(bg=theme['background'])

    frame = tk.Frame(janela, bg=theme['card_bg'], pady=20, padx=20)
    frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

    # ID do produto
    tk.Label(
        frame, 
        text="ID do Produto:", 
        bg=theme['card_bg'],
        fg=theme['text'],
        font=("Arial", 12)
    ).grid(row=0, column=0, padx=5, pady=5)
    
    entry_id = tk.Entry(frame, font=("Arial", 12))
    entry_id.grid(row=0, column=1, padx=5, pady=5)
    
    ttk.Button(
        frame,
        text="Buscar",
        command=buscar
    ).grid(row=0, column=2, padx=5, pady=5)

    # Add category selection
    categorias = ["Selecione...", "Bebidas", "Suplementos", "Outros"]
    var_categoria = tk.StringVar(value=categorias[0])
    
    campos = [
        ("Nome:", entry_nome := tk.Entry(frame, font=("Arial", 12))),
        ("Quantidade:", entry_quantidade := tk.Entry(frame, font=("Arial", 12))),
        ("Preço:", entry_preco := tk.Entry(frame, font=("Arial", 12))),
        ("Validade:", entry_validade := tk.Entry(frame, font=("Arial", 12))),
        ("Categoria:", ttk.OptionMenu(frame, var_categoria, *categorias))
    ]

    for i, (label, widget) in enumerate(campos, start=1):
        tk.Label(
            frame,
            text=label,
            bg=theme['card_bg'],
            fg=theme['text'],
            font=("Arial", 12)
        ).grid(row=i, column=0, padx=5, pady=5)
        widget.grid(row=i, column=1, columnspan=2, padx=5, pady=5)

    ttk.Button(
        frame,
        text="Atualizar",
        command=atualizar
    ).grid(row=len(campos)+1, column=0, columnspan=3, pady=15)
    
    ttk.Button(
        frame,
        text="Voltar",
        command=janela.destroy
    ).grid(row=len(campos)+2, column=0, columnspan=3, pady=5)

def gui_excluir_produto(tela_cheia=False):
    """GUI for deleting a product"""
    config = get_config()
    theme = config['themes']['light']
    
    def excluir():
        try:
            produto_id = int(entry_id.get())
            if not messagebox.askyesno("Confirmar", "Tem certeza que deseja excluir este produto?"):
                return
            produto = buscar_produto(produto_id)
            if not produto:
                messagebox.showerror("Erro", "Produto não encontrado.")
                return
            excluir_produto(produto_id)
            logger.info(f"Produto excluído: {produto['nome']} (ID: {produto_id})")
            messagebox.showinfo("Sucesso", "Produto excluído com sucesso!")
            janela.destroy()
        except ValueError:
            messagebox.showerror("Erro", "ID do produto deve ser um número.")
        except Exception as e:
            logger.error(f"Erro ao excluir produto: {e}")
            messagebox.showerror("Erro", str(e))

    janela = tk.Toplevel()
    janela.title("Excluir Produto")
    janela.geometry(config['ui']['dialog'])
    janela.configure(bg=theme['background'])

    frame = tk.Frame(janela, bg=theme['card_bg'], pady=20, padx=20)
    frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

    tk.Label(
        frame, 
        text="ID do Produto:", 
        bg=theme['card_bg'],
        fg=theme['text'],
        font=("Arial", 12)
    ).pack(pady=10)
    
    entry_id = tk.Entry(frame, font=("Arial", 12))
    entry_id.pack(pady=5)
    
    ttk.Button(
        frame,
        text="Excluir",
        command=excluir
    ).pack(pady=15)
    
    ttk.Button(
        frame,
        text="Voltar",
        command=janela.destroy
    ).pack(pady=5)
