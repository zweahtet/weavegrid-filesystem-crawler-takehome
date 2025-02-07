from pathlib import Path
from pydantic import BaseSettings


class Settings(BaseSettings):
    """Main configuration class loaded from environment variables.

    Attributes:
        ROOT_DIR (Path): Base directory for file operations
    """
    ROOT_DIR: Path

    class Config:
        env_file = ".env"


settings = Settings()
