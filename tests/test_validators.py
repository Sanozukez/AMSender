import unittest

from src.validators import Validators


class ValidatorsTests(unittest.TestCase):
    def test_valid_email(self):
        ok, msg = Validators.validate_email("user@example.com")
        self.assertTrue(ok)
        self.assertIsNone(msg)

    def test_invalid_email(self):
        ok, msg = Validators.validate_email("user@@example")
        self.assertFalse(ok)
        self.assertIsNotNone(msg)


if __name__ == "__main__":
    unittest.main()
