"""Configuration settings for the expense agent."""

import tempfile
from pathlib import Path
from typing import Optional

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing_extensions import Self


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="allow")

    # OpenAI
    OPENAI_API_KEY: Optional[str] = Field(None, description="API key for authenticating with the server")
    OPENAI_MODEL_NAME: Optional[str] = Field(None, description="Name of the model to use (e.g. `qwen3:8b)")
    OPENAI_BASE_URL: Optional[str] = Field(None, description="Base URL of the server")

    # Chainlit
    CHAINLIT_FILES_DIRECTORY: str = Field(
        default_factory=lambda: str(Path(tempfile.gettempdir()) / ".chainlit_files"),
        description="Directory for Chainlit to store files. Defaults to system temp directory if not specified.",
    )
    CHAINLIT_AUTH_SECRET: Optional[str] = Field(
        None,
        description="Authorization secret used for signing tokens. Can be generated using `chainlit create-secret`",
    )

    MLFLOW_TRACKING_URI: Optional[str] = Field(None, description="MLFlow Tracking URI")
    MLFLOW_EXPERIMENT_NAME: Optional[str] = Field(None, description="MLFlow Experiment Name")
    MFLOW_ACTIVE_MODEL_ID: Optional[str] = Field("database_agent_demo", description="MLFlow Experiment Name")

    @property
    def openai_enabled(self) -> bool:
        """Check if required OpenAI environment variables are set."""
        return self.OPENAI_API_KEY is not None and self.OPENAI_MODEL_NAME is not None

    @property
    def auth_enabled(self) -> bool:
        """Check if required Keycloak environment variables are set."""
        return self.CHAINLIT_AUTH_SECRET is not None

    @model_validator(mode="after")
    def llm(self) -> Self:
        """Validate that there are at least one set of required environment variables for the LLM."""
        if not self.openai_enabled:
            raise Exception(
                "Missing required environment variables for LLM. Please ensure OPENAI_API_KEY and OPENAI_MODEL_NAME are in your environment or .env file."
            )
        return self
