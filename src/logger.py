# src/logger.py
"""
Sistema de logging para o Mail Sender.
Salva logs em arquivo e também exibe no console.
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from src.config import get_user_documents_dir

class MailSenderLogger:
    """
    Logger customizado para o sistema Mail Sender.
    """
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MailSenderLogger, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if MailSenderLogger._initialized:
            return
        
        # Cria diretório de logs (com parents=True para criar diretórios pais se necessário)
        # Usa tratamento robusto de erros para evitar bloqueios do Windows Defender
        def _safe_mkdir(path: Path) -> bool:
            """Cria um diretório de forma segura."""
            try:
                path.mkdir(parents=True, exist_ok=True)
                return True
            except (OSError, PermissionError, FileNotFoundError, ValueError):
                return False
            except Exception:
                return False
        
        # Tenta criar em Documents primeiro
        self.logs_dir = get_user_documents_dir() / 'AmatoolsMailSender' / 'logs'
        if not _safe_mkdir(self.logs_dir):
            # Fallback 1: Diretório temporário
            import tempfile
            try:
                self.logs_dir = Path(tempfile.gettempdir()) / 'AmatoolsMailSender' / 'logs'
                if not _safe_mkdir(self.logs_dir):
                    raise Exception("Não foi possível criar em temp")
            except Exception:
                # Fallback 2: Diretório do executável
                import sys
                if getattr(sys, 'frozen', False):
                    self.logs_dir = Path(sys.executable).parent / 'AmatoolsMailSender' / 'logs'
                else:
                    from src.config import PROJECT_ROOT
                    self.logs_dir = PROJECT_ROOT / 'AmatoolsMailSender' / 'logs'
                _safe_mkdir(self.logs_dir)
        
        # Arquivo de log geral
        log_file = self.logs_dir / f'app_{datetime.now().strftime("%Y%m%d")}.log'
        
        # Configura logger
        self.logger = logging.getLogger('MailSender')
        self.logger.setLevel(logging.DEBUG)
        
        # Evita duplicação de handlers
        if self.logger.handlers:
            return
        
        # Handler para arquivo
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_format = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(name)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_format)
        
        # Handler para console
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setLevel(logging.INFO)
        console_format = logging.Formatter('%(levelname)s: %(message)s')
        console_handler.setFormatter(console_format)
        
        # Adiciona handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        MailSenderLogger._initialized = True
    
    def debug(self, message: str):
        """Log de debug."""
        self.logger.debug(message)
    
    def info(self, message: str):
        """Log de informação."""
        self.logger.info(message)
    
    def warning(self, message: str):
        """Log de aviso."""
        self.logger.warning(message)
    
    def error(self, message: str):
        """Log de erro."""
        self.logger.error(message)
    
    def exception(self, message: str):
        """Log de exceção com traceback."""
        self.logger.exception(message)
    
    def get_log_file(self) -> Path:
        """Retorna o caminho do arquivo de log atual."""
        return self.logs_dir / f'app_{datetime.now().strftime("%Y%m%d")}.log'

# Instância global
_logger = None

def get_logger() -> MailSenderLogger:
    """Retorna a instância do logger."""
    global _logger
    if _logger is None:
        _logger = MailSenderLogger()
    return _logger

