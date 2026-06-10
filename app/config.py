from functools import lru_cache
from pathlib import Path
from pydantic import BaseModel
from dotenv import dotenv_values
import os


ROOT_DIR = Path(__file__).resolve().parent.parent
APP_DIR = ROOT_DIR / "app"
DATA_DIR = APP_DIR / "data"
GENERATED_DIR = ROOT_DIR / "generated"


class Settings(BaseModel):
    mistral_api_key: str | None = None
    mistral_model: str = "mistral-small-latest"
    github_token: str | None = None
    portfolio_url: str = "https://wsmaisys.github.io/waseemmansari.github.io/"
    github_username: str = "wsmaisys"


@lru_cache
def get_settings() -> Settings:
    env_path = ROOT_DIR / ".env"
    file_values = dotenv_values(env_path) if env_path.exists() else {}
    return Settings(
        mistral_api_key=(
            os.getenv("MISTRAL_API_KEY")
            or os.getenv("mistral_api_key")
            or file_values.get("MISTRAL_API_KEY")
            or file_values.get("mistral_api_key")
        ),
        mistral_model=os.getenv("MISTRAL_MODEL")
        or file_values.get("MISTRAL_MODEL")
        or "mistral-small-latest",
        github_token=os.getenv("GITHUB_TOKEN") or file_values.get("GITHUB_TOKEN"),
    )

