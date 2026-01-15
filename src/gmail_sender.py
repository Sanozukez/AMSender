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
from pathlib import Path
from typing import List, Optional, Callable
from googleapiclient.errors import HttpError

from src.google_oauth import GoogleOAuth

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
        raw_message = base64.urlsafe_b64encode(msg.as_bytes()).decode('utf-8')
        return {'raw': raw_message}
    
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
            
            # Cria mensagem
            message = self._create_message(to_email, subject, body, attachments)
            
            # Tenta enviar com retry
            for attempt in range(retry_count):
                try:
                    # Envia email
                    sent_message = self.service.users().messages().send(
                        userId='me',
                        body=message
                    ).execute()
                    
                    # Obtém detalhes completos da mensagem
                    message_id = sent_message.get('id')
                    thread_id = sent_message.get('threadId')
                    
                    # Busca a mensagem para obter headers
                    try:
                        full_message = self.service.users().messages().get(
                            userId='me',
                            id=message_id,
                            format='full'
                        ).execute()
                        
                        # Extrai headers
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
                    except:
                        # Se não conseguir buscar headers, retorna pelo menos os IDs
                        return True, {
                            'message': f"Email enviado com sucesso. ID: {message_id}",
                            'gmail_message_id': message_id,
                            'gmail_thread_id': thread_id,
                            'message_id': None,
                            'headers': {}
                        }
                    
                except HttpError as e:
                    error_details = e.error_details[0] if e.error_details else {}
                    reason = error_details.get('reason', str(e))
                    
                    if reason == 'rateLimitExceeded':
                        if attempt < retry_count - 1:
                            time.sleep(5)  # Espera mais tempo para rate limit
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
                    enviados += 1
                    detalhes.append({
                        'email': to_email,
                        'status': 'enviado',
                        'mensagem': message.get('message', '') if isinstance(message, dict) else message,
                        'gmail_message_id': message.get('gmail_message_id') if isinstance(message, dict) else None,
                        'gmail_thread_id': message.get('gmail_thread_id') if isinstance(message, dict) else None,
                        'message_id': message.get('message_id') if isinstance(message, dict) else None,
                        'headers': message.get('headers', {}) if isinstance(message, dict) else {}
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

