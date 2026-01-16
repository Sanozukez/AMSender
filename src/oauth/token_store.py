"""Persistência de tokens OAuth."""
import pickle
from pathlib import Path
from typing import Optional


class TokenStore:
    def __init__(self, token_file: Path):
        self.token_file = Path(token_file)
        self.token_file.parent.mkdir(parents=True, exist_ok=True)

    def load(self):
        if not self.token_file.exists():
            return None
        with open(self.token_file, "rb") as f:
            return pickle.load(f)

    def save(self, creds) -> None:
        with open(self.token_file, "wb") as f:
            pickle.dump(creds, f)

    def delete(self) -> None:
        if self.token_file.exists():
            self.token_file.unlink()
