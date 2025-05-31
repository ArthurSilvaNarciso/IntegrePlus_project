# Integre+ v2.0 - Sistema de Gestão Empresarial

Um sistema completo de gestão empresarial desenvolvido em Python com interface gráfica moderna e funcionalidades avançadas.

## 🚀 Funcionalidades

### 📊 Dashboard Interativo
- Estatísticas em tempo real
- Gráficos dinâmicos de vendas
- Distribuição de produtos por categoria
- Atividades recentes do sistema

### 📦 Gestão de Produtos
- Cadastro completo de produtos
- Controle de estoque
- Histórico de preços
- Categorização
- Códigos de barras

### 💰 Controle de Vendas
- Registro de vendas
- Histórico completo
- Exportação para Excel
- Relatórios detalhados

### 👥 Gestão de Clientes
- Cadastro de clientes
- Histórico de compras
- Informações de contato

### 📈 Relatórios Avançados
- Relatórios de vendas
- Controle de estoque
- Análise de clientes
- Relatórios financeiros

### 🎨 Interface Moderna
- Temas claro e escuro
- Design responsivo
- Navegação intuitiva
- Componentes modernos

## 🛠️ Tecnologias Utilizadas

- **Python 3.11+**
- **Tkinter** - Interface gráfica
- **SQLite** - Banco de dados
- **Matplotlib** - Gráficos e visualizações
- **Pandas** - Manipulação de dados
- **Pillow** - Processamento de imagens

## 📋 Pré-requisitos

- Python 3.11 ou superior
- Pip (gerenciador de pacotes Python)

## 🔧 Instalação

1. **Clone o repositório:**
```bash
git clone <repository-url>
cd integre_plus
```

2. **Instale as dependências:**
```bash
pip install -r requirements.txt
```

3. **Execute a aplicação:**
```bash
python main.py
```

## 🔐 Acesso Inicial

**Credenciais padrão:**
- **Usuário:** admin
- **Senha:** admin123

## 📁 Estrutura do Projeto

```
integre_plus/
├── main.py                    # Ponto de entrada da aplicação
├── gui_enhanced.py           # Interface gráfica aprimorada
├── dashboard.py              # Dashboard interativo
├── theme_manager.py          # Gerenciador de temas
├── config.py                 # Configurações do sistema
├── database.py               # Módulo de banco de dados
├── produtos.py               # Gestão de produtos
├── vendas.py                 # Controle de vendas
├── clientes.py               # Gestão de clientes
├── relatorios.py             # Sistema de relatórios
├── utils.py                  # Utilitários
├── requirements.txt          # Dependências
└── README.md                 # Documentação
```

## 🎯 Como Usar

### 1. Login
- Execute `python main.py`
- Use as credenciais padrão ou crie novos usuários
- Alterne entre temas claro/escuro

### 2. Dashboard
- Visualize estatísticas em tempo real
- Monitore vendas e estoque
- Acompanhe atividades recentes

### 3. Gestão de Produtos
- Cadastre novos produtos
- Atualize informações e preços
- Controle níveis de estoque
- Organize por categorias

### 4. Vendas
- Registre novas vendas
- Consulte histórico
- Exporte relatórios

### 5. Clientes
- Cadastre clientes
- Mantenha informações atualizadas
- Consulte histórico de compras

### 6. Relatórios
- Gere relatórios personalizados
- Exporte para Excel
- Analise tendências

## 🔧 Configuração

### Banco de Dados
O sistema usa SQLite por padrão. As configurações estão em `config.py`:

```python
DB_CONFIG = {
    'database': 'integre_plus.db',
    'timeout': 30,
    'backup_dir': 'backups'
}
```

### Temas
Personalize cores e aparência em `config.py`:

```python
THEME_COLORS = {
    'light': { ... },
    'dark': { ... }
}
```

## 📊 Funcionalidades Avançadas

### Sistema de Backup
- Backups automáticos do banco de dados
- Restauração de backups
- Histórico de alterações

### Auditoria
- Log de todas as operações
- Rastreamento de usuários
- Histórico de mudanças

### Segurança
- Senhas criptografadas
- Controle de acesso
- Sessões seguras

## 🐛 Solução de Problemas

### Erro de Dependências
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Erro de Banco de Dados
- Verifique permissões de escrita
- Execute `python database.py` para recriar tabelas

### Interface não Carrega
- Verifique se o Tkinter está instalado
- No Ubuntu: `sudo apt-get install python3-tk`

## 🔄 Atualizações

### v2.0 (Atual)
- ✅ Interface completamente redesenhada
- ✅ Dashboard interativo com gráficos
- ✅ Sistema de temas claro/escuro
- ✅ Navegação aprimorada
- ✅ Relatórios avançados
- ✅ Melhor experiência do usuário

### v1.0
- ✅ Funcionalidades básicas
- ✅ CRUD de produtos, vendas e clientes
- ✅ Interface simples

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 📞 Suporte

Para suporte e dúvidas:
- Abra uma issue no GitHub
- Entre em contato via email

## 🎉 Agradecimentos

- Comunidade Python
- Desenvolvedores do Tkinter
- Contribuidores do projeto

---

**Integre+ v2.0** - Desenvolvido com ❤️ em Python
