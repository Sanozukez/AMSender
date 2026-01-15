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
        
        # Cria diretório de logs
        self.logs_dir = get_user_documents_dir() / 'AmatoolsMailSender' / 'logs'
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
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

