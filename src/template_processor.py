# src/template_processor.py
"""
Módulo para processamento de templates de email.
Suporta arquivos DOCX e TXT com placeholders.
"""

import re
from pathlib import Path
from typing import Dict, Optional

# Importação lazy do docx para evitar erros se não estiver disponível
try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False
    Document = None

class TemplateProcessor:
    """
    Classe para processar templates de email com placeholders.
    """
    
    def __init__(self, template_path: str):
        """
        Inicializa o processador de template.
        
        Args:
            template_path: Caminho para o arquivo template (DOCX ou TXT)
        """
        self.template_path = Path(template_path)
        self.template_content: Optional[str] = None
        self.template_type: Optional[str] = None
        
    def load(self) -> bool:
        """
        Carrega o conteúdo do template.
        
        Returns:
            bool: True se carregamento foi bem-sucedido, False caso contrário
        """
        try:
            if not self.template_path.exists():
                return False
            
            extension = self.template_path.suffix.lower()
            
            if extension == '.docx':
                # Verifica se docx está disponível
                if not DOCX_AVAILABLE:
                    import sys
                    print("Erro: python-docx não está disponível. Não é possível processar arquivos .docx", file=sys.stderr)
                    return False
                # Lê arquivo DOCX
                doc = Document(self.template_path)
                # Concatena todos os parágrafos
                paragraphs = [para.text for para in doc.paragraphs]
                self.template_content = '\n'.join(paragraphs)
                self.template_type = 'docx'
                
            elif extension == '.txt':
                # Lê arquivo TXT
                with open(self.template_path, 'r', encoding='utf-8') as f:
                    self.template_content = f.read()
                self.template_type = 'txt'
            else:
                return False
            
            return True
            
        except FileNotFoundError:
            return False
        except PermissionError:
            return False
        except Exception as e:
            # Log do erro sem expor detalhes sensíveis
            import sys
            print(f"Erro ao carregar template: {type(e).__name__}", file=sys.stderr)
            return False
    
    def process(self, data: Dict[str, str]) -> str:
        """
        Processa o template substituindo placeholders pelos valores.
        
        Args:
            data: Dicionário com valores para substituição (ex: {'nome': 'João', 'email': 'joao@exemplo.com'})
        
        Returns:
            str: Template processado com valores substituídos
        """
        if self.template_content is None:
            return ""
        
        result = self.template_content
        
        # Substitui placeholders no formato {{chave}}
        # Busca todos os placeholders no template
        placeholders = re.findall(r'\{\{(\w+)\}\}', result)
        
        for placeholder in placeholders:
            key = placeholder.lower()
            value = data.get(key, '')
            # Substitui todas as ocorrências do placeholder
            result = result.replace(f'{{{{{placeholder}}}}}', str(value))
            result = result.replace(f'{{{{{placeholder.upper()}}}}}', str(value))
            result = result.replace(f'{{{{{placeholder.capitalize()}}}}}', str(value))
        
        return result
    
    def get_preview(self, sample_data: Optional[Dict[str, str]] = None) -> str:
        """
        Retorna preview do template com dados de exemplo.
        
        Args:
            sample_data: Dados de exemplo (se None, usa dados padrão)
        
        Returns:
            str: Preview do template processado
        """
        if sample_data is None:
            sample_data = {
                'nome': 'Nome do Destinatário',
                'email': 'email@exemplo.com'
            }
        
        return self.process(sample_data)

