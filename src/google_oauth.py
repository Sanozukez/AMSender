# src/google_oauth.py
"""
Módulo para autenticação OAuth do Google.
Gerencia login via OAuth e salvamento de tokens.
"""

import os
import json
import pickle
import warnings
from pathlib import Path
from typing import Optional, Tuple
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Escopos necessários para envio de emails e leitura de perfil
# gmail.send: permite enviar emails
# userinfo.email: permite ler o email do usuário autenticado (para verificação)
SCOPES = [
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/userinfo.email'
]

class GoogleOAuth:
    """
    Classe para gerenciar autenticação OAuth do Google.
    """
    
    def __init__(self, email: str, credentials_dir: Optional[Path] = None):
        """
        Inicializa o gerenciador OAuth.
        
        Args:
            email: Email do Google para autenticação
            credentials_dir: Diretório para salvar tokens (opcional)
        """
        self.email = email
        if credentials_dir is None:
            credentials_dir = Path(__file__).parent.parent / 'credentials'
        self.credentials_dir = Path(credentials_dir)
        self.credentials_dir.mkdir(exist_ok=True)
        
        # Arquivo de token para este email
        safe_email = email.replace('@', '_at_').replace('.', '_')
        self.token_file = self.credentials_dir / f'token_{safe_email}.pickle'
        self.credentials_file = self.credentials_dir / 'credentials.json'
        
        self.creds: Optional[Credentials] = None
        self.service = None
    
    def is_authenticated(self) -> bool:
        """
        Verifica se já está autenticado.
        
        Returns:
            bool: True se autenticado, False caso contrário
        """
        from src.logger import get_logger
        logger = get_logger()
        logger.debug(f"Verificando autenticação OAuth para: {self.email}")
        logger.debug(f"Arquivo de token: {self.token_file}")
        logger.debug(f"Token existe: {self.token_file.exists()}")
        
        if not self.token_file.exists():
            logger.debug("Token não encontrado - não autenticado")
            return False
        
        try:
            with open(self.token_file, 'rb') as token:
                self.creds = pickle.load(token)
            
            logger.debug(f"Credenciais carregadas. Válidas: {self.creds.valid if self.creds else False}")
            logger.debug(f"Credenciais expiradas: {self.creds.expired if self.creds else False}")
            
            # Se as credenciais expiraram, tenta renovar
            if self.creds and self.creds.expired and self.creds.refresh_token:
                logger.info("Renovando token OAuth expirado...")
                self.creds.refresh(Request())
                self._save_credentials()
                logger.info("Token OAuth renovado com sucesso")
                return True
            
            is_valid = self.creds and self.creds.valid
            logger.debug(f"Resultado final is_authenticated: {is_valid}")
            return is_valid
            
        except (FileNotFoundError, PermissionError, pickle.UnpicklingError) as e:
            logger.warning(f"Erro ao verificar autenticação: {type(e).__name__}")
            return False
        except Exception as e:
            # Erro genérico - loga mas não expõe detalhes
            from src.logger import get_logger
            get_logger().exception(f"Erro inesperado ao verificar autenticação: {e}")
            return False
    
    def authenticate(self) -> Tuple[bool, str]:
        """
        Realiza autenticação OAuth via navegador.
        
        Returns:
            tuple: (success, message) - True se autenticado com sucesso
        """
        # Suprime warnings do Python sobre versão (não são críticos)
        # Isso evita que warnings do google.api_core sobre Python 3.10 interfiram
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=FutureWarning)
            warnings.filterwarnings("ignore", message=".*Python version.*")
            warnings.filterwarnings("ignore", message=".*google.api_core.*")
            return self._authenticate_internal()
    
    def _authenticate_internal(self) -> Tuple[bool, str]:
        """
        Implementação interna da autenticação.
        """
        try:
            # Verifica se já tem credenciais salvas
            if self.token_file.exists():
                with open(self.token_file, 'rb') as token:
                    self.creds = pickle.load(token)
            
            # Se não tem credenciais válidas, faz login
            if not self.creds or not self.creds.valid:
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    # Renova token expirado
                    self.creds.refresh(Request())
                else:
                    # Faz novo login
                    if not self.credentials_file.exists():
                        return False, "Arquivo credentials.json não encontrado. " \
                                     "Baixe as credenciais OAuth do Google Cloud Console e coloque em: " \
                                     f"{self.credentials_file}"
                    
                    flow = InstalledAppFlow.from_client_secrets_file(
                        str(self.credentials_file), SCOPES
                    )
                    # Abre navegador para autenticação
                    # Se o usuário fechar o navegador, isso pode gerar exceção
                    try:
                        from src.logger import get_logger
                        logger = get_logger()
                        logger.info("Iniciando fluxo OAuth no navegador...")
                        
                        # IMPORTANTE: O oauthlib lança Warning como exceção quando o escopo muda
                        # O Google adiciona automaticamente escopos como 'openid', gerando Warning
                        # mas isso NÃO impede a autenticação - as credenciais são obtidas normalmente
                        # O oauthlib usa `raise w` onde `w` é um Warning, fazendo com que seja tratado como exceção
                        # A melhor solução é interceptar o Warning antes que seja lançado como exceção
                        # usando um monkey patch temporário no oauthlib
                        
                        # Monkey patch temporário para interceptar o Warning sobre escopo
                        from oauthlib.oauth2.rfc6749.parameters import validate_token_parameters
                        original_validate = validate_token_parameters
                        
                        def patched_validate(params):
                            """Versão patchada que suprime Warning sobre escopo."""
                            try:
                                original_validate(params)
                            except Warning as w:
                                warning_msg = str(w).lower()
                                # Se for Warning sobre escopo, suprime (não relança)
                                if 'scope' in warning_msg or 'escopo' in warning_msg:
                                    logger.warning(f"Warning sobre escopo suprimido (não crítico): {w}")
                                    # Não relança o Warning - permite que o fluxo continue
                                    pass
                                else:
                                    # Outro tipo de Warning - relança
                                    raise
                        
                        # Aplica o monkey patch temporariamente
                        import oauthlib.oauth2.rfc6749.parameters
                        oauthlib.oauth2.rfc6749.parameters.validate_token_parameters = patched_validate
                        
                        try:
                            # Timeout de 5 minutos (300 segundos) - tempo razoável para o usuário completar
                            # Se o usuário fechar o navegador, o servidor local aguardará até o timeout
                            self.creds = flow.run_local_server(
                                port=0, 
                                open_browser=True,
                                timeout_seconds=300  # 5 minutos
                            )
                        finally:
                            # Restaura a função original
                            oauthlib.oauth2.rfc6749.parameters.validate_token_parameters = original_validate
                        
                        logger.info("Fluxo OAuth completado no navegador")
                        logger.debug(f"Credenciais obtidas: {self.creds is not None}")
                        if self.creds:
                            logger.debug(f"Credenciais válidas: {self.creds.valid}")
                            logger.debug(f"Tem refresh_token: {hasattr(self.creds, 'refresh_token') and self.creds.refresh_token is not None}")
                    except (KeyboardInterrupt, SystemExit):
                        # Usuário cancelou (Ctrl+C ou fechou navegador)
                        from src.logger import get_logger
                        get_logger().warning("Autenticação OAuth cancelada pelo usuário")
                        return False, "Autenticação cancelada pelo usuário"
                    except Warning as w:
                        # Warning não crítico - verifica se credenciais foram obtidas
                        from src.logger import get_logger
                        logger = get_logger()
                        warning_msg = str(w).lower()
                        logger.warning(f"Warning durante fluxo OAuth: {w}")
                        
                        # Se for Warning sobre escopo, pode ser que as credenciais foram obtidas
                        if 'scope' in warning_msg or 'escopo' in warning_msg:
                            if self.creds and hasattr(self.creds, 'valid') and self.creds.valid:
                                logger.info("Credenciais válidas obtidas mesmo com Warning sobre escopo - continuando...")
                                # Não retorna erro, continua para salvar credenciais
                            else:
                                logger.warning("Warning sobre escopo impediu obtenção de credenciais")
                                return False, f"Warning sobre escopo: {str(w)[:200]}\n\nIsso pode acontecer se o Google adicionar escopos automaticamente. Tente novamente."
                        else:
                            # Outro tipo de Warning
                            if self.creds and hasattr(self.creds, 'valid') and self.creds.valid:
                                logger.info("Credenciais válidas obtidas mesmo com Warning - continuando...")
                                # Não retorna erro, continua para salvar credenciais
                            else:
                                return False, f"Warning durante autenticação: {str(w)[:200]}"
                    except Exception as e:
                        # Outros erros (ex: navegador fechado antes de completar, timeout)
                        from src.logger import get_logger
                        logger = get_logger()
                        error_msg = str(e).lower()
                        error_type = type(e).__name__
                        logger.warning(f"Erro durante fluxo OAuth: {error_type}")
                        logger.exception(f"Detalhes: {error_msg[:300]}")
                        
                        # Verifica se foi cancelamento ou timeout
                        if any(keyword in error_msg for keyword in ['cancelled', 'cancel', 'closed', 'timeout', 'timed out']):
                            return False, "Autenticação cancelada ou expirada. Tente novamente."
                        
                        # Se for erro de conexão ou servidor
                        if any(keyword in error_msg for keyword in ['connection', 'server', 'refused']):
                            return False, f"Erro de conexão: {error_type}"
                        
                        # Outros erros - mas verifica se credenciais foram obtidas mesmo assim
                        # Pode ser que o erro ocorreu após obter as credenciais
                        if self.creds and hasattr(self.creds, 'valid') and self.creds.valid:
                            logger.info("Credenciais válidas obtidas mesmo com erro - continuando...")
                            # Não retorna erro, continua para salvar credenciais
                        else:
                            logger.warning(f"Credenciais não obtidas após erro: {error_type}")
                            return False, f"Erro na autenticação: {error_type}"
                
                # Salva credenciais ANTES de verificar email (mais importante)
                from src.logger import get_logger
                logger = get_logger()
                logger.info("Salvando credenciais OAuth...")
                logger.debug(f"Credenciais obtidas: {self.creds is not None}")
                if self.creds:
                    logger.debug(f"Credenciais válidas: {self.creds.valid}")
                    logger.debug(f"Credenciais expiradas: {self.creds.expired}")
                    logger.debug(f"Tem refresh_token: {hasattr(self.creds, 'refresh_token') and self.creds.refresh_token is not None}")
                
                try:
                    self._save_credentials()
                    logger.info("Credenciais OAuth salvas com sucesso")
                except Exception as save_error:
                    # Se falhar ao salvar, retorna erro específico
                    error_type = type(save_error).__name__
                    error_msg = str(save_error)
                    logger.error(f"Erro ao salvar credenciais OAuth: {error_type}")
                    logger.exception(f"Detalhes: {error_msg}")
                    return False, f"Erro ao salvar credenciais: {error_type}. Verifique permissões da pasta credentials/."
            
            # Verifica se o email corresponde (opcional - se falhar, usa o email informado)
            # Esta verificação é opcional e não deve falhar a autenticação
            # IMPORTANTE: Se der Warning aqui, as credenciais já foram salvas, então é sucesso
            if self.creds:
                try:
                    # Tenta obter email do perfil usando Gmail API
                    service = build('gmail', 'v1', credentials=self.creds)
                    profile = service.users().getProfile(userId='me').execute()
                    authenticated_email = profile.get('emailAddress', '')
                    
                    if authenticated_email and authenticated_email.lower() != self.email.lower():
                        # Avisa mas não falha - o token é válido
                        import sys
                        print(f"[WARNING] Email autenticado ({authenticated_email}) difere do informado ({self.email})", file=sys.stderr)
                except HttpError as e:
                    # Se der erro 403 ou outro erro, tenta usar o serviço de userinfo
                    if e.resp.status == 403:
                        try:
                            # Tenta usar o serviço de userinfo (se tiver o escopo)
                            userinfo_service = build('oauth2', 'v2', credentials=self.creds)
                            user_info = userinfo_service.userinfo().get().execute()
                            authenticated_email = user_info.get('email', '')
                            
                            if authenticated_email and authenticated_email.lower() != self.email.lower():
                                # Avisa mas não falha
                                import sys
                                print(f"[WARNING] Email autenticado ({authenticated_email}) difere do informado ({self.email})", file=sys.stderr)
                        except Exception as userinfo_err:
                            # Se não conseguir verificar, confia no email informado pelo usuário
                            # Isso é aceitável pois o token OAuth já foi validado
                            from src.logger import get_logger
                            get_logger().info(f"Não foi possível verificar email via userinfo: {type(userinfo_err).__name__}")
                            pass
                    else:
                        # Outro tipo de erro HTTP - não crítico, continua
                        from src.logger import get_logger
                        get_logger().info(f"Erro HTTP {e.resp.status} ao verificar perfil, mas autenticação foi bem-sucedida")
                        pass
                except Exception as verify_err:
                    # Se não conseguir verificar, confia no email informado
                    # O token OAuth já foi validado, então podemos confiar
                    # Se for Warning, não é crítico pois credenciais já foram salvas
                    from src.logger import get_logger
                    logger = get_logger()
                    error_type_verify = type(verify_err).__name__
                    if 'Warning' in error_type_verify:
                        logger.warning(f"Warning durante verificação de email (não crítico): {error_type_verify}")
                    else:
                        logger.info(f"Não foi possível verificar email: {error_type_verify}")
                    pass
            
            # Se chegou aqui, autenticação foi bem-sucedida
            from src.logger import get_logger
            get_logger().info(f"Autenticação OAuth bem-sucedida para: {self.email}")
            return True, "Autenticação realizada com sucesso!"
            
        except FileNotFoundError:
            return False, f"Arquivo credentials.json não encontrado em: {self.credentials_file}"
        except PermissionError:
            return False, f"Sem permissão para acessar: {self.credentials_file}"
        except Exception as e:
            error_type = type(e).__name__
            error_msg = str(e)
            
            # Log detalhado do erro em arquivo
            from src.logger import get_logger
            logger = get_logger()
            logger.error(f"Erro na autenticação OAuth: {error_type}")
            logger.exception(f"Detalhes do erro: {error_msg[:500]}")
            logger.debug(f"Credenciais após erro: {self.creds is not None}")
            if self.creds:
                logger.debug(f"Credenciais válidas após erro: {self.creds.valid if hasattr(self.creds, 'valid') else 'N/A'}")
            
            # IMPORTANTE: Verifica se as credenciais foram obtidas mesmo com erro
            # Isso pode acontecer se houver um Warning não crítico durante a verificação do email
            # Se o token já foi salvo (arquivo existe), então a autenticação foi bem-sucedida
            if self.token_file.exists():
                logger.info("Token já foi salvo - autenticação foi bem-sucedida mesmo com erro")
                return True, "Autenticação realizada com sucesso!"
            
            # Se não tem token salvo, verifica se tem credenciais válidas para salvar
            if self.creds and hasattr(self.creds, 'valid') and self.creds.valid:
                logger.info("Credenciais válidas obtidas mesmo com erro - tentando salvar...")
                try:
                    self._save_credentials()
                    logger.info("Credenciais OAuth salvas com sucesso após erro")
                    # Se conseguiu salvar, autenticação foi bem-sucedida
                    return True, "Autenticação realizada com sucesso!"
                except Exception as save_err:
                    logger.exception(f"Erro ao salvar credenciais após erro: {save_err}")
                    return False, f"Erro ao salvar credenciais: {type(save_err).__name__}. Verifique permissões da pasta credentials/."
            
            # Se não tem credenciais válidas, retorna erro detalhado
            # Mensagens específicas para tipos comuns de erro
            if 'Warning' in error_type or 'warning' in error_msg.lower():
                logger.warning(f"Warning capturado mas credenciais não obtidas. Tipo: {error_type}, Mensagem: {error_msg[:200]}")
                return False, f"Warning durante autenticação: {error_msg[:200]}\n\nVerifique o arquivo de log para mais detalhes:\n{logger.get_log_file()}"
            
            # Não expõe detalhes sensíveis
            if 'credentials' in error_msg.lower() or 'token' in error_msg.lower():
                return False, f"Erro na autenticação: {error_type}.\n\nVerifique o arquivo credentials.json em:\n{self.credentials_file}"
            
            # Mensagem genérica mas informativa
            return False, f"Erro na autenticação: {error_type}\n\nDetalhes: {error_msg[:200]}\n\nVerifique o arquivo de log para mais informações."
    
    def _save_credentials(self):
        """
        Salva credenciais no arquivo.
        """
        if not self.creds:
            return
        
        try:
            with open(self.token_file, 'wb') as token:
                pickle.dump(self.creds, token)
        except (IOError, OSError, PermissionError) as e:
            raise Exception(f"Erro ao salvar credenciais: {type(e).__name__}")
        except Exception as e:
            raise Exception(f"Erro inesperado ao salvar credenciais: {type(e).__name__}")
    
    def get_service(self):
        """
        Retorna serviço Gmail API autenticado.
        
        Returns:
            Service: Serviço Gmail API
        """
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
                self._save_credentials()
            else:
                raise Exception("Não autenticado. Execute authenticate() primeiro.")
        
        if not self.service:
            self.service = build('gmail', 'v1', credentials=self.creds)
        
        return self.service
    
    def revoke_authentication(self) -> bool:
        """
        Revoga autenticação e remove token.
        
        Returns:
            bool: True se revogado com sucesso
        """
        try:
            if self.token_file.exists():
                self.token_file.unlink()
            
            if self.creds:
                try:
                    self.creds.revoke(Request())
                except:
                    pass
                self.creds = None
            
            self.service = None
            return True
            
        except Exception:
            return False
    
    def get_email(self) -> Optional[str]:
        """
        Retorna o email autenticado.
        Tenta obter do perfil, mas se não conseguir, retorna o email informado.
        
        Returns:
            str: Email autenticado ou None
        """
        if not self.is_authenticated():
            return None
        
        try:
            # Tenta obter do Gmail API
            service = self.get_service()
            profile = service.users().getProfile(userId='me').execute()
            email = profile.get('emailAddress')
            if email:
                return email
        except HttpError as e:
            # Se der 403, tenta usar o serviço de userinfo
            if e.resp.status == 403:
                try:
                    from googleapiclient.discovery import build
                    userinfo_service = build('oauth2', 'v2', credentials=self.creds)
                    user_info = userinfo_service.userinfo().get().execute()
                    return user_info.get('email')
                except Exception:
                    pass
        except Exception:
            pass
        
        # Se não conseguir obter do perfil, retorna o email informado
        # (o token já foi validado, então podemos confiar)
        return self.email

