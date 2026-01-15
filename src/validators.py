# src/validators.py
"""
Módulo de validações do sistema.
Valida dados de entrada e configurações.
"""

import re
from typing import Tuple, Optional
from pathlib import Path

class Validators:
    """
    Classe com métodos estáticos para validações.
    """
    
    @staticmethod
    def validate_email(email: str) -> Tuple[bool, Optional[str]]:
        """
        Valida formato de email.
        
        Args:
            email: Email a ser validado
        
        Returns:
            tuple: (is_valid, error_message)
        """
        if not email or not email.strip():
            return False, "Email não pode estar vazio"
        
        email = email.strip()
        
        # Regex básico para validação de email
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            return False, "Formato de email inválido"
        
        return True, None
    
    @staticmethod
    def validate_file_path(file_path: str, must_exist: bool = True) -> Tuple[bool, Optional[str]]:
        """
        Valida caminho de arquivo.
        
        Args:
            file_path: Caminho do arquivo
            must_exist: Se True, arquivo deve existir
        
        Returns:
            tuple: (is_valid, error_message)
        """
        if not file_path or not file_path.strip():
            return False, "Caminho do arquivo não pode estar vazio"
        
        path = Path(file_path)
        
        if must_exist and not path.exists():
            return False, f"Arquivo não encontrado: {file_path}"
        
        if must_exist and not path.is_file():
            return False, f"Caminho não é um arquivo: {file_path}"
        
        return True, None
    
    @staticmethod
    def validate_port(port: str) -> Tuple[bool, Optional[str]]:
        """
        Valida porta SMTP.
        
        Args:
            port: Porta a ser validada
        
        Returns:
            tuple: (is_valid, error_message)
        """
        if not port or not port.strip():
            return False, "Porta não pode estar vazia"
        
        try:
            port_num = int(port.strip())
            if port_num < 1 or port_num > 65535:
                return False, "Porta deve estar entre 1 e 65535"
            return True, None
        except ValueError:
            return False, "Porta deve ser um número"
    
    @staticmethod
    def validate_delay(delay: str) -> Tuple[bool, Optional[str]]:
        """
        Valida delay entre envios.
        
        Args:
            delay: Delay a ser validado
        
        Returns:
            tuple: (is_valid, error_message)
        """
        if not delay or not delay.strip():
            return False, "Delay não pode estar vazio"
        
        try:
            delay_num = float(delay.strip())
            if delay_num < 0:
                return False, "Delay não pode ser negativo"
            if delay_num > 60:
                return False, "Delay não pode ser maior que 60 segundos"
            return True, None
        except ValueError:
            return False, "Delay deve ser um número"
    
    @staticmethod
    def validate_campanha_name(name: str) -> Tuple[bool, Optional[str]]:
        """
        Valida nome da campanha.
        
        Args:
            name: Nome da campanha
        
        Returns:
            tuple: (is_valid, error_message)
        """
        if not name or not name.strip():
            return True, None  # Nome opcional
        
        name = name.strip()
        
        # Valida caracteres permitidos para nome de pasta
        invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
        for char in invalid_chars:
            if char in name:
                return False, f"Nome da campanha não pode conter o caractere: {char}"
        
        if len(name) > 100:
            return False, "Nome da campanha muito longo (máximo 100 caracteres)"
        
        return True, None

