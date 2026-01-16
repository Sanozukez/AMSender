# src/ui/main_window.py
"""
Interface gráfica principal do sistema Mail Sender.
Usa Tkinter com ttkbootstrap para visual moderno e minimalista.
"""

import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from pathlib import Path
import threading
from typing import Optional, List
from datetime import datetime

from src.config import validate_config, SMTP_EMAIL, reload_config
from src.config_manager import ConfigManager
from src.excel_reader import ExcelReader
from src.template_processor import TemplateProcessor
from src.email_sender import EmailSender
from src.comprovacao import Comprovacao
from src.batch_controller import BatchController

class MainWindow:
    """
    Janela principal da aplicação.
    """
    
    def __init__(self):
        """
        Inicializa a interface gráfica.
        """
        # Inicializa logger
        try:
            from src.logger import get_logger
            logger = get_logger()
            logger.info("="*60)
            logger.info("Iniciando AMSender")
            logger.info(f"Arquivo de log: {logger.get_log_file()}")
            logger.info("="*60)
        except Exception as e:
            # Se não conseguir inicializar logger, continua sem ele
            import sys
            print(f"[WARNING] Não foi possível inicializar logger: {e}", file=sys.stderr)
        
        # Gerenciador de configurações
        self.config_manager = ConfigManager()
        self.batch_controller = BatchController(log_fn=self._log, stats_fn=self._update_stats)
        self._ui_thread_id = threading.get_ident()
        
        # Cria janela principal
        self.root = ttk.Window(themename="cosmo")  # Tema moderno e minimalista
        self.root.title("AMSender - Email Relay")
        self.root.geometry("900x750")
        self.root.resizable(True, True)
        
        # Define ícone da janela
        try:
            # Tenta encontrar o ícone em diferentes locais (desenvolvimento e executável)
            import sys
            if getattr(sys, 'frozen', False):
                # Executável PyInstaller
                base_path = Path(sys._MEIPASS)
            else:
                # Desenvolvimento
                base_path = Path(__file__).parent.parent.parent
            
            icon_path = base_path / 'image' / 'icon.ico'
            if not icon_path.exists():
                # Tenta caminho alternativo
                icon_path = Path('image') / 'icon.ico'
            
            if icon_path.exists():
                self.root.iconbitmap(str(icon_path))
        except Exception as e:
            # Se não conseguir carregar o ícone, continua sem ele
            from src.logger import get_logger
            get_logger().debug(f"Não foi possível carregar ícone: {e}")
        
        # Variáveis
        self.excel_path = tk.StringVar()
        self.template_path = tk.StringVar()
        self.attachments = []  # Lista de caminhos de anexos
        self.subject = tk.StringVar(value="")
        self.campanha_name = tk.StringVar(value="")
        
        # Variáveis de configuração SMTP
        self.smtp_server = tk.StringVar()
        self.smtp_port = tk.StringVar()
        self.smtp_email = tk.StringVar()
        self.smtp_password = tk.StringVar()
        self.email_delay = tk.StringVar()
        
        # Variáveis de configuração OAuth Google
        self.google_email = tk.StringVar()
        self.use_oauth = tk.BooleanVar(value=False)  # False = SMTP, True = OAuth
        self.gmail_sender = None
        
        # Estado do envio
        self.is_sending = False
        self.should_stop = False
        self.sending_thread: Optional[threading.Thread] = None
        
        # Componentes
        self.excel_reader: Optional[ExcelReader] = None
        self.template_processor: Optional[TemplateProcessor] = None
        self.email_sender: Optional[EmailSender] = None
        self.comprovacao: Optional[Comprovacao] = None
        
        # Cria interface
        self._create_ui()
        
        # Carrega configurações
        self._load_config()
        
        # Verifica status OAuth se necessário
        if self.use_oauth.get():
            self._check_oauth_status()
        
        # Atualiza preview inicial
        self._update_preview()

    def _run_on_ui_thread(self, func, *args, **kwargs):
        """Garante que a função rode na thread da UI."""
        if threading.get_ident() == self._ui_thread_id:
            func(*args, **kwargs)
        else:
            self.root.after(0, lambda: func(*args, **kwargs))
    
    def _create_ui(self):
        """
        Cria todos os componentes da interface.
        """
        # Container principal com padding
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=BOTH, expand=True, padx=20, pady=20)
        
        # Título
        title_label = ttk.Label(
            main_frame,
            text="AMSender",
            font=("Segoe UI", 24, "bold"),
            bootstyle=PRIMARY
        )
        title_label.pack(pady=(0, 10))
        
        subtitle_label = ttk.Label(
            main_frame,
            text="Email Relay",
            font=("Segoe UI", 10),
            bootstyle=SECONDARY
        )
        subtitle_label.pack(pady=(0, 20))
        
        # Notebook (Abas)
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=BOTH, expand=True)
        
        # Aba 1: Campanha
        self._create_campanha_tab()
        
        # Aba 2: Configurações
        self._create_config_tab()
        
        # Aba 3: Ajuda
        self._create_help_tab()
    
    def _create_campanha_tab(self):
        """
        Cria a aba de configuração da campanha.
        """
        campanha_tab = ttk.Frame(self.notebook)
        self.notebook.add(campanha_tab, text="Campanha")
        
        # Canvas com scrollbar para permitir scroll
        canvas = tk.Canvas(campanha_tab, highlightthickness=0)
        scrollbar = ttk.Scrollbar(campanha_tab, orient="vertical", command=canvas.yview)
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
        
        # Frame interno com padding (agora dentro do scrollable_frame)
        inner = ttk.Frame(scrollable_frame)
        inner.pack(fill=BOTH, expand=True, padx=15, pady=15)
        
        # Frame de configuração
        config_frame = ttk.LabelFrame(inner, text="Configuração da Campanha")
        config_frame.pack(fill=X, pady=(0, 15))
        
        config_inner = ttk.Frame(config_frame)
        config_inner.pack(fill=BOTH, expand=True, padx=15, pady=15)
        
        # Excel - Labels alinhadas à direita, largura fixa
        excel_frame = ttk.Frame(config_inner)
        excel_frame.pack(fill=X, pady=5)
        ttk.Label(excel_frame, text="Planilha Excel:", width=20, anchor=E).pack(side=LEFT, padx=(0, 10))
        excel_content = ttk.Frame(excel_frame)
        excel_content.pack(side=LEFT, fill=X, expand=True)
        ttk.Entry(excel_content, textvariable=self.excel_path, state=READONLY, width=40).pack(side=LEFT, fill=X, expand=True, padx=(0, 5))
        ttk.Button(excel_content, text="Selecionar", command=self._select_excel, bootstyle=OUTLINE).pack(side=LEFT)
        
        # Template
        template_frame = ttk.Frame(config_inner)
        template_frame.pack(fill=X, pady=5)
        ttk.Label(template_frame, text="Template (DOCX/TXT):", width=20, anchor=E).pack(side=LEFT, padx=(0, 10))
        template_content = ttk.Frame(template_frame)
        template_content.pack(side=LEFT, fill=X, expand=True)
        ttk.Entry(template_content, textvariable=self.template_path, state=READONLY, width=40).pack(side=LEFT, fill=X, expand=True, padx=(0, 5))
        ttk.Button(template_content, text="Selecionar", command=self._select_template, bootstyle=OUTLINE).pack(side=LEFT)
        
        # Anexos
        attachments_frame = ttk.Frame(config_inner)
        attachments_frame.pack(fill=X, pady=5)
        ttk.Label(attachments_frame, text="Anexos:", width=20, anchor=E).pack(side=LEFT, padx=(0, 10))
        attachments_content = ttk.Frame(attachments_frame)
        attachments_content.pack(side=LEFT, fill=X, expand=True)
        self.attachments_listbox = tk.Listbox(attachments_content, height=3, width=40)
        self.attachments_listbox.pack(side=LEFT, fill=X, expand=True, padx=(0, 5))
        attachments_btn_frame = ttk.Frame(attachments_content)
        attachments_btn_frame.pack(side=LEFT)
        ttk.Button(attachments_btn_frame, text="Adicionar", command=self._add_attachment, bootstyle=OUTLINE).pack(pady=2)
        ttk.Button(attachments_btn_frame, text="Remover", command=self._remove_attachment, bootstyle=OUTLINE).pack(pady=2)
        
        # Assunto
        subject_frame = ttk.Frame(config_inner)
        subject_frame.pack(fill=X, pady=5)
        ttk.Label(subject_frame, text="Assunto:", width=20, anchor=E).pack(side=LEFT, padx=(0, 10))
        ttk.Entry(subject_frame, textvariable=self.subject).pack(side=LEFT, fill=X, expand=True)
        self.subject.trace('w', lambda *args: self._update_preview())
        
        # Nome da campanha (opcional)
        campanha_frame = ttk.Frame(config_inner)
        campanha_frame.pack(fill=X, pady=5)
        ttk.Label(campanha_frame, text="Nome Campanha:", width=20, anchor=E).pack(side=LEFT, padx=(0, 10))
        ttk.Entry(campanha_frame, textvariable=self.campanha_name).pack(side=LEFT, fill=X, expand=True)
        
        # Preview
        preview_frame = ttk.LabelFrame(inner, text="Preview do Email")
        preview_frame.pack(fill=BOTH, expand=True, pady=(0, 15))
        
        preview_inner = ttk.Frame(preview_frame)
        preview_inner.pack(fill=BOTH, expand=True, padx=15, pady=15)
        
        self.preview_text = scrolledtext.ScrolledText(preview_inner, height=8, wrap=tk.WORD, font=("Consolas", 10))
        self.preview_text.pack(fill=BOTH, expand=True)
        
        # Controles e estatísticas
        control_frame = ttk.Frame(inner)
        control_frame.pack(fill=X, pady=(0, 15))
        
        # Estatísticas
        stats_frame = ttk.LabelFrame(control_frame, text="Estatísticas")
        stats_frame.pack(side=LEFT, fill=X, expand=True, padx=(0, 10))
        
        stats_inner = ttk.Frame(stats_frame)
        stats_inner.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        self.stats_label = ttk.Label(stats_inner, text="Total: 0 | Enviados: 0 | Erros: 0", font=("Segoe UI", 10))
        self.stats_label.pack()
        
        # Botões de controle
        buttons_frame = ttk.Frame(control_frame)
        buttons_frame.pack(side=RIGHT)
        
        self.start_btn = ttk.Button(buttons_frame, text="Iniciar Envio", command=self._start_sending, bootstyle=SUCCESS, width=15)
        self.start_btn.pack(side=LEFT, padx=5)
        
        self.pause_btn = ttk.Button(buttons_frame, text="Pausar", command=self._pause_sending, bootstyle=WARNING, width=15, state=DISABLED)
        self.pause_btn.pack(side=LEFT, padx=5)
        
        self.stop_btn = ttk.Button(buttons_frame, text="Parar", command=self._stop_sending, bootstyle=DANGER, width=15, state=DISABLED)
        self.stop_btn.pack(side=LEFT, padx=5)
        
        # Log
        log_frame = ttk.LabelFrame(inner, text="Log de Execução")
        log_frame.pack(fill=BOTH, expand=True)
        
        log_inner = ttk.Frame(log_frame)
        log_inner.pack(fill=BOTH, expand=True, padx=15, pady=15)
        
        self.log_text = scrolledtext.ScrolledText(log_inner, height=8, wrap=tk.WORD, font=("Consolas", 9))
        self.log_text.pack(fill=BOTH, expand=True)
        
        # Bind eventos
        self.excel_path.trace('w', lambda *args: self._update_preview())
        self.template_path.trace('w', lambda *args: self._update_preview())
    
    def _create_config_tab(self):
        """
        Cria a aba de configurações (SMTP e OAuth Google).
        """
        config_tab = ttk.Frame(self.notebook)
        self.notebook.add(config_tab, text="Configurações")
        
        # Canvas com scrollbar para permitir scroll
        canvas = tk.Canvas(config_tab, highlightthickness=0)
        scrollbar = ttk.Scrollbar(config_tab, orient="vertical", command=canvas.yview)
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
        
        # Frame interno com padding (agora dentro do scrollable_frame)
        inner = ttk.Frame(scrollable_frame)
        inner.pack(fill=BOTH, expand=True, padx=15, pady=15)
        
        # Seleção de método
        method_frame = ttk.LabelFrame(inner, text="Método de Envio")
        method_frame.pack(fill=X, pady=(0, 15))
        
        method_inner = ttk.Frame(method_frame)
        method_inner.pack(fill=BOTH, expand=True, padx=15, pady=15)
        
        def on_method_change():
            self._update_config_ui()
            # Salva preferência automaticamente
            try:
                config = {
                    'smtp_server': self.smtp_server.get(),
                    'smtp_port': self.smtp_port.get(),
                    'smtp_email': self.smtp_email.get(),
                    'smtp_password': self.smtp_password.get(),
                    'email_delay': self.email_delay.get(),
                    'use_oauth': self.use_oauth.get(),
                    'google_email': self.google_email.get()
                }
                self.config_manager.save_config(config)
            except Exception:
                pass  # Não falha se não conseguir salvar
        
        ttk.Radiobutton(
            method_inner,
            text="SMTP (Senha de App)",
            variable=self.use_oauth,
            value=False,
            command=on_method_change
        ).pack(anchor=W, pady=5)
        
        ttk.Radiobutton(
            method_inner,
            text="Google OAuth (Autenticação via Navegador)",
            variable=self.use_oauth,
            value=True,
            command=on_method_change
        ).pack(anchor=W, pady=5)
        
        # Frame de configurações SMTP
        self.smtp_frame = ttk.LabelFrame(inner, text="Configurações SMTP")
        self.smtp_frame.pack(fill=X, pady=(0, 15))
        
        smtp_inner = ttk.Frame(self.smtp_frame)
        smtp_inner.pack(fill=BOTH, expand=True, padx=15, pady=15)
        
        # Servidor SMTP
        server_frame = ttk.Frame(smtp_inner)
        server_frame.pack(fill=X, pady=5)
        ttk.Label(server_frame, text="Servidor SMTP:", width=20, anchor=E).pack(side=LEFT, padx=(0, 10))
        ttk.Entry(server_frame, textvariable=self.smtp_server, width=40).pack(side=LEFT)
        
        # Porta SMTP
        port_frame = ttk.Frame(smtp_inner)
        port_frame.pack(fill=X, pady=5)
        ttk.Label(port_frame, text="Porta SMTP:", width=20, anchor=E).pack(side=LEFT, padx=(0, 10))
        ttk.Entry(port_frame, textvariable=self.smtp_port, width=40).pack(side=LEFT)
        
        # Email
        email_frame = ttk.Frame(smtp_inner)
        email_frame.pack(fill=X, pady=5)
        ttk.Label(email_frame, text="Email (Remetente):", width=20, anchor=E).pack(side=LEFT, padx=(0, 10))
        ttk.Entry(email_frame, textvariable=self.smtp_email, width=40).pack(side=LEFT)
        
        # Senha (App Password)
        password_frame = ttk.Frame(smtp_inner)
        password_frame.pack(fill=X, pady=5)
        ttk.Label(password_frame, text="Senha de App:", width=20, anchor=E).pack(side=LEFT, padx=(0, 10))
        ttk.Entry(password_frame, textvariable=self.smtp_password, show="*", width=40).pack(side=LEFT)
        
        # Delay entre envios
        delay_frame = ttk.Frame(smtp_inner)
        delay_frame.pack(fill=X, pady=5)
        ttk.Label(delay_frame, text="Delay (segundos):", width=20, anchor=E).pack(side=LEFT, padx=(0, 10))
        ttk.Entry(delay_frame, textvariable=self.email_delay, width=40).pack(side=LEFT)
        ttk.Label(delay_frame, text="(Recomendado: 2.5s)", font=("Segoe UI", 8), bootstyle=SECONDARY).pack(side=LEFT, padx=(5, 0))
        
        # Botões de ação SMTP
        smtp_buttons_frame = ttk.Frame(smtp_inner)
        smtp_buttons_frame.pack(fill=X, pady=(15, 5))
        
        ttk.Button(smtp_buttons_frame, text="Testar Conexão", command=self._test_connection, bootstyle=INFO).pack(side=LEFT, padx=5)
        ttk.Button(smtp_buttons_frame, text="Salvar Configurações", command=self._save_config, bootstyle=SUCCESS).pack(side=LEFT, padx=5)
        
        # Frame de configurações OAuth Google
        self.oauth_frame = ttk.LabelFrame(inner, text="Configurações Google OAuth")
        self.oauth_frame.pack(fill=X, pady=(0, 15))
        
        oauth_inner = ttk.Frame(self.oauth_frame)
        oauth_inner.pack(fill=BOTH, expand=True, padx=15, pady=15)
        
        # Email Google
        google_email_frame = ttk.Frame(oauth_inner)
        google_email_frame.pack(fill=X, pady=5)
        ttk.Label(google_email_frame, text="Email Google:", width=20, anchor=E).pack(side=LEFT, padx=(0, 10))
        ttk.Entry(google_email_frame, textvariable=self.google_email, width=40).pack(side=LEFT)
        # Atualiza status quando email mudar (com tratamento de erro)
        def on_email_change(*args):
            try:
                self._check_oauth_status()
            except Exception as e:
                # Ignora erros durante digitação
                pass
        self.google_email.trace('w', on_email_change)
        
        # Status de autenticação
        status_frame = ttk.Frame(oauth_inner)
        status_frame.pack(fill=X, pady=10)
        ttk.Label(status_frame, text="Status:", width=20, anchor=E).pack(side=LEFT, padx=(0, 10))
        self.oauth_status_label = ttk.Label(status_frame, text="Não autenticado", font=("Segoe UI", 9), bootstyle=DANGER)
        self.oauth_status_label.pack(side=LEFT)
        
        # Botões OAuth
        oauth_buttons_frame = ttk.Frame(oauth_inner)
        oauth_buttons_frame.pack(fill=X, pady=(10, 5))
        
        self.oauth_login_btn = ttk.Button(oauth_buttons_frame, text="Autenticar com Google", command=self._oauth_authenticate, bootstyle=SUCCESS)
        self.oauth_login_btn.pack(side=LEFT, padx=5)
        
        self.oauth_logout_btn = ttk.Button(oauth_buttons_frame, text="Desconectar", command=self._oauth_logout, bootstyle=OUTLINE, state=DISABLED)
        self.oauth_logout_btn.pack(side=LEFT, padx=5)
        
        # Delay entre envios (OAuth)
        oauth_delay_frame = ttk.Frame(oauth_inner)
        oauth_delay_frame.pack(fill=X, pady=5)
        ttk.Label(oauth_delay_frame, text="Delay (segundos):", width=20, anchor=E).pack(side=LEFT, padx=(0, 10))
        ttk.Entry(oauth_delay_frame, textvariable=self.email_delay, width=40).pack(side=LEFT)
        ttk.Label(oauth_delay_frame, text="(Recomendado: 2.5s)", font=("Segoe UI", 8), bootstyle=SECONDARY).pack(side=LEFT, padx=(5, 0))
        
        # Atualiza UI inicial
        self._update_config_ui()
        
        # Informações
        info_frame = ttk.LabelFrame(inner, text="Informações")
        info_frame.pack(fill=X)
        
        info_inner = ttk.Frame(info_frame)
        info_inner.pack(fill=BOTH, expand=True, padx=15, pady=15)
        
        info_text = """
SMTP (Senha de App):
1. Ative a verificação em duas etapas na sua conta Google
2. Acesse: Conta Google → Segurança → Verificação em duas etapas → Senhas de app
3. Crie uma nova senha de app para "Email"
4. Use essa senha no campo "Senha de App"

Google OAuth:
1. Baixe o arquivo credentials.json do Google Cloud Console
2. Coloque o arquivo na pasta credentials/ do projeto
3. Digite seu email e clique em "Autenticar com Google"
4. Uma janela do navegador abrirá para autorizar o acesso
5. Após autorizar, não precisará fazer login novamente

Servidor SMTP padrão: smtp.gmail.com | Porta: 587
Delay recomendado: 2.5 segundos (para lotes de 50-300 emails)
        """
        ttk.Label(info_inner, text=info_text.strip(), font=("Segoe UI", 9), justify=LEFT).pack(anchor=W)
    
    def _select_excel(self):
        """
        Abre diálogo para seleção de arquivo Excel.
        """
        filename = filedialog.askopenfilename(
            title="Selecionar Planilha Excel",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")]
        )
        if filename:
            self.excel_path.set(filename)
            self._log(f"Planilha Excel selecionada: {Path(filename).name}")
            self._update_preview()
    
    def _select_template(self):
        """
        Abre diálogo para seleção de template.
        """
        filename = filedialog.askopenfilename(
            title="Selecionar Template",
            filetypes=[("Documentos", "*.docx *.txt"), ("Word", "*.docx"), ("Texto", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            self.template_path.set(filename)
            self._log(f"Template selecionado: {Path(filename).name}")
            self._update_preview()
    
    def _add_attachment(self):
        """
        Adiciona anexo à lista.
        """
        filenames = filedialog.askopenfilenames(
            title="Selecionar Anexos",
            filetypes=[("All files", "*.*")]
        )
        for filename in filenames:
            if filename not in self.attachments:
                self.attachments.append(filename)
                self.attachments_listbox.insert(tk.END, Path(filename).name)
                self._log(f"Anexo adicionado: {Path(filename).name}")
    
    def _remove_attachment(self):
        """
        Remove anexo selecionado da lista.
        """
        selection = self.attachments_listbox.curselection()
        if selection:
            index = selection[0]
            removed = self.attachments.pop(index)
            self.attachments_listbox.delete(index)
            self._log(f"Anexo removido: {Path(removed).name}")
    
    def _update_preview(self):
        """
        Atualiza preview do email.
        """
        self.preview_text.delete(1.0, tk.END)
        
        # Verifica se tem arquivos selecionados
        if not self.excel_path.get() or not self.template_path.get():
            self.preview_text.insert(1.0, "Selecione a planilha Excel e o template para visualizar o preview.")
            return
        
        try:
            # Lê Excel
            excel_reader = ExcelReader(self.excel_path.get())
            if not excel_reader.read():
                error_msg = excel_reader.last_error or "Erro ao ler planilha Excel."
                self.preview_text.insert(1.0, error_msg)
                return
            
            recipients = excel_reader.get_recipients()
            if not recipients:
                self.preview_text.insert(1.0, "Nenhum destinatário encontrado na planilha.")
                return
            
            # Processa template
            template_processor = TemplateProcessor(self.template_path.get())
            if not template_processor.load():
                error_msg = template_processor.last_error or "Erro ao carregar template."
                self.preview_text.insert(1.0, error_msg)
                return
            
            # Preview com primeiro destinatário
            sample_data = recipients[0]
            preview_body = template_processor.process(sample_data)
            
            # Monta preview completo
            if self.use_oauth.get():
                from_email = self.google_email.get() or "email@exemplo.com"
            else:
                from_email = self.smtp_email.get() or SMTP_EMAIL or "email@exemplo.com"
            preview = f"De: {from_email}\n"
            preview += f"Para: {sample_data.get('email', 'N/A')}\n"
            preview += f"Assunto: {self.subject.get() or '(sem assunto)'}\n"
            preview += f"\n{'='*60}\n\n"
            preview += preview_body
            preview += f"\n\n{'='*60}\n"
            preview += f"\nTotal de destinatários: {len(recipients)}\n"
            preview += f"Anexos: {len(self.attachments)}\n"
            
            self.preview_text.insert(1.0, preview)
            
        except Exception as e:
            self.preview_text.insert(1.0, f"Erro ao gerar preview: {e}")
    
    def _log(self, message: str):
        """
        Adiciona mensagem ao log.
        """
        def _write():
            self.log_text.insert(tk.END, f"{message}\n")
            self.log_text.see(tk.END)
            self.root.update_idletasks()
        self._run_on_ui_thread(_write)
    
    def _start_sending(self):
        """
        Inicia processo de envio de emails.
        """
        # Validações
        if not self.excel_path.get():
            messagebox.showerror("Erro", "Selecione a planilha Excel.")
            return
        
        if not self.template_path.get():
            messagebox.showerror("Erro", "Selecione o template.")
            return
        
        if not self.subject.get().strip():
            if not messagebox.askyesno("Confirmar", "Assunto está vazio. Deseja continuar?"):
                return
        
        # Carrega dados
        try:
            self.excel_reader = ExcelReader(self.excel_path.get())
            if not self.excel_reader.read():
                messagebox.showerror("Erro", self.excel_reader.last_error or "Erro ao ler planilha Excel.")
                return
            
            self.template_processor = TemplateProcessor(self.template_path.get())
            if not self.template_processor.load():
                messagebox.showerror("Erro", self.template_processor.last_error or "Erro ao carregar template.")
                return
            
            recipients = self.excel_reader.get_recipients()
            if not recipients:
                messagebox.showerror("Erro", "Nenhum destinatário encontrado na planilha.")
                return
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar dados: {e}")
            return
        
        # Confirma envio
        total = len(recipients)
        if not messagebox.askyesno(
            "Confirmar Envio",
            f"Tem certeza que deseja enviar {total} email(s)?\n\n"
            f"Assunto: {self.subject.get() or '(sem assunto)'}\n"
            f"Anexos: {len(self.attachments)}"
        ):
            return
        
        # Inicializa componentes baseado no método selecionado
        if self.use_oauth.get():
            # Usa Gmail API (OAuth)
            email = self.google_email.get().strip()
            if not email:
                messagebox.showerror("Erro", "Configure o email do Google na aba Configurações.")
                return
            
            # Verifica autenticação
            if not self.gmail_sender:
                from src.gmail_sender import GmailSender
                delay = float(self.email_delay.get() or '2.5')
                self.gmail_sender = GmailSender(email, delay)
            
            if not self.gmail_sender.is_authenticated():
                messagebox.showerror("Erro", "Não autenticado. Faça login na aba Configurações.")
                return
            
            self.email_sender = None  # Não usa SMTP
            metodo_envio = "OAuth (Gmail API)"
            remetente = email
        else:
            # Usa SMTP
            self.email_sender = EmailSender()
            self.gmail_sender = None
            metodo_envio = "SMTP"
            remetente = self.smtp_email.get() or SMTP_EMAIL or "N/A"
        
        # Obtém lista de emails do Excel
        excel_emails = [r.get('email', '') for r in recipients if r.get('email')]
        
        # Inicializa comprovação com informações da campanha
        campanha_name = self.campanha_name.get().strip() or None
        self.comprovacao = Comprovacao(
            campanha_name=campanha_name,
            template_path=self.template_path.get() if self.template_path.get() else None,
            attachments=self.attachments if self.attachments else None,
            excel_emails=excel_emails
        )
        
        # Define informações da campanha (inclui handshake para evidência)
        handshake = "EHLO/STARTTLS/EHLO" if not self.use_oauth.get() else "HTTPS Gmail API"
        self.comprovacao.set_campaign_info(
            metodo_envio=metodo_envio,
            remetente=remetente,
            assunto=self.subject.get(),
            handshake=handshake
        )
        
        # Atualiza UI
        self.is_sending = True
        self.should_stop = False
        self.start_btn.config(state=DISABLED)
        self.pause_btn.config(state=NORMAL)
        self.stop_btn.config(state=NORMAL)
        
        self._log("="*60)
        self._log(f"Iniciando envio de {total} email(s)...")
        self._log(f"Assunto: {self.subject.get()}")
        self._log(f"Anexos: {len(self.attachments)}")
        self._log("="*60)
        
        # Inicia thread de envio
        self.sending_thread = threading.Thread(target=self._sending_worker, args=(recipients,), daemon=True)
        self.sending_thread.start()
    
    def _sending_worker(self, recipients: List[dict]):
        """
        Worker thread para envio de emails.
        """
        try:
            from_email = (self.google_email.get() if self.use_oauth.get() else self.smtp_email.get()) or SMTP_EMAIL or "email@exemplo.com"
            sender = self.gmail_sender if self.use_oauth.get() else self.email_sender

            stats = self.batch_controller.run(
                recipients=recipients,
                subject=self.subject.get(),
                attachments=self.attachments if self.attachments else None,
                template_processor=self.template_processor,
                comprovacao=self.comprovacao,
                sender=sender,
                use_oauth=self.use_oauth.get(),
                from_email=from_email,
                stop_flag=lambda: self.should_stop,
            )

            self._log("="*60)
            self._log("Envio finalizado!")
            self._log(f"Total: {stats.get('total', 0)}")
            self._log(f"Enviados: {stats.get('enviados', 0)}")
            self._log(f"Erros: {stats.get('erros', 0)}")
            self._log(f"Comprovações salvas em: {self.comprovacao.get_campanha_dir()}")
            self._log("="*60)
            
        except Exception as e:
            self._log(f"ERRO CRÍTICO: {e}")
        finally:
            self._finish_sending()
    
    def _pause_sending(self):
        """
        Pausa o envio (implementação futura).
        """
        messagebox.showinfo("Info", "Funcionalidade de pausa será implementada em breve.")
    
    def _stop_sending(self):
        """
        Para o envio.
        """
        if messagebox.askyesno("Confirmar", "Deseja realmente parar o envio?"):
            self.should_stop = True
            self._log("Parando envio...")
    
    def _finish_sending(self):
        """
        Finaliza processo de envio e atualiza UI.
        """
        def _finish():
            self.is_sending = False
            self.start_btn.config(state=NORMAL)
            self.pause_btn.config(state=DISABLED)
            self.stop_btn.config(state=DISABLED)
        self._run_on_ui_thread(_finish)
    
    def _update_stats(self, total: int, enviados: int, erros: int):
        """
        Atualiza estatísticas na interface.
        """
        def _set():
            self.stats_label.config(text=f"Total: {total} | Enviados: {enviados} | Erros: {erros}")
            self.root.update_idletasks()
        self._run_on_ui_thread(_set)
    
    def _load_config(self):
        """
        Carrega configurações do arquivo .env e preenche os campos.
        """
        config = self.config_manager.get_config()
        self.smtp_server.set(config.get('smtp_server', 'smtp.gmail.com'))
        self.smtp_port.set(config.get('smtp_port', '587'))
        self.smtp_email.set(config.get('smtp_email', ''))
        self.smtp_password.set(config.get('smtp_password', ''))
        self.email_delay.set(config.get('email_delay', '2.5'))
        
        # Carrega preferência OAuth
        self.use_oauth.set(config.get('use_oauth', False))
        self.google_email.set(config.get('google_email', ''))
        
        # Atualiza UI baseado na preferência
        self._update_config_ui()
    
    def _save_config(self):
        """
        Salva configurações no arquivo .env.
        """
        config = {
            'smtp_server': self.smtp_server.get().strip(),
            'smtp_port': self.smtp_port.get().strip(),
            'smtp_email': self.smtp_email.get().strip(),
            'smtp_password': self.smtp_password.get().strip(),
            'email_delay': self.email_delay.get().strip(),
            'comprovacoes_dir': 'comprovacoes',
            'logs_dir': 'logs',
            'use_oauth': self.use_oauth.get(),  # Salva preferência OAuth
            'google_email': self.google_email.get()  # Salva email Google
        }
        
        # Validações (apenas se não estiver usando OAuth)
        if not config.get('use_oauth', False):
            if not config['smtp_email']:
                messagebox.showerror("Erro", "Email SMTP é obrigatório.")
                return
            
            if not config['smtp_password']:
                messagebox.showerror("Erro", "Senha de App é obrigatória.")
                return
        
        try:
            int(config['smtp_port'])
        except ValueError:
            messagebox.showerror("Erro", "Porta SMTP deve ser um número.")
            return
        
        try:
            float(config['email_delay'])
        except ValueError:
            messagebox.showerror("Erro", "Delay deve ser um número.")
            return
        
        # Salva
        success, message = self.config_manager.save_config(config)
        
        if success:
            # Recarrega configurações no módulo config
            from src.config import reload_config
            reload_config()
            
            self.config_status_label.config(text=message, bootstyle=SUCCESS)
            messagebox.showinfo("Sucesso", message)
        else:
            self.config_status_label.config(text=message, bootstyle=DANGER)
            messagebox.showerror("Erro", message)
    
    def _test_connection(self):
        """
        Testa conexão SMTP com as credenciais fornecidas.
        """
        smtp_server = self.smtp_server.get().strip()
        smtp_email = self.smtp_email.get().strip()
        smtp_password = self.smtp_password.get().strip()
        
        if not smtp_server:
            messagebox.showerror("Erro", "Servidor SMTP não informado.")
            return
        
        if not smtp_email:
            messagebox.showerror("Erro", "Email não informado.")
            return
        
        if not smtp_password:
            messagebox.showerror("Erro", "Senha não informada.")
            return
        
        try:
            smtp_port = int(self.smtp_port.get().strip())
        except ValueError:
            messagebox.showerror("Erro", "Porta SMTP inválida.")
            return
        
        # Testa conexão
        self.config_status_label.config(text="Testando conexão...", bootstyle=INFO)
        self.root.update()
        
        success, message = self.config_manager.test_connection(
            smtp_server, smtp_port, smtp_email, smtp_password
        )
        
        if success:
            self.config_status_label.config(text=message, bootstyle=SUCCESS)
            messagebox.showinfo("Sucesso", message)
        else:
            self.config_status_label.config(text=message, bootstyle=DANGER)
            messagebox.showerror("Erro", message)
    
    def _update_config_ui(self):
        """
        Atualiza a UI baseado no método selecionado (SMTP ou OAuth).
        """
        if self.use_oauth.get():
            # Mostra OAuth, esconde SMTP
            self.smtp_frame.pack_forget()
            self.oauth_frame.pack(fill=X, pady=(0, 15))
            # Verifica status OAuth
            self._check_oauth_status()
        else:
            # Mostra SMTP, esconde OAuth
            self.oauth_frame.pack_forget()
            self.smtp_frame.pack(fill=X, pady=(0, 15))
    
    def _check_oauth_status(self):
        """
        Verifica status de autenticação OAuth e atualiza UI.
        """
        email = self.google_email.get().strip()
        if not email:
            self.oauth_status_label.config(text="Digite o email", bootstyle=SECONDARY)
            self.oauth_login_btn.config(state=NORMAL)
            self.oauth_logout_btn.config(state=DISABLED)
            return
        
        # Inicializa GmailSender se necessário (com import lazy)
        if not self.gmail_sender or (hasattr(self.gmail_sender, 'email') and self.gmail_sender.email != email):
            try:
                # Import lazy - só importa quando necessário
                try:
                    from src.gmail_sender import GmailSender
                except ImportError as import_err:
                    # Se não conseguir importar, mostra erro e retorna
                    self.oauth_status_label.config(
                        text="Dependências Google não instaladas. Execute: pip install -r requirements.txt",
                        bootstyle=DANGER
                    )
                    self.oauth_login_btn.config(state=DISABLED)
                    self.oauth_logout_btn.config(state=DISABLED)
                    return
                
                delay = float(self.email_delay.get() or '2.5')
                self.gmail_sender = GmailSender(email, delay)
            except Exception as e:
                # Outros erros na inicialização
                error_type = type(e).__name__
                self.oauth_status_label.config(text=f"Erro: {error_type}", bootstyle=DANGER)
                self.oauth_login_btn.config(state=DISABLED)
                self.oauth_logout_btn.config(state=DISABLED)
                return
        
        # Verifica autenticação (com tratamento de erro)
        try:
            from src.logger import get_logger
            logger = get_logger()
            logger.debug(f"Verificando status OAuth para: {email}")
            
            if self.gmail_sender:
                is_auth = self.gmail_sender.is_authenticated()
                logger.debug(f"Status is_authenticated(): {is_auth}")
                
                if is_auth:
                    authenticated_email = self.gmail_sender.oauth.get_email()
                    logger.debug(f"Email obtido do OAuth: {authenticated_email}")
                    
                    if authenticated_email:
                        self.oauth_status_label.config(text=f"Autenticado: {authenticated_email}", bootstyle=SUCCESS)
                        self.oauth_login_btn.config(state=DISABLED)
                        self.oauth_logout_btn.config(state=NORMAL)
                        logger.info(f"Status OAuth atualizado: Autenticado - {authenticated_email}")
                    else:
                        # Se is_authenticated() retorna True mas não consegue obter email, ainda considera autenticado
                        self.oauth_status_label.config(text=f"Autenticado: {email}", bootstyle=SUCCESS)
                        self.oauth_login_btn.config(state=DISABLED)
                        self.oauth_logout_btn.config(state=NORMAL)
                        logger.info(f"Status OAuth atualizado: Autenticado (email não obtido, usando informado) - {email}")
                else:
                    self.oauth_status_label.config(text="Não autenticado", bootstyle=DANGER)
                    self.oauth_login_btn.config(state=NORMAL)
                    self.oauth_logout_btn.config(state=DISABLED)
                    logger.debug("Status OAuth: Não autenticado")
            else:
                self.oauth_status_label.config(text="Não autenticado", bootstyle=DANGER)
                self.oauth_login_btn.config(state=NORMAL)
                self.oauth_logout_btn.config(state=DISABLED)
                logger.debug("GmailSender não inicializado")
        except Exception as e:
            # Se houver erro ao verificar, assume não autenticado
            from src.logger import get_logger
            logger = get_logger()
            logger.exception(f"Erro ao verificar status OAuth: {e}")
            self.oauth_status_label.config(text="Erro ao verificar status", bootstyle=DANGER)
            self.oauth_login_btn.config(state=NORMAL)
            self.oauth_logout_btn.config(state=DISABLED)
    
    def _oauth_authenticate(self):
        """
        Realiza autenticação OAuth do Google.
        """
        email = self.google_email.get().strip()
        if not email:
            messagebox.showerror("Erro", "Digite o email do Google.")
            return
        
        # Inicializa GmailSender
        try:
            from src.gmail_sender import GmailSender
            delay = float(self.email_delay.get() or '2.5')
            self.gmail_sender = GmailSender(email, delay)
        except ImportError as e:
            messagebox.showerror(
                "Erro",
                f"Dependências Google não instaladas.\n\n"
                f"Execute no terminal:\n"
                f"pip install -r requirements.txt\n\n"
                f"Erro: {e}"
            )
            return
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao inicializar GmailSender: {e}")
            return
        
        # Atualiza status
        self.oauth_status_label.config(text="Abrindo navegador para autenticação...", bootstyle=INFO)
        self.oauth_login_btn.config(state=DISABLED)
        self.root.update()  # Atualiza UI imediatamente
        
        # Realiza autenticação em thread separada para não travar UI
        def authenticate_worker():
            try:
                from src.logger import get_logger
                logger = get_logger()
                logger.info(f"Iniciando autenticação OAuth para: {email}")
                
                success, message = self.gmail_sender.authenticate()
                
                if success:
                    logger.info(f"Autenticação OAuth bem-sucedida: {message}")
                else:
                    logger.warning(f"Autenticação OAuth falhou: {message}")
                
                # Atualiza UI na thread principal
                self.root.after(0, lambda: self._handle_oauth_result(success, message, email))
            except Exception as e:
                # Trata erros inesperados com mais detalhes
                error_type = type(e).__name__
                error_msg = str(e)
                from src.logger import get_logger
                logger = get_logger()
                logger.error(f"Erro inesperado na autenticação OAuth: {error_type}")
                logger.exception(f"Detalhes: {error_msg}")
                full_error_msg = f"Erro inesperado: {error_type}\n{error_msg[:200]}"
                self.root.after(0, lambda: self._handle_oauth_result(False, full_error_msg, email))
        
        # Executa autenticação em thread separada
        auth_thread = threading.Thread(target=authenticate_worker, daemon=True)
        auth_thread.start()
    
    def _handle_oauth_result(self, success: bool, message: str, email: str):
        """
        Trata resultado da autenticação OAuth (chamado na thread principal).
        
        Args:
            success: Se autenticação foi bem-sucedida
            message: Mensagem de resultado
            email: Email usado
        """
        # Salva preferência OAuth antes de processar resultado
        try:
            config = {
                'smtp_server': self.smtp_server.get(),
                'smtp_port': self.smtp_port.get(),
                'smtp_email': self.smtp_email.get(),
                'smtp_password': self.smtp_password.get(),
                'email_delay': self.email_delay.get(),
                'use_oauth': self.use_oauth.get(),
                'google_email': self.google_email.get()
            }
            self.config_manager.save_config(config)
        except Exception:
            pass  # Não falha se não conseguir salvar preferência
        
        if success:
            self.oauth_status_label.config(text=f"Autenticado: {email}", bootstyle=SUCCESS)
            self.oauth_login_btn.config(state=DISABLED)
            self.oauth_logout_btn.config(state=NORMAL)
            try:
                messagebox.showinfo("Sucesso", "Autenticação realizada com sucesso!\nVocê não precisará fazer login novamente.")
            except:
                pass  # Ignora se usuário fechar janela
        else:
            # Verifica se está autenticado mesmo com erro (pode ter dado warning mas funcionou)
            try:
                if self.gmail_sender and self.gmail_sender.is_authenticated():
                    # Está autenticado mesmo com erro - provavelmente foi um warning não crítico
                    authenticated_email = self.gmail_sender.oauth.get_email() or email
                    self.oauth_status_label.config(text=f"Autenticado: {authenticated_email}", bootstyle=SUCCESS)
                    self.oauth_login_btn.config(state=DISABLED)
                    self.oauth_logout_btn.config(state=NORMAL)
                    # Não mostra erro se estiver autenticado
                    return
            except Exception:
                pass
            
            # Se não está autenticado, mostra erro
            self.oauth_status_label.config(text="Erro na autenticação", bootstyle=DANGER)
            self.oauth_login_btn.config(state=NORMAL)
            self.oauth_logout_btn.config(state=DISABLED)
            
            if "cancelada" in message.lower() or "cancel" in message.lower():
                try:
                    messagebox.showwarning("Autenticação Cancelada", 
                        f"{message}\n\nVocê pode tentar novamente quando quiser.")
                except:
                    pass  # Ignora se usuário fechar a janela
            else:
                try:
                    # Mostra mensagem de erro sem mencionar credentials.json se já foi mencionado
                    if "credentials.json" in message:
                        messagebox.showerror("Erro", f"Erro na autenticação:\n{message}")
                    else:
                        messagebox.showerror("Erro", 
                            f"Erro na autenticação:\n{message}\n\nVerifique o console para mais detalhes.")
                except:
                    pass  # Ignora se usuário fechar a janela
    
    def _oauth_logout(self):
        """
        Desconecta autenticação OAuth.
        """
        if messagebox.askyesno("Confirmar", "Deseja realmente desconectar?"):
            if self.gmail_sender:
                self.gmail_sender.oauth.revoke_authentication()
                self.gmail_sender = None
            
            self.oauth_status_label.config(text="Desconectado", bootstyle=SECONDARY)
            self.oauth_login_btn.config(state=NORMAL)
            self.oauth_logout_btn.config(state=DISABLED)
    
    def _create_help_tab(self):
        """
        Cria a aba de ajuda usando a view separada.
        """
        from src.ui.views.help_tab import create_help_tab
        create_help_tab(self.notebook)
    
    def run(self):
        """
        Inicia a aplicação.
        """
        self.root.mainloop()

