# main.py
"""
Aplicação principal Mail Sender.
Email Relay com interface gráfica.
"""

import sys
import warnings
from pathlib import Path

# Suprime warnings do Python sobre versão (não são críticos para funcionamento)
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", message=".*Python version.*")
warnings.filterwarnings("ignore", message=".*google.api_core.*")

# Adiciona diretório src ao path
sys.path.insert(0, str(Path(__file__).parent))

from src.ui.main_window import MainWindow

def main():
    """
    Função principal da aplicação.
    """
    try:
        app = MainWindow()
        app.run()
    except Exception as e:
        print(f"Erro ao iniciar aplicação: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

