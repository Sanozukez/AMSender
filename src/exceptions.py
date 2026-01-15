# src/exceptions.py
"""
Exceções customizadas do sistema Mail Sender.
"""

class MailSenderException(Exception):
    """Exceção base do sistema Mail Sender."""
    pass

class ConfigurationError(MailSenderException):
    """Erro de configuração."""
    pass

class ExcelReadError(MailSenderException):
    """Erro ao ler arquivo Excel."""
    pass

class TemplateError(MailSenderException):
    """Erro ao processar template."""
    pass

class EmailSendError(MailSenderException):
    """Erro ao enviar email."""
    pass

class OAuthError(MailSenderException):
    """Erro na autenticação OAuth."""
    pass

class ComprovacaoError(MailSenderException):
    """Erro ao gerar comprovação."""
    pass

