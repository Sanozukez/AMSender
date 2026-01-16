# src/gmail_sender.py
"""
Módulo para envio de emails via Gmail API (OAuth).
Alternativa ao SMTP para envio de emails.
"""

import base64
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from email.utils import formatdate
from pathlib import Path
from typing import List, Optional, Callable
import hashlib
from googleapiclient.errors import HttpError

from src.google_oauth import GoogleOAuth
from src.validators import Validators
from src.logger import get_logger

class GmailSender:
    """
    Classe para envio de emails via Gmail API.
    """
    
    def __init__(self, email: str, delay: float = 2.5):
        """
        Inicializa o sender de emails via Gmail API.
        
        Args:
            email: Email do Google para envio
            delay: Delay entre envios (em segundos)
        """
        self.email = email
        self.delay = delay
        self.oauth = GoogleOAuth(email)
        self.service = None

    def _refresh_auth(self) -> bool:
        """Tenta renovar o token e reconstruir o serviço."""
        try:
            if not self.oauth.is_authenticated():
                return False
            self.service = self.oauth.get_service()
            return True
        except Exception as e:
            get_logger().warning(f"Falha ao renovar token OAuth: {e}")
            return False
    
    def is_authenticated(self) -> bool:
        """
        Verifica se está autenticado.
        
        Returns:
            bool: True se autenticado
        """
        return self.oauth.is_authenticated()
    
    def authenticate(self) -> tuple:
        """
        Realiza autenticação OAuth.
        
        Returns:
            tuple: (success, message)
        """
        return self.oauth.authenticate()
    
    def _create_message(
        self,
        to_email: str,
        subject: str,
        body: str,
        attachments: Optional[List[str]] = None
    ) -> dict:
        """
        Cria mensagem de email no formato Gmail API.
        
        Args:
            to_email: Email do destinatário
            subject: Assunto do email
            body: Corpo do email
            attachments: Lista de caminhos para anexos
        
        Returns:
            dict: Mensagem no formato Gmail API
        """
        # Cria mensagem MIME
        msg = MIMEMultipart()
        msg['To'] = to_email
        msg['From'] = self.email
        msg['Subject'] = subject
        msg['Date'] = formatdate(localtime=True)
        import uuid
        msg['Message-ID'] = msg.get('Message-ID') or f"<{uuid.uuid4()}@amatools.com.br>"
        
        # Adiciona corpo
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        # Adiciona anexos
        if attachments:
            for attachment_path in attachments:
                    try:
                        path = Path(attachment_path)
                        if path.exists() and path.is_file():
                            with open(path, 'rb') as f:
                                part = MIMEBase('application', 'octet-stream')
                                part.set_payload(f.read())
                            
                            encoders.encode_base64(part)
                            part.add_header(
                                'Content-Disposition',
                                f'attachment; filename= {path.name}'
                            )
                            msg.attach(part)
                    except (FileNotFoundError, PermissionError, OSError):
                        # Log erro mas continua com outros anexos
                        pass
                    except Exception:
                        # Log erro genérico
                        pass
        
        # Converte para formato Gmail API
        raw_bytes = msg.as_bytes()
        raw_message = base64.urlsafe_b64encode(raw_bytes).decode('utf-8')
        return {'raw': raw_message, 'mime': msg, 'raw_bytes': raw_bytes}
    
    def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        attachments: Optional[List[str]] = None,
        retry_count: int = 3
    ) -> tuple:
        """
        Envia um email via Gmail API.
        
        Args:
            to_email: Email do destinatário
            subject: Assunto do email
            body: Corpo do email
            attachments: Lista de caminhos para anexos
            retry_count: Número de tentativas em caso de erro
        
        Returns:
            tuple: (success, message)
        """
        if not self.is_authenticated():
            return False, "Não autenticado. Execute authenticate() primeiro."
        
        try:
            # Obtém serviço
            if not self.service:
                self.service = self.oauth.get_service()
            
            # Cria mensagem e mantém headers locais para evidência
            message_data = self._create_message(to_email, subject, body, attachments)
            message = {'raw': message_data['raw']}
            local_headers = dict(message_data['mime'].items())
            raw_bytes = message_data['raw_bytes']
            
            attempted_refresh = False
            
            # Tenta enviar com retry
            for attempt in range(retry_count):
                try:
                    sent_message = self.service.users().messages().send(
                        userId='me',
                        body=message
                    ).execute()
                    
                    message_id = sent_message.get('id')
                    thread_id = sent_message.get('threadId')
                    
                    try:
                        full_message = self.service.users().messages().get(
                            userId='me',
                            id=message_id,
                            format='full'
                        ).execute()
                        headers = {}
                        for header in full_message.get('payload', {}).get('headers', []):
                            headers[header['name']] = header['value']
                        
                        return True, {
                            'message': f"Email enviado com sucesso. ID: {message_id}",
                            'gmail_message_id': message_id,
                            'gmail_thread_id': thread_id,
                            'message_id': headers.get('Message-ID'),
                            'headers': headers
                        }
                    except Exception:
                        # Fallback: usa headers locais da mensagem
                        return True, {
                            'message': f"Email enviado com sucesso. ID: {message_id}",
                            'gmail_message_id': message_id,
                            'gmail_thread_id': thread_id,
                            'message_id': local_headers.get('Message-ID'),
                            'headers': local_headers,
                            'raw': message_data['raw'],
                            'history_id': sent_message.get('historyId')
                        }
                    
                except HttpError as e:
                    status = getattr(getattr(e, 'resp', None), 'status', None)
                    error_details = getattr(e, 'error_details', None) or []
                    error_detail = error_details[0] if error_details else {}
                    reason = error_detail.get('reason', str(e))
                    auth_error = status in (401, 403) or 'auth' in str(e).lower() or 'invalid_grant' in str(e).lower()
                    
                    if auth_error and not attempted_refresh:
                        get_logger().warning(f"Token possivelmente expirado (status {status}, reason {reason}), tentando renovar...")
                        attempted_refresh = True
                        if self._refresh_auth():
                            time.sleep(1)
                            continue
                        return False, "Autenticação expirada. Faça login novamente."
                    
                    if reason == 'rateLimitExceeded':
                        if attempt < retry_count - 1:
                            time.sleep(5)
                            continue
                        return False, f"Limite de taxa excedido: {e}"
                    elif reason == 'quotaExceeded':
                        return False, f"Cota excedida: {e}"
                    else:
                        if attempt < retry_count - 1:
                            time.sleep(2)
                            continue
                        return False, f"Erro Gmail API: {e}"
                except Exception as e:
                    get_logger().warning(f"Erro inesperado Gmail API: {e}")
                    if attempt < retry_count - 1:
                        time.sleep(2)
                        continue
                    return False, f"Erro inesperado: {e}"
            
            return False, "Falha após múltiplas tentativas"
            
        except Exception as e:
            return False, f"Erro ao enviar email: {e}"
    
    def send_batch(
        self,
        recipients: List[dict],
        subject: str,
        get_body: Callable[[dict], str],
        attachments: Optional[List[str]] = None,
        progress_callback: Optional[Callable[[int, int, dict], None]] = None,
        stop_flag: Optional[Callable[[], bool]] = None
    ) -> dict:
        """
        Envia emails em lote com delay entre envios.
        
        Args:
            recipients: Lista de destinatários (dicts com dados)
            subject: Assunto do email
            get_body: Função que recebe dados do destinatário e retorna corpo do email
            attachments: Lista de caminhos para anexos
            progress_callback: Callback chamado a cada envio (current, total, recipient_data)
            stop_flag: Função que retorna True se deve parar o envio
        
        Returns:
            dict: Estatísticas do envio {'total': int, 'enviados': int, 'erros': int, 'detalhes': list}
        """
        total = len(recipients)
        enviados = 0
        erros = 0
        detalhes = []
        
        for idx, recipient in enumerate(recipients, 1):
            # Verifica se deve parar
            if stop_flag and stop_flag():
                break
            
            to_email = recipient.get('email', '')
            if not to_email:
                erros += 1
                detalhes.append({
                    'email': to_email,
                    'status': 'erro',
                    'mensagem': 'Email não fornecido'
                })
                continue

            # Valida email
            is_valid, err_msg = Validators.validate_email(to_email)
            if not is_valid:
                erros += 1
                detalhes.append({
                    'email': to_email,
                    'status': 'erro',
                    'mensagem': err_msg or 'Email inválido'
                })
                continue
            
            # Obtém corpo do email
            try:
                body = get_body(recipient)
            except Exception as e:
                erros += 1
                detalhes.append({
                    'email': to_email,
                    'status': 'erro',
                    'mensagem': f'Erro ao processar template: {e}'
                })
                continue
            
            # Envia email
            result = self.send_email(to_email, subject, body, attachments)
            
            if isinstance(result, tuple):
                success, message = result
                if success:
                    # Hash dos anexos (se houver)
                    att_hashes = {}
                    if attachments:
                        for att in attachments:
                            try:
                                h = hashlib.sha256()
                                with open(att, 'rb') as f:
                                    for chunk in iter(lambda: f.read(8192), b''):
                                        h.update(chunk)
                                att_hashes[Path(att).name] = h.hexdigest()
                            except Exception:
                                pass
                    # Hash do raw (se retornado)
                    raw_b64 = message.get('raw') if isinstance(message, dict) else None
                    raw_hash = None
                    if raw_b64:
                        try:
                            raw_bytes = base64.urlsafe_b64decode(raw_b64.encode('utf-8'))
                            h_raw = hashlib.sha256()
                            h_raw.update(raw_bytes)
                            raw_hash = h_raw.hexdigest()
                        except Exception:
                            pass

                    enviados += 1
                    detalhes.append({
                        'email': to_email,
                        'status': 'enviado',
                        'mensagem': message.get('message', '') if isinstance(message, dict) else message,
                        'gmail_message_id': message.get('gmail_message_id') if isinstance(message, dict) else None,
                        'gmail_thread_id': message.get('gmail_thread_id') if isinstance(message, dict) else None,
                        'message_id': message.get('message_id') if isinstance(message, dict) else None,
                        'headers': message.get('headers', {}) if isinstance(message, dict) else {},
                        'attachments_hashes': att_hashes,
                        'raw_hash': raw_hash,
                        'history_id': message.get('history_id') if isinstance(message, dict) else None,
                        'raw': raw_b64
                    })
                else:
                    erros += 1
                    detalhes.append({
                        'email': to_email,
                        'status': 'erro',
                        'mensagem': message if isinstance(message, str) else str(message)
                    })
            else:
                # Compatibilidade com formato antigo
                success, message = result
                if success:
                    enviados += 1
                    detalhes.append({
                        'email': to_email,
                        'status': 'enviado',
                        'mensagem': message if isinstance(message, str) else str(message)
                    })
                else:
                    erros += 1
                    detalhes.append({
                        'email': to_email,
                        'status': 'erro',
                        'mensagem': message if isinstance(message, str) else str(message)
                    })
            
            # Callback de progresso
            if progress_callback:
                progress_callback(idx, total, recipient)
            
            # Delay entre envios (exceto no último)
            if idx < total:
                time.sleep(self.delay)
        
        return {
            'total': total,
            'enviados': enviados,
            'erros': erros,
            'detalhes': detalhes
        }

