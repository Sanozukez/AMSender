"""
Controlador de envio em lote, separando lógica de orquestração da UI.
"""
from datetime import datetime
from typing import Callable, Dict, List, Optional

from src.comprovacao import Comprovacao
from src.interfaces import BatchSender, TemplateRenderer
from src.logger import get_logger


class BatchController:
    def __init__(
        self,
        log_fn: Callable[[str], None],
        stats_fn: Callable[[int, int, int], None],
    ):
        self._log = log_fn
        self._stats = stats_fn
        self._logger = get_logger()

    def run(
        self,
        *,
        recipients: List[dict],
        subject: str,
        attachments: Optional[List[str]],
        template_processor: TemplateRenderer,
        comprovacao: Comprovacao,
        sender: BatchSender,
        use_oauth: bool,
        from_email: str,
        stop_flag: Callable[[], bool],
    ) -> Dict[str, int]:
        """Executa o envio em lote e registra evidências."""
        total_recipients = len(recipients)
        enviados = 0
        erros = 0

        # Conexão/validação do sender
        if use_oauth:
            # GmailSender já validado no fluxo da UI
            if not getattr(sender, "is_authenticated", lambda: False)():
                self._log("ERRO: Não autenticado no Google.")
                return {"total": total_recipients, "enviados": 0, "erros": total_recipients, "detalhes": []}
            self._log("Usando Gmail API (OAuth) para envio.")
        else:
            connect = getattr(sender, "connect", None)
            if connect and not connect():
                self._log("ERRO: Não foi possível conectar ao servidor SMTP.")
                return {"total": total_recipients, "enviados": 0, "erros": total_recipients, "detalhes": []}
            self._log("Conectado ao servidor SMTP com sucesso.")

        def get_body(recipient_data: dict) -> str:
            return template_processor.process(recipient_data)

        def progress_callback(current: int, total: int, recipient: dict):
            email = recipient.get("email", "N/A")
            self._log(f"[{current}/{total}] Enviando para {email}...")

        stats = sender.send_batch(
            recipients=recipients,
            subject=subject,
            get_body=get_body,
            attachments=attachments,
            progress_callback=progress_callback,
            stop_flag=stop_flag,
        )

        total = len(stats.get("detalhes", [])) or total_recipients

        for detail in stats.get("detalhes", []):
            email = detail.get("email")
            status = detail.get("status")
            message = detail.get("mensagem")

            if status == "enviado":
                recipient_data = next((r for r in recipients if r.get("email") == email), {})
                body = get_body(recipient_data)
                message_id = detail.get("message_id")
                headers = detail.get("headers", {})

                eml_path = comprovacao.save_eml(
                    to_email=email,
                    subject=subject,
                    body=body,
                    from_email=from_email,
                    attachments=attachments,
                    message_id=message_id,
                    headers=headers,
                )

                comprovacao.register_email(
                    to_email=email,
                    subject=subject,
                    attachments_count=len(attachments) if attachments else 0,
                    status="enviado",
                    message=message,
                    eml_path=eml_path,
                    gmail_message_id=detail.get("gmail_message_id"),
                    gmail_thread_id=detail.get("gmail_thread_id"),
                    message_id=message_id,
                    headers=headers,
                    timestamp_envio=datetime.now(),
                    attachments_hashes=detail.get("attachments_hashes"),
                    raw_message=detail.get("raw"),
                    history_id=detail.get("history_id"),
                )
                enviados += 1
            else:
                comprovacao.register_email(
                    to_email=email,
                    subject=subject,
                    status="erro",
                    message=message,
                    eml_path=None,
                    attachments_count=len(attachments) if attachments else 0,
                    attachments_hashes=detail.get("attachments_hashes"),
                    raw_message=detail.get("raw"),
                    history_id=detail.get("history_id"),
                )
                erros += 1

            self._stats(total, enviados, erros)

        comprovacao.finalize()
        self._stats(stats.get("total", total), stats.get("enviados", enviados), stats.get("erros", erros))

        if not use_oauth:
            disconnect = getattr(sender, "disconnect", None)
            if disconnect:
                try:
                    disconnect()
                except Exception:
                    self._logger.debug("Erro ao desconectar SMTP (ignorado)")

        return stats
