from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class BootstrapState:
    database_path: Path
    initialized: bool


def initialize_database(database_path: Path) -> BootstrapState:
    database_path.parent.mkdir(parents=True, exist_ok=True)
    database_path.touch(exist_ok=True)
    return BootstrapState(database_path=database_path, initialized=True)
