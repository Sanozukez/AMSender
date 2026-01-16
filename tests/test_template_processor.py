import tempfile
import unittest
from pathlib import Path

from src.template_processor import TemplateProcessor


class TemplateProcessorTests(unittest.TestCase):
    def test_valid_placeholder_replacement(self):
        with tempfile.TemporaryDirectory() as tmp:
            template_path = Path(tmp) / "tpl.txt"
            template_path.write_text("Olá {{nome}}", encoding="utf-8")
            tp = TemplateProcessor(str(template_path))
            self.assertTrue(tp.load())
            result = tp.process({"nome": "João"})
            self.assertIn("João", result)

    def test_invalid_placeholder_is_cleaned(self):
        with tempfile.TemporaryDirectory() as tmp:
            template_path = Path(tmp) / "tpl.txt"
            template_path.write_text("Olá {{nome completo}}", encoding="utf-8")
            tp = TemplateProcessor(str(template_path))
            self.assertTrue(tp.load())
            result = tp.process({"nome completo": "João"})
            self.assertNotIn("João", result)
            self.assertIn("Olá", result)


if __name__ == "__main__":
    unittest.main()
