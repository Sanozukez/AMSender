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

# Cria diretórios se não existirem (com parents=True para criar diretórios pais se necessário)
# Usa tratamento robusto de erros para evitar bloqueios do Windows Defender
def _safe_mkdir(path: Path) -> bool:
    """
    Cria um diretório de forma segura, tratando todos os erros possíveis.
    
    Args:
        path: Caminho do diretório a criar
        
    Returns:
        bool: True se criado com sucesso, False caso contrário
    """
    try:
        path.mkdir(parents=True, exist_ok=True)
        return True
    except (OSError, PermissionError, FileNotFoundError, ValueError) as e:
        # Loga o erro mas não interrompe a execução
        try:
            import logging
            logging.warning(f"Não foi possível criar diretório {path}: {e}")
        except:
            pass
        return False
    except Exception as e:
        # Captura qualquer outro erro inesperado
        try:
            import logging
            logging.warning(f"Erro inesperado ao criar diretório {path}: {e}")
        except:
            pass
        return False

# Tenta criar diretórios com fallbacks progressivos
if not _safe_mkdir(APP_DATA_DIR) or not _safe_mkdir(LOGS_DIR):
    # Fallback 1: Diretório temporário
    import tempfile
    try:
        temp_dir = Path(tempfile.gettempdir())
        APP_DATA_DIR = temp_dir / "AmatoolsMailSender"
        LOGS_DIR = APP_DATA_DIR / "logs"
        if not _safe_mkdir(APP_DATA_DIR) or not _safe_mkdir(LOGS_DIR):
            raise Exception("Não foi possível criar em temp")
    except Exception:
        # Fallback 2: Diretório do executável
        import sys
        try:
            if getattr(sys, 'frozen', False):
                APP_DATA_DIR = Path(sys.executable).parent / "AmatoolsMailSender"
            else:
                APP_DATA_DIR = PROJECT_ROOT / "AmatoolsMailSender"
            LOGS_DIR = APP_DATA_DIR / "logs"
            _safe_mkdir(APP_DATA_DIR)
            _safe_mkdir(LOGS_DIR)
        except Exception:
            # Último recurso: usa o diretório atual
            APP_DATA_DIR = Path.cwd() / "AmatoolsMailSender"
            LOGS_DIR = APP_DATA_DIR / "logs"
            _safe_mkdir(APP_DATA_DIR)
            _safe_mkdir(LOGS_DIR)

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

