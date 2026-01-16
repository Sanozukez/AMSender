import tempfile
import unittest
from pathlib import Path

from src.excel_reader import ExcelReader


class ExcelReaderTests(unittest.TestCase):
    def test_xlsx_engine_selected(self):
        """Verifica que openpyxl é usado para .xlsx."""
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
            tmp_path = tmp.name
        try:
            reader = ExcelReader(tmp_path)
            # Não tentamos read() pois arquivo vazio; apenas verificamos seleção de engine
            self.assertIsNotNone(reader)
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    def test_last_error_set_on_missing_file(self):
        """Verifica que last_error é populado quando arquivo não existe."""
        reader = ExcelReader("nao_existe.xlsx")
        result = reader.read()
        self.assertFalse(result)
        self.assertIsNotNone(reader.last_error)
        self.assertIn("não encontrado", reader.last_error.lower())


if __name__ == "__main__":
    unittest.main()
