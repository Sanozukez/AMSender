# src/ui/views/help_tab.py
"""
Aba de Ajuda do AMSender.
Fornece informações sobre o programa e uso de placeholders.
"""

import tkinter as tk
from tkinter import scrolledtext
import ttkbootstrap as ttk
from ttkbootstrap.constants import *


def create_help_tab(notebook):
    """
    Cria a aba de ajuda com informações sobre o programa e placeholders.
    
    Args:
        notebook: Widget Notebook onde a aba será adicionada
        
    Returns:
        ttk.Frame: Frame da aba de ajuda
    """
    help_tab = ttk.Frame(notebook)
    notebook.add(help_tab, text="Ajuda")
    
    # Canvas com scrollbar para permitir scroll
    canvas = tk.Canvas(help_tab, highlightthickness=0)
    scrollbar = ttk.Scrollbar(help_tab, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)
    
    def configure_scroll_region(event=None):
        canvas.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))
    
    scrollable_frame.bind("<Configure>", configure_scroll_region)
    
    canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    
    def configure_canvas_width(event):
        canvas_width = event.width
        canvas.itemconfig(canvas_window, width=canvas_width)
    
    canvas.bind('<Configure>', configure_canvas_width)
    canvas.configure(yscrollcommand=scrollbar.set)
    
    # Bind mouse wheel
    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    
    def _bind_mousewheel(event):
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
    
    def _unbind_mousewheel(event):
        canvas.unbind_all("<MouseWheel>")
    
    canvas.bind('<Enter>', _bind_mousewheel)
    canvas.bind('<Leave>', _unbind_mousewheel)
    
    # Pack canvas e scrollbar
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    # Frame interno com padding
    inner = ttk.Frame(scrollable_frame)
    inner.pack(fill=BOTH, expand=True, padx=20, pady=20)
    
    # Título principal
    title_label = ttk.Label(
        inner,
        text="AMSender - Email Relay",
        font=("Segoe UI", 20, "bold"),
        bootstyle=PRIMARY
    )
    title_label.pack(anchor=W, pady=(0, 10))
    
    # Seção: Sobre o Programa
    section_intro_frame = ttk.LabelFrame(inner, text="Sobre o Programa")
    section_intro_frame.pack(fill=X, pady=(0, 15))
    
    section_intro_inner = ttk.Frame(section_intro_frame)
    section_intro_inner.pack(fill=BOTH, expand=True, padx=15, pady=15)
    
    intro_text = """O AMSender é um sistema para automatizar o envio de emails em massa com conteúdo personalizado.

O programa permite enviar o mesmo conteúdo de email para vários destinatários, personalizando cada mensagem com dados específicos de cada destinatário.

Como funciona:
1. Você prepara uma planilha Excel com os dados dos destinatários
2. Cria um template de email (arquivo .docx ou .txt) com placeholders
3. O programa lê a planilha e envia um email personalizado para cada destinatário

Estrutura da Planilha Excel:
- A primeira linha deve conter os cabeçalhos (nomes das colunas)
- As demais linhas contêm os dados de cada destinatário
- A coluna "email" é obrigatória e deve conter o endereço de email de cada destinatário
- Você pode adicionar quantas colunas quiser (nome, empresa, cargo, etc.)

Template de Email:
- Pode ser um arquivo .docx (Word) ou .txt (texto simples)
- Use placeholders no formato {{nome_da_coluna}} para personalizar
- O placeholder será substituído pelo valor correspondente de cada linha da planilha"""
    
    ttk.Label(section_intro_inner, text=intro_text.strip(), font=("Segoe UI", 10), justify=LEFT, wraplength=800).pack(anchor=W)
    
    # Seção: O que são Placeholders
    section1_frame = ttk.LabelFrame(inner, text="O que são Placeholders?")
    section1_frame.pack(fill=X, pady=(0, 15))
    
    section1_inner = ttk.Frame(section1_frame)
    section1_inner.pack(fill=BOTH, expand=True, padx=15, pady=15)
    
    section1_text = """Placeholders são variáveis que você pode usar no seu template de email para personalizar cada mensagem.

Eles são substituídos automaticamente pelos valores correspondentes de cada linha da planilha Excel.

Formato aceito: {{nome_da_coluna}} apenas com letras, números e underscore (sem espaços ou acentos).

Exemplo: Se sua planilha tem uma coluna chamada "nome", você pode usar {{nome}} no template."""
    
    ttk.Label(section1_inner, text=section1_text.strip(), font=("Segoe UI", 10), justify=LEFT, wraplength=800).pack(anchor=W)
    
    # Seção: Como Usar
    section2_frame = ttk.LabelFrame(inner, text="Como Usar Placeholders")
    section2_frame.pack(fill=X, pady=(0, 15))
    
    section2_inner = ttk.Frame(section2_frame)
    section2_inner.pack(fill=BOTH, expand=True, padx=15, pady=15)
    
    section2_text = """1. Identifique as colunas da sua planilha Excel (primeira linha = cabeçalho)
2. Use o nome exato da coluna entre chaves duplas no template
3. O sistema substituirá automaticamente pelos valores de cada destinatário

IMPORTANTE:
- Use o nome exato da coluna (case-insensitive)
- Só são aceitos placeholders sem espaços/acentos: use {{nome_completo}} em vez de {{Nome Completo}}
- Se um placeholder não existir ou tiver formato inválido, ele é removido do email (fica vazio)
- Coluna obrigatória: "email" (deve existir na planilha)"""
    
    ttk.Label(section2_inner, text=section2_text.strip(), font=("Segoe UI", 10), justify=LEFT, wraplength=800).pack(anchor=W)
    
    # Seção: Placeholders Comuns
    section3_frame = ttk.LabelFrame(inner, text="Placeholders Comuns")
    section3_frame.pack(fill=X, pady=(0, 15))
    
    section3_inner = ttk.Frame(section3_frame)
    section3_inner.pack(fill=BOTH, expand=True, padx=15, pady=15)
    
    # Tabela de placeholders comuns
    common_placeholders = [
        ("{{email}}", "Email do destinatário (obrigatório)", "joao@exemplo.com"),
        ("{{nome}}", "Nome do destinatário", "João Silva"),
        ("{{Nome}}", "Nome (case-insensitive)", "João Silva"),
        ("{{empresa}}", "Nome da empresa", "Empresa ABC"),
        ("{{cargo}}", "Cargo/Função", "Gerente"),
        ("{{telefone}}", "Telefone de contato", "(11) 99999-9999"),
        ("{{cidade}}", "Cidade", "São Paulo"),
        ("{{estado}}", "Estado", "SP"),
    ]
    
    # Cabeçalho da tabela
    header_frame = ttk.Frame(section3_inner)
    header_frame.pack(fill=X, pady=(0, 10))
    ttk.Label(header_frame, text="Placeholder", font=("Segoe UI", 10, "bold"), width=20).pack(side=LEFT, padx=5)
    ttk.Label(header_frame, text="Descrição", font=("Segoe UI", 10, "bold"), width=40).pack(side=LEFT, padx=5)
    ttk.Label(header_frame, text="Exemplo", font=("Segoe UI", 10, "bold"), width=30).pack(side=LEFT, padx=5)
    
    # Linhas da tabela
    for placeholder, descricao, exemplo in common_placeholders:
        row_frame = ttk.Frame(section3_inner)
        row_frame.pack(fill=X, pady=2)
        ttk.Label(row_frame, text=placeholder, font=("Consolas", 10), bootstyle=INFO, width=20).pack(side=LEFT, padx=5)
        ttk.Label(row_frame, text=descricao, font=("Segoe UI", 9), width=40).pack(side=LEFT, padx=5)
        ttk.Label(row_frame, text=exemplo, font=("Segoe UI", 9), bootstyle=SECONDARY, width=30).pack(side=LEFT, padx=5)
    
    # Seção: Exemplos Práticos
    section4_frame = ttk.LabelFrame(inner, text="Exemplos Práticos")
    section4_frame.pack(fill=X, pady=(0, 15))
    
    section4_inner = ttk.Frame(section4_frame)
    section4_inner.pack(fill=BOTH, expand=True, padx=15, pady=15)
    
    # Exemplo 1
    example1_label = ttk.Label(section4_inner, text="Exemplo 1 - Template Simples:", font=("Segoe UI", 10, "bold"))
    example1_label.pack(anchor=W, pady=(0, 5))
    
    example1_text = """Olá {{nome}},

Este é um email personalizado para você.

Seus dados:
- Email: {{email}}
- Empresa: {{empresa}}

Atenciosamente,
Equipe"""
    
    example1_code = tk.Text(section4_inner, height=10, wrap=tk.WORD, font=("Consolas", 10), bg="#f5f5f5", relief=FLAT)
    example1_code.pack(fill=X, pady=(0, 15))
    example1_code.insert(1.0, example1_text.strip())
    example1_code.config(state=DISABLED)
    
    # Exemplo 2
    example2_label = ttk.Label(section4_inner, text="Exemplo 2 - Template com Múltiplos Campos:", font=("Segoe UI", 10, "bold"))
    example2_label.pack(anchor=W, pady=(0, 5))
    
    example2_text = """Prezado(a) {{nome}},

Esperamos que este email o encontre bem.

Informações do contato:
- Nome: {{nome}}
- Email: {{email}}
- Cargo: {{cargo}}
- Empresa: {{empresa}}
- Telefone: {{telefone}}
- Localização: {{cidade}} - {{estado}}

Ficamos à disposição.

Atenciosamente,
Equipe Amatools"""
    
    example2_code = tk.Text(section4_inner, height=15, wrap=tk.WORD, font=("Consolas", 10), bg="#f5f5f5", relief=FLAT)
    example2_code.pack(fill=X, pady=(0, 15))
    example2_code.insert(1.0, example2_text.strip())
    example2_code.config(state=DISABLED)
    
    # Seção: Dicas
    section5_frame = ttk.LabelFrame(inner, text="Dicas Importantes")
    section5_frame.pack(fill=X, pady=(0, 15))
    
    section5_inner = ttk.Frame(section5_frame)
    section5_inner.pack(fill=BOTH, expand=True, padx=15, pady=15)
    
    tips_text = """✓ Use o Preview na aba Campanha para ver como o email ficará antes de enviar
✓ O nome da coluna no Excel deve corresponder exatamente ao placeholder (case-insensitive)
✓ Se uma coluna não existir na planilha, o placeholder será substituído por uma string vazia
✓ Você pode usar qualquer coluna da planilha como placeholder
✓ Placeholders podem ser usados múltiplas vezes no mesmo template
✓ Funciona tanto em arquivos .txt quanto .docx"""
    
    ttk.Label(section5_inner, text=tips_text.strip(), font=("Segoe UI", 10), justify=LEFT, wraplength=800).pack(anchor=W)
    
    # Seção: Estrutura da Planilha
    section6_frame = ttk.LabelFrame(inner, text="Estrutura da Planilha Excel")
    section6_frame.pack(fill=X)
    
    section6_inner = ttk.Frame(section6_frame)
    section6_inner.pack(fill=BOTH, expand=True, padx=15, pady=15)
    
    excel_structure_text = """A primeira linha da planilha deve conter os cabeçalhos (nomes das colunas).

Exemplo de estrutura:

| email                     | nome          | empresa       | cargo        |
|---------------------------|---------------|---------------|--------------|
| joao@exemplo.com          | João Silva    | Empresa A     | Gerente      |
| maria@exemplo.com         | Maria Santos  | Empresa B     | Diretora     |

Colunas obrigatórias:
- email (deve existir e conter emails válidos)

Colunas opcionais:
- Qualquer outra coluna pode ser usada como placeholder"""
    
    ttk.Label(section6_inner, text=excel_structure_text.strip(), font=("Segoe UI", 10), justify=LEFT, wraplength=800).pack(anchor=W)
    
    return help_tab

