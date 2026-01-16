import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock

from src.batch_controller import BatchController
from src.comprovacao import Comprovacao


class BatchControllerTests(unittest.TestCase):
    def test_run_with_mock_sender(self):
        """Teste de integração leve com sender mockado."""
        log_messages = []
        stats_calls = []

        def log_fn(msg):
            log_messages.append(msg)

        def stats_fn(total, enviados, erros):
            stats_calls.append((total, enviados, erros))

        controller = BatchController(log_fn=log_fn, stats_fn=stats_fn)

        # Mock sender
        mock_sender = MagicMock()
        mock_sender.send_batch.return_value = {
            "total": 1,
            "enviados": 1,
            "erros": 0,
            "detalhes": [
                {
                    "email": "test@example.com",
                    "status": "enviado",
                    "mensagem": "OK",
                    "message_id": "<test@mail>",
                    "headers": {},
                }
            ],
        }

        # Mock template
        mock_template = MagicMock()
        mock_template.process.return_value = "Corpo do email"

        # Comprovação temporária
        with tempfile.TemporaryDirectory() as tmpdir:
            comprovacao = Comprovacao(campanha_name="test")
            recipients = [{"email": "test@example.com", "nome": "Test"}]
            stats = controller.run(
                recipients=recipients,
                subject="Test",
                attachments=None,
                template_processor=mock_template,
                comprovacao=comprovacao,
                sender=mock_sender,
                use_oauth=False,
                from_email="from@example.com",
                stop_flag=lambda: False,
            )

        self.assertEqual(stats["enviados"], 1)
        self.assertEqual(stats["erros"], 0)
        self.assertGreater(len(log_messages), 0)
        self.assertGreater(len(stats_calls), 0)


if __name__ == "__main__":
    unittest.main()
