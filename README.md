📦 Integre+ – Sistema de Gestão para Adegas e Suplementos
Integre+ é uma aplicação desktop desenvolvida em Python com interface gráfica Tkinter, projetada para gerenciar produtos, clientes e relatórios em adegas e lojas de suplementos. O sistema oferece funcionalidades completas de cadastro, listagem, atualização e exclusão de registros, além de um painel de controle moderno com tema escuro e design responsivo.

🖼️ Interface
Tela de login moderna e em tela cheia

Tema escuro por padrão, com alternância entre temas claro e escuro

Botões com ícones, animações suaves e feedback visual

Layout organizado com menus laterais e botões de acesso rápido

Interface adaptada a diferentes tamanhos de tela

🚀 Funcionalidades
Login seguro com validação de credenciais

Cadastro de produtos e clientes

Listagem e busca de produtos/clientes

Atualização e exclusão de registros

Relatórios automáticos (Geral e Estoque)

Dashboard visual

Suporte a tema claro/escuro

Botão de logout com redirecionamento para login

📁 Estrutura de Pastas
bash
Copiar
Editar
integre_plus/
├── main.py                  # Arquivo principal que inicia o sistema
├── gui.py                   # Interface principal com os frames e navegação
├── clientes.py              # Funções relacionadas a clientes
├── produtos.py              # Funções relacionadas a produtos
├── relatorios.py            # Geração de relatórios e dashboard
├── imagens/                 # Ícones e imagens da interface
├── dados/                   # Arquivos CSV com dados persistentes
├── utils/                   # (Opcional) Funções utilitárias
└── README.md                # Documentação do projeto
✅ Requisitos
Python 3.10 ou superior

Bibliotecas padrão do Python:

tkinter

csv

os

datetime

🛠️ Como Executar
Clone ou extraia o repositório:

bash
Copiar
Editar
git clone https://github.com/seuusuario/integre_plus.git
Navegue até o diretório:

bash
Copiar
Editar
cd integre_plus
Execute o sistema:

bash
Copiar
Editar
python main.py
💡 Sugestões Futuras
Integração com banco de dados (SQLite ou PostgreSQL)

Exportação de relatórios em PDF

Controle de estoque com alertas automáticos

Suporte multiusuário com permissões

🧑‍💻 Autor
Desenvolvido por Arthur.
