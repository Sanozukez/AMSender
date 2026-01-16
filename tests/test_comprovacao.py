import tempfile
import unittest
from pathlib import Path

from src.comprovacao import Comprovacao


class ComprovacaoTests(unittest.TestCase):
    def test_save_eml_creates_file(self):
        """Verifica que save_eml cria .eml."""
        with tempfile.TemporaryDirectory() as tmpdir:
            comp = Comprovacao(campanha_name="test")
            eml_path = comp.save_eml(
                to_email="test@example.com",
                subject="Test",
                body="Body",
                from_email="from@example.com",
            )
            self.assertIsNotNone(eml_path)
            self.assertTrue(eml_path.exists())
            self.assertTrue(eml_path.suffix == ".eml")

    def test_register_email_in_resumo(self):
        """Verifica que register_email adiciona ao resumo."""
        with tempfile.TemporaryDirectory() as tmpdir:
            comp = Comprovacao(campanha_name="test")
            comp.register_email(
                to_email="test@example.com",
                subject="Test",
                status="enviado",
                message="OK",
            )
            resumo = comp.get_resumo()
            self.assertEqual(len(resumo["emails"]), 1)
            self.assertEqual(resumo["emails"][0]["email"], "test@example.com")
            self.assertEqual(resumo["emails"][0]["status"], "enviado")


if __name__ == "__main__":
    unittest.main()
