"""
Interfaces (Protocols) para componentes principais.
"""
from typing import Protocol, Callable, List, Optional, Dict, Any


class TemplateRenderer(Protocol):
    last_error: Optional[str]

    def load(self) -> bool: ...
    def process(self, data: Dict[str, Any]) -> str: ...


class RecipientReader(Protocol):
    last_error: Optional[str]

    def read(self) -> bool: ...
    def get_recipients(self) -> List[Dict[str, Any]]: ...


class BatchSender(Protocol):
    def send_batch(
        self,
        recipients: List[Dict[str, Any]],
        subject: str,
        get_body: Callable[[Dict[str, Any]], str],
        attachments: Optional[List[str]] = None,
        progress_callback: Optional[Callable[[int, int, Dict[str, Any]], None]] = None,
        stop_flag: Optional[Callable[[], bool]] = None
    ) -> Dict[str, Any]: ...
