# app/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # default development values (override via .env or system env)
    validator_url: str = "http://127.0.0.1:8000/execute_command"
    validator_api_key: str = "dev-key"
    request_timeout: int = 3
    retry_count: int = 2
    robot_control_url: str = "http://127.0.0.1:8200/execute"

    # Allow extra env vars to be present without causing validation errors.
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="allow"   # <--- important: ignore unexpected env vars
    )

# single shared settings instance
settings = Settings()
