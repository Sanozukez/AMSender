# src/comprovacao.py
"""
Módulo para geração de comprovações de envio de emails.
Gera logs detalhados, arquivos .eml e estrutura completa de evidências.
"""

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from email.utils import formatdate
import uuid

from src.config import APP_DATA_DIR

class Comprovacao:
    """
    Classe para gerenciar comprovações de envio de emails.
    """
    
    def __init__(
        self,
        campanha_name: Optional[str] = None,
        template_path: Optional[str] = None,
        attachments: Optional[List[str]] = None,
        excel_emails: Optional[List[str]] = None
    ):
        """
        Inicializa o sistema de comprovação.
        
        Args:
            campanha_name: Nome da campanha (opcional)
            template_path: Caminho do template usado
            attachments: Lista de caminhos dos anexos
            excel_emails: Lista de emails do Excel (resumo)
        """
        self.timestamp = datetime.now()
        self.campanha_name = campanha_name or f"campanha_{self.timestamp.strftime('%Y%m%d_%H%M%S')}"
        
        # Sanitiza nome da campanha para usar como nome de pasta
        # Remove caracteres especiais, converte para minúsculas e substitui espaços por hífens
        safe_campanha_name = "".join(c for c in self.campanha_name if c.isalnum() or c in (' ', '-', '_')).strip()
        safe_campanha_name = safe_campanha_name.lower()
        safe_campanha_name = safe_campanha_name.replace(' ', '-').replace('_', '-')
        # Remove múltiplos hífens consecutivos
        while '--' in safe_campanha_name:
            safe_campanha_name = safe_campanha_name.replace('--', '-')
        # Remove hífens no início e fim
        safe_campanha_name = safe_campanha_name.strip('-')
        
        if not safe_campanha_name:
            safe_campanha_name = "campanha"
        
        # Formato do timestamp: DDMMYY-HHMM (ex: 150126-1558 para 15/01/2026 15:58)
        timestamp_str = self.timestamp.strftime('%d%m%y-%H%M')
        
        # Nome final da pasta: nome-campanha-timestamp
        folder_name = f"{safe_campanha_name}-{timestamp_str}"
        
        # Cria diretório da campanha diretamente em APP_DATA_DIR (Documentos/AmatoolsMailSender/)
        self.campanha_dir = APP_DATA_DIR / folder_name
        self.campanha_dir.mkdir(parents=True, exist_ok=True)
        
        # Arquivo de log detalhado
        self.log_file = self.campanha_dir / f"log_{self.timestamp.strftime('%Y%m%d_%H%M%S')}.txt"
        
        # Copia arquivos da campanha
        self._copy_campaign_files(template_path, attachments)
        
        # Salva resumo do Excel
        if excel_emails:
            self._save_excel_summary(excel_emails)
        
        # Dados do resumo JSON
        self.resumo = {
            'campanha': self.campanha_name,
            'timestamp_inicio': self.timestamp.isoformat(),
            'timestamp_fim': None,
            'total': 0,
            'enviados': 0,
            'erros': 0,
            'metodo_envio': None,
            'remetente': None,
            'assunto': None,
            'emails': []
        }
        
        # Inicia log
        self.log("="*80)
        self.log(f"CAMPANHA: {self.campanha_name}")
        self.log(f"INÍCIO: {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        self.log("="*80)
    
    def _copy_campaign_files(
        self,
        template_path: Optional[str],
        attachments: Optional[List[str]]
    ):
        """
        Copia arquivos da campanha para a pasta de logs.
        
        Args:
            template_path: Caminho do template
            attachments: Lista de caminhos dos anexos
        """
        try:
            # Copia template
            if template_path:
                template_src = Path(template_path)
                if template_src.exists():
                    template_dst = self.campanha_dir / f"template{template_src.suffix}"
                    shutil.copy2(template_src, template_dst)
                    self.log(f"Template copiado: {template_dst.name}")
            
            # Copia anexos
            if attachments:
                anexos_dir = self.campanha_dir / "anexos"
                anexos_dir.mkdir(exist_ok=True)
                
                for attachment_path in attachments:
                    try:
                        att_src = Path(attachment_path)
                        if att_src.exists():
                            att_dst = anexos_dir / att_src.name
                            shutil.copy2(att_src, att_dst)
                            self.log(f"Anexo copiado: {att_dst.name}")
                    except (FileNotFoundError, PermissionError, OSError) as e:
                        self.log(f"Erro ao copiar anexo {attachment_path}: {type(e).__name__}", 'WARNING')
                    except Exception as e:
                        self.log(f"Erro inesperado ao copiar anexo {attachment_path}: {type(e).__name__}", 'WARNING')
        except (FileNotFoundError, PermissionError, OSError) as e:
            self.log(f"Erro ao copiar arquivos da campanha: {type(e).__name__}", 'ERROR')
        except Exception as e:
            self.log(f"Erro inesperado ao copiar arquivos: {type(e).__name__}", 'ERROR')
    
    def _save_excel_summary(self, emails: List[str]):
        """
        Salva resumo do Excel (apenas lista de emails).
        
        Args:
            emails: Lista de emails dos destinatários
        """
        try:
            summary_file = self.campanha_dir / "destinatarios.txt"
            with open(summary_file, 'w', encoding='utf-8') as f:
                f.write("LISTA DE DESTINATÁRIOS\n")
                f.write("="*80 + "\n")
                f.write(f"Total: {len(emails)}\n\n")
                for idx, email in enumerate(emails, 1):
                    f.write(f"{idx:4d}. {email}\n")
            self.log(f"Resumo de destinatários salvo: {len(emails)} emails")
        except (IOError, OSError, PermissionError) as e:
            self.log(f"Erro ao salvar resumo do Excel: {type(e).__name__}", 'ERROR')
        except Exception as e:
            self.log(f"Erro inesperado ao salvar resumo: {type(e).__name__}", 'ERROR')
    
    def log(self, message: str, level: str = 'INFO'):
        """
        Registra mensagem no log.
        
        Args:
            message: Mensagem a ser registrada
            level: Nível do log (INFO, ERROR, WARNING)
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] [{level}] {message}\n"
        
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry)
        except (IOError, OSError, PermissionError) as e:
            # Fallback: tenta escrever no stderr se não conseguir no arquivo
            import sys
            print(f"[LOG ERROR] {log_entry.strip()}", file=sys.stderr)
        except Exception as e:
            import sys
            print(f"[LOG ERROR] {log_entry.strip()}", file=sys.stderr)
    
    def save_eml(
        self,
        to_email: str,
        subject: str,
        body: str,
        from_email: str,
        attachments: Optional[List[str]] = None,
        message_id: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Optional[Path]:
        """
        Salva email como arquivo .eml com headers completos.
        
        Args:
            to_email: Email do destinatário
            subject: Assunto do email
            body: Corpo do email
            from_email: Email do remetente
            attachments: Lista de caminhos para anexos
            message_id: Message-ID do email (se disponível)
            headers: Headers adicionais do email
        
        Returns:
            Path: Caminho do arquivo .eml salvo, ou None se houve erro
        """
        try:
            # Cria mensagem
            msg = MIMEMultipart()
            msg['From'] = from_email
            msg['To'] = to_email
            msg['Subject'] = subject
            msg['Date'] = formatdate(localtime=True)
            
            # Adiciona Message-ID se fornecido, senão gera um
            if message_id:
                msg['Message-ID'] = message_id
            else:
                msg['Message-ID'] = f"<{uuid.uuid4()}@amatools.com.br>"
            
            # Adiciona headers customizados
            if headers:
                for key, value in headers.items():
                    if key not in ['From', 'To', 'Subject', 'Date', 'Message-ID']:
                        msg[key] = value
            
            # Adiciona corpo
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            # Adiciona anexos
            if attachments:
                for attachment_path in attachments:
                    try:
                        path = Path(attachment_path)
                        if path.exists():
                            with open(path, 'rb') as f:
                                part = MIMEBase('application', 'octet-stream')
                                part.set_payload(f.read())
                            
                            encoders.encode_base64(part)
                            part.add_header(
                                'Content-Disposition',
                                f'attachment; filename= {path.name}'
                            )
                            msg.attach(part)
                    except Exception as e:
                        self.log(f"Erro ao anexar arquivo {attachment_path} no .eml: {e}", 'WARNING')
            
            # Salva arquivo .eml
            safe_email = to_email.replace('@', '_at_').replace('.', '_')
            eml_filename = f"{safe_email}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.eml"
            eml_path = self.campanha_dir / eml_filename
            
            with open(eml_path, 'wb') as f:
                f.write(msg.as_bytes())
            
            return eml_path
            
        except (IOError, OSError, PermissionError) as e:
            self.log(f"Erro ao salvar .eml para {to_email}: {type(e).__name__}", 'ERROR')
            return None
        except Exception as e:
            self.log(f"Erro inesperado ao salvar .eml: {type(e).__name__}", 'ERROR')
            return None
    
    def register_email(
        self,
        to_email: str,
        subject: str,
        status: str,
        message: str,
        eml_path: Optional[Path] = None,
        gmail_message_id: Optional[str] = None,
        gmail_thread_id: Optional[str] = None,
        message_id: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        timestamp_envio: Optional[datetime] = None,
        attachments_count: Optional[int] = None,
        message_size: Optional[int] = None
    ):
        """
        Registra envio de email no resumo com todas as evidências.
        
        Args:
            to_email: Email do destinatário
            subject: Assunto do email
            status: Status do envio ('enviado' ou 'erro')
            message: Mensagem de status ou erro
            eml_path: Caminho do arquivo .eml (se salvo)
            gmail_message_id: ID da mensagem do Gmail (se OAuth)
            gmail_thread_id: ID do thread do Gmail (se OAuth)
            message_id: Message-ID do email
            headers: Headers do email
            timestamp_envio: Timestamp do envio
            attachments_count: Número de anexos
            message_size: Tamanho da mensagem em bytes
        """
        if timestamp_envio is None:
            timestamp_envio = datetime.now()
        
        # Calcula tamanho do .eml se disponível
        eml_size = None
        if eml_path and eml_path.exists():
            try:
                eml_size = eml_path.stat().st_size
            except (OSError, PermissionError):
                pass
        
        email_data = {
            'email': to_email,
            'subject': subject,
            'status': status,
            'timestamp': timestamp_envio.isoformat(),
            'mensagem': message,
            'eml_path': str(eml_path) if eml_path else None,
            'eml_size_bytes': eml_size,
            'gmail_message_id': gmail_message_id,
            'gmail_thread_id': gmail_thread_id,
            'message_id': message_id,
            'headers': headers or {},
            'attachments_count': attachments_count,
            'message_size_bytes': message_size or eml_size
        }
        
        self.resumo['emails'].append(email_data)
        
        # Log detalhado
        if status == 'enviado':
            self.resumo['enviados'] += 1
            self.log(f"✓ Email enviado: {to_email}")
            if gmail_message_id:
                self.log(f"  Gmail Message ID: {gmail_message_id}")
            if gmail_thread_id:
                self.log(f"  Gmail Thread ID: {gmail_thread_id}")
            if message_id:
                self.log(f"  Message-ID: {message_id}")
            if headers:
                for key, value in headers.items():
                    self.log(f"  {key}: {value}")
        else:
            self.resumo['erros'] += 1
            self.log(f"✗ Erro ao enviar: {to_email} - {message}", 'ERROR')
    
    def set_campaign_info(self, metodo_envio: str, remetente: str, assunto: str):
        """
        Define informações gerais da campanha.
        
        Args:
            metodo_envio: Método usado (SMTP ou OAuth)
            remetente: Email do remetente
            assunto: Assunto do email
        """
        self.resumo['metodo_envio'] = metodo_envio
        self.resumo['remetente'] = remetente
        self.resumo['assunto'] = assunto
        
        self.log(f"Método de envio: {metodo_envio}")
        self.log(f"Remetente: {remetente}")
        self.log(f"Assunto: {assunto}")
    
    def finalize(self):
        """
        Finaliza a comprovação, salvando resumo JSON e informações finais.
        """
        self.resumo['timestamp_fim'] = datetime.now().isoformat()
        self.resumo['total'] = len(self.resumo['emails'])
        
        # Salva resumo JSON
        resumo_path = self.campanha_dir / 'resumo.json'
        try:
            with open(resumo_path, 'w', encoding='utf-8') as f:
                json.dump(self.resumo, f, indent=2, ensure_ascii=False)
            
            self.log("="*80)
            self.log(f"FIM: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            self.log(f"Total: {self.resumo['total']}")
            self.log(f"Enviados: {self.resumo['enviados']}")
            self.log(f"Erros: {self.resumo['erros']}")
            self.log(f"Diretório: {self.campanha_dir}")
            self.log("="*80)
            
        except Exception as e:
            self.log(f"Erro ao salvar resumo: {e}", 'ERROR')
    
    def get_resumo(self) -> Dict:
        """
        Retorna resumo atual.
        
        Returns:
            Dict: Resumo da comprovação
        """
        return self.resumo.copy()
    
    def get_campanha_dir(self) -> Path:
        """
        Retorna o diretório da campanha.
        
        Returns:
            Path: Diretório da campanha
        """
        return self.campanha_dir
