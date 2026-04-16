from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Settings:
    database_path: Path = PROJECT_ROOT / "db" / "finally.db"
    database_path_label: str = "db/finally.db"


settings = Settings()
