# src/email_sender.py
"""
Módulo para envio de emails via SMTP.
Suporta envio com anexos e tratamento robusto de erros.
"""

import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path
from typing import List, Optional, Callable, Tuple
import ssl

from src.config import SMTP_SERVER, SMTP_PORT, SMTP_EMAIL, SMTP_PASSWORD, EMAIL_DELAY

class EmailSender:
    """
    Classe para envio de emails via SMTP.
    """
    
    def __init__(self):
        """
        Inicializa o sender de emails.
        """
        self.smtp_server = SMTP_SERVER
        self.smtp_port = SMTP_PORT
        self.smtp_email = SMTP_EMAIL
        self.smtp_password = SMTP_PASSWORD
        self.delay = EMAIL_DELAY
        self.server: Optional[smtplib.SMTP] = None
        self.is_connected = False
        
    def connect(self) -> bool:
        """
        Conecta ao servidor SMTP.
        
        Returns:
            bool: True se conexão foi bem-sucedida, False caso contrário
        """
        try:
            # Cria contexto SSL
            context = ssl.create_default_context()
            
            # Conecta ao servidor
            self.server = smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=30)
            self.server.starttls(context=context)
            
            # Autentica
            self.server.login(self.smtp_email, self.smtp_password)
            
            self.is_connected = True
            return True
            
        except (smtplib.SMTPAuthenticationError, smtplib.SMTPException) as e:
            self.is_connected = False
            return False
        except (ConnectionError, TimeoutError, OSError) as e:
            self.is_connected = False
            return False
        except Exception as e:
            self.is_connected = False
            return False
    
    def disconnect(self):
        """
        Desconecta do servidor SMTP de forma segura.
        """
        if self.server and self.is_connected:
            try:
                self.server.quit()
            except (smtplib.SMTPException, AttributeError):
                # Tenta fechar forçadamente se quit() falhar
                try:
                    self.server.close()
                except:
                    pass
            except Exception:
                # Ignora outros erros ao desconectar
                pass
            finally:
                self.is_connected = False
                self.server = None
    
    def create_message(
        self,
        to_email: str,
        subject: str,
        body: str,
        attachments: Optional[List[str]] = None
    ) -> MIMEMultipart:
        """
        Cria mensagem de email com anexos.
        
        Args:
            to_email: Email do destinatário
            subject: Assunto do email
            body: Corpo do email (texto)
            attachments: Lista de caminhos para arquivos anexos
        
        Returns:
            MIMEMultipart: Mensagem de email pronta para envio
        """
        # Cria mensagem
        msg = MIMEMultipart()
        msg['From'] = self.smtp_email
        msg['To'] = to_email
        msg['Subject'] = subject
        
        # Adiciona corpo do email
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
                    except (FileNotFoundError, PermissionError, OSError) as e:
                        # Log erro mas continua com outros anexos
                        pass
                    except Exception as e:
                        # Log erro genérico
                        pass
        
        return msg
    
    def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        attachments: Optional[List[str]] = None,
        retry_count: int = 3
    ) -> Tuple[bool, str]:
        """
        Envia um email.
        
        Args:
            to_email: Email do destinatário
            subject: Assunto do email
            body: Corpo do email
            attachments: Lista de caminhos para anexos
            retry_count: Número de tentativas em caso de erro
        
        Returns:
            tuple: (success, message) - True se enviado com sucesso, mensagem de erro se falhou
        """
        if not self.is_connected:
            if not self.connect():
                return False, "Não foi possível conectar ao servidor SMTP"
        
        # Cria mensagem
        msg = self.create_message(to_email, subject, body, attachments)
        
        # Tenta enviar com retry
        for attempt in range(retry_count):
            try:
                # Envia email
                self.server.send_message(msg)
                
                # Extrai headers da mensagem
                headers = {}
                for key, value in msg.items():
                    headers[key] = value
                
                # Gera Message-ID se não existir
                message_id = headers.get('Message-ID')
                if not message_id:
                    import uuid
                    message_id = f"<{uuid.uuid4()}@amatools.com.br>"
                    headers['Message-ID'] = message_id
                
                return True, {
                    'message': "Email enviado com sucesso",
                    'gmail_message_id': None,
                    'gmail_thread_id': None,
                    'message_id': message_id,
                    'headers': headers
                }
                
            except smtplib.SMTPRecipientsRefused as e:
                return False, f"Destinatário recusado: {e}"
            except smtplib.SMTPDataError as e:
                return False, f"Erro de dados SMTP: {e}"
            except smtplib.SMTPException as e:
                if attempt < retry_count - 1:
                    time.sleep(2)  # Espera antes de tentar novamente
                    continue
                return False, f"Erro SMTP: {e}"
            except Exception as e:
                return False, f"Erro inesperado: {e}"
        
        return False, "Falha após múltiplas tentativas"
    
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

