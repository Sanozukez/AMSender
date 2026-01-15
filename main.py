# main.py
"""
Aplicação principal Mail Sender.
Email Relay com interface gráfica.
"""

import sys
import warnings
import traceback
from pathlib import Path

# Suprime warnings do Python sobre versão (não são críticos para funcionamento)
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", message=".*Python version.*")
warnings.filterwarnings("ignore", message=".*google.api_core.*")

# Adiciona diretório src ao path
sys.path.insert(0, str(Path(__file__).parent))

def check_dependencies():
    """
    Verifica se todas as dependências necessárias estão instaladas.
    
    Returns:
        tuple: (bool, str) - (sucesso, mensagem de erro)
    """
    import sys
    
    # Se estiver executando como executável PyInstaller, pula a verificação
    # O PyInstaller já inclui todas as dependências no executável
    # Se algum módulo realmente faltar, o erro aparecerá naturalmente ao tentar usá-lo
    if getattr(sys, 'frozen', False):
        return True, ""
    
    # Em ambiente de desenvolvimento, verifica todas as dependências
    missing_modules = []
    
    required_modules = [
        ('lxml', 'lxml'),
        ('docx', 'python-docx'),
        ('pandas', 'pandas'),
        ('openpyxl', 'openpyxl'),
        ('ttkbootstrap', 'ttkbootstrap'),
        ('PIL', 'Pillow'),
        ('google.auth', 'google-auth'),
        ('googleapiclient', 'google-api-python-client'),
        ('dotenv', 'python-dotenv'),
    ]
    
    for module_name, package_name in required_modules:
        try:
            __import__(module_name)
        except ImportError:
            missing_modules.append(package_name)
    
    if missing_modules:
        return False, f"Módulos faltando: {', '.join(missing_modules)}\n\nPor favor, instale com: pip install {' '.join(missing_modules)}"
    
    return True, ""

def show_error_dialog(title, message):
    """
    Exibe uma mensagem de erro. Tenta usar tkinter, senão usa print.
    """
    try:
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()  # Esconde a janela principal
        messagebox.showerror(title, message)
        root.destroy()
    except:
        # Se não conseguir usar tkinter, apenas imprime
        print(f"\n{'='*60}")
        print(f"ERRO: {title}")
        print(f"{'='*60}")
        print(message)
        print(f"{'='*60}\n")

def main():
    """
    Função principal da aplicação.
    """
    try:
        # Verifica dependências antes de iniciar
        deps_ok, deps_message = check_dependencies()
        if not deps_ok:
            show_error_dialog(
                "Dependências Faltando",
                f"O aplicativo não pode iniciar porque faltam módulos necessários.\n\n{deps_message}\n\n"
                "Se você instalou a partir do instalador, por favor reporte este erro."
            )
            sys.exit(1)
        
        from src.ui.main_window import MainWindow
        app = MainWindow()
        app.run()
        
    except ModuleNotFoundError as e:
        error_msg = (
            f"Módulo não encontrado: {e.name}\n\n"
            f"Erro completo:\n{str(e)}\n\n"
            "Isso geralmente indica que o executável foi criado sem incluir todas as dependências.\n"
            "Por favor, reporte este erro ao desenvolvedor."
        )
        show_error_dialog("Erro de Módulo", error_msg)
        sys.exit(1)
        
    except Exception as e:
        error_msg = (
            f"Erro inesperado ao iniciar aplicação:\n\n"
            f"{type(e).__name__}: {str(e)}\n\n"
            f"Traceback completo:\n{''.join(traceback.format_exc())}"
        )
        show_error_dialog("Erro ao Iniciar", error_msg)
        sys.exit(1)

if __name__ == "__main__":
    main()

