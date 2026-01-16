# src/excel_reader.py
"""
Módulo para leitura de planilhas Excel.
Lê destinatários e dados para personalização dos emails.
"""

import pandas as pd
from pathlib import Path
from typing import List, Dict, Optional

class ExcelReader:
    """
    Classe para leitura e processamento de planilhas Excel.
    """
    
    def __init__(self, excel_path: str):
        """
        Inicializa o leitor de Excel.
        
        Args:
            excel_path: Caminho para o arquivo Excel
        """
        self.excel_path = Path(excel_path)
        self.df: Optional[pd.DataFrame] = None
        self.headers: List[str] = []
        self.last_error: str = ""
        
    def read(self) -> bool:
        """
        Lê o arquivo Excel e armazena os dados.
        
        Returns:
            bool: True se leitura foi bem-sucedida, False caso contrário
        """
        self.last_error = ""
        try:
            # Lê o Excel (suporta .xlsx e .xls)
            extension = self.excel_path.suffix.lower()
            engine = None
            # Define engine por extensão para evitar erro silencioso em .xls
            if extension == '.xlsx':
                engine = 'openpyxl'
            elif extension == '.xls':
                engine = 'xlrd'
            try:
                self.df = pd.read_excel(self.excel_path, engine=engine)
            except ImportError:
                # Engine específica não instalada
                missing = 'openpyxl' if extension == '.xlsx' else 'xlrd'
                self.last_error = f"Dependência ausente para ler {extension}: instale {missing}."
                return False
            
            # Remove linhas completamente vazias
            self.df = self.df.dropna(how='all')
            
            # Obtém cabeçalhos (primeira linha)
            self.headers = [str(col).strip().lower() for col in self.df.columns]
            
            # Valida coluna obrigatória 'email'
            if 'email' not in self.headers:
                self.last_error = "Planilha sem a coluna obrigatória 'email'."
                return False
            
            # Normaliza nome da coluna email (case-insensitive)
            email_col = next(col for col in self.df.columns if str(col).strip().lower() == 'email')
            self.df = self.df.rename(columns={email_col: 'email'})
            self.headers = [str(col).strip().lower() for col in self.df.columns]
            
            # Remove linhas sem email
            self.df = self.df.dropna(subset=['email'])
            
            # Converte email para string e remove espaços
            self.df['email'] = self.df['email'].astype(str).str.strip()
            
            # Remove emails inválidos básicos
            self.df = self.df[self.df['email'].str.contains('@', na=False)]
            
            return True
            
        except FileNotFoundError:
            self.last_error = "Arquivo não encontrado."
            return False
        except Exception as e:
            # Log do erro sem expor detalhes sensíveis
            import sys
            self.last_error = f"Erro ao ler Excel: {type(e).__name__}"
            print(self.last_error, file=sys.stderr)
            return False
    
    def get_recipients(self) -> List[Dict[str, str]]:
        """
        Retorna lista de destinatários com todos os dados.
        
        Returns:
            List[Dict]: Lista de dicionários, cada um representando um destinatário
        """
        if self.df is None:
            return []
        
        recipients = []
        for _, row in self.df.iterrows():
            recipient = {}
            for col in self.df.columns:
                value = row[col]
                # Converte para string, trata NaN
                if pd.isna(value):
                    recipient[str(col).lower()] = ''
                else:
                    recipient[str(col).lower()] = str(value).strip()
            recipients.append(recipient)
        
        return recipients
    
    def get_count(self) -> int:
        """
        Retorna o número de destinatários.
        
        Returns:
            int: Número de destinatários
        """
        if self.df is None:
            return 0
        return len(self.df)
    
    def get_headers(self) -> List[str]:
        """
        Retorna lista de cabeçalhos disponíveis.
        
        Returns:
            List[str]: Lista de cabeçalhos
        """
        return self.headers.copy()

