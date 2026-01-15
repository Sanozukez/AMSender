# src/config.py
"""
Módulo de configuração do sistema.
Carrega variáveis de ambiente e configurações gerais.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

# Diretório raiz do projeto
PROJECT_ROOT = Path(__file__).parent.parent

# Configurações SMTP
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
SMTP_EMAIL = os.getenv('SMTP_EMAIL', '')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')

# Delay entre envios (em segundos)
# Recomendação Google: 1-2s para contas normais, 2-3s para lotes maiores (50-300 emails)
EMAIL_DELAY = float(os.getenv('EMAIL_DELAY', '2.5'))

# Diretório base em Documentos do usuário
def get_user_documents_dir() -> Path:
    """
    Retorna o diretório de Documentos do usuário.
    
    Returns:
        Path: Caminho para Documentos do usuário
    """
    try:
        # Windows
        documents = Path(os.path.expanduser("~")) / "Documents"
        if documents.exists():
            return documents
    except:
        pass
    
    # Fallback para diretório do projeto
    return PROJECT_ROOT

USER_DOCUMENTS = get_user_documents_dir()
APP_DATA_DIR = USER_DOCUMENTS / "AmatoolsMailSender"
LOGS_DIR = APP_DATA_DIR / "logs"

# Cria diretórios se não existirem
APP_DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# Mantém compatibilidade com código antigo
COMPROVACOES_DIR = LOGS_DIR

def reload_config():
    """
    Recarrega as configurações do arquivo .env.
    """
    load_dotenv(override=True)
    global SMTP_SERVER, SMTP_PORT, SMTP_EMAIL, SMTP_PASSWORD, EMAIL_DELAY
    SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
    SMTP_EMAIL = os.getenv('SMTP_EMAIL', '')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
    EMAIL_DELAY = float(os.getenv('EMAIL_DELAY', '2.5'))

def validate_config():
    """
    Valida se as configurações necessárias estão presentes.
    
    Returns:
        tuple: (is_valid, error_message)
    """
    if not SMTP_EMAIL:
        return False, "SMTP_EMAIL não configurado no arquivo .env"
    if not SMTP_PASSWORD:
        return False, "SMTP_PASSWORD não configurado no arquivo .env"
    return True, ""

