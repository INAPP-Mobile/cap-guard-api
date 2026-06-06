from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    cap_endpoint: Optional[str] = None
    cap_secret_key: Optional[str] = None
    pow_default_difficulty: int = 4
    
    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

settings = Settings()
