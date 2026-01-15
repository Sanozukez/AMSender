# src/config_manager.py
"""
Módulo para gerenciar configurações SMTP através da interface.
Salva e carrega configurações do arquivo .env
"""

import os
from pathlib import Path
from typing import Tuple
from dotenv import set_key, load_dotenv

class ConfigManager:
    """
    Classe para gerenciar configurações do sistema.
    """
    
    def __init__(self, env_path: str = None):
        """
        Inicializa o gerenciador de configurações.
        
        Args:
            env_path: Caminho para o arquivo .env (opcional)
        """
        if env_path is None:
            env_path = Path(__file__).parent.parent / '.env'
        self.env_path = Path(env_path)
        
        # Garante que o arquivo existe
        if not self.env_path.exists():
            self.env_path.touch()
        
        # Carrega configurações atuais
        load_dotenv(self.env_path)
    
    def get_config(self) -> dict:
        """
        Retorna todas as configurações atuais.
        
        Returns:
            dict: Dicionário com as configurações
        """
        load_dotenv(self.env_path)
        return {
            'smtp_server': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
            'smtp_port': os.getenv('SMTP_PORT', '587'),
            'smtp_email': os.getenv('SMTP_EMAIL', ''),
            'smtp_password': os.getenv('SMTP_PASSWORD', ''),
            'email_delay': os.getenv('EMAIL_DELAY', '2.5'),
            'comprovacoes_dir': os.getenv('COMPROVACOES_DIR', 'comprovacoes'),
            'logs_dir': os.getenv('LOGS_DIR', 'logs'),
            'use_oauth': os.getenv('USE_OAUTH', 'false').lower() == 'true',
            'google_email': os.getenv('GOOGLE_EMAIL', '')
        }
    
    def save_config(self, config: dict) -> Tuple[bool, str]:
        """
        Salva configurações no arquivo .env.
        
        Args:
            config: Dicionário com as configurações a salvar
        
        Returns:
            tuple: (success, message) - True se salvou com sucesso, mensagem de erro se falhou
        """
        try:
            # Validações básicas (apenas se não estiver usando OAuth)
            if not config.get('use_oauth', False):
                if not config.get('smtp_email'):
                    return False, "Email SMTP é obrigatório"
                
                if not config.get('smtp_password'):
                    return False, "Senha SMTP é obrigatória"
            
            # Salva cada configuração
            set_key(str(self.env_path), 'SMTP_SERVER', config.get('smtp_server', 'smtp.gmail.com'))
            set_key(str(self.env_path), 'SMTP_PORT', str(config.get('smtp_port', '587')))
            set_key(str(self.env_path), 'SMTP_EMAIL', config.get('smtp_email', ''))
            set_key(str(self.env_path), 'SMTP_PASSWORD', config.get('smtp_password', ''))
            set_key(str(self.env_path), 'EMAIL_DELAY', str(config.get('email_delay', '2.5')))
            set_key(str(self.env_path), 'COMPROVACOES_DIR', config.get('comprovacoes_dir', 'comprovacoes'))
            set_key(str(self.env_path), 'LOGS_DIR', config.get('logs_dir', 'logs'))
            
            # Salva preferência OAuth (não requer validação)
            set_key(str(self.env_path), 'USE_OAUTH', 'true' if config.get('use_oauth', False) else 'false')
            set_key(str(self.env_path), 'GOOGLE_EMAIL', config.get('google_email', ''))
            
            return True, "Configurações salvas com sucesso!"
            
        except Exception as e:
            return False, f"Erro ao salvar configurações: {e}"
    
    def test_connection(self, smtp_server: str, smtp_port: int, smtp_email: str, smtp_password: str) -> tuple:
        """
        Testa conexão SMTP com as credenciais fornecidas.
        
        Args:
            smtp_server: Servidor SMTP
            smtp_port: Porta SMTP
            smtp_email: Email
            smtp_password: Senha
        
        Returns:
            tuple: (success, message)
        """
        try:
            import smtplib
            import ssl
            
            context = ssl.create_default_context()
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls(context=context)
            server.login(smtp_email, smtp_password)
            server.quit()
            
            return True, "Conexão testada com sucesso!"
            
        except smtplib.SMTPAuthenticationError:
            return False, "Erro de autenticação. Verifique email e senha."
        except smtplib.SMTPException as e:
            return False, f"Erro SMTP: {e}"
        except Exception as e:
            return False, f"Erro ao conectar: {e}"

