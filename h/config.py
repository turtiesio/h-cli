"""Configuration management for h-cli."""

import os
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def get_config_path() -> Path:
    """Get the path to the config file."""
    config_dir = Path("config")
    return config_dir / "default.yaml"


def get_global_config_path() -> Path:
    """Get the path to the global config file."""
    return Path(os.path.expanduser("~")) / ".config" / "h-cli" / "config.yaml"


def copy_default_config_if_not_exists() -> None:
    """Copy the default config to the global path if it doesn't exist."""
    global_config_path = get_global_config_path()
    if not global_config_path.exists():
        global_config_path.parent.mkdir(parents=True, exist_ok=True)
        default_config_path = get_config_path()
        shutil.copy2(default_config_path, global_config_path)


class AppConfig(BaseModel):
    """Application configuration."""

    name: str = Field(default="h-cli", description="Application name")
    version: str = Field(default="0.1.0", description="Application version")


class PluginConfig(BaseModel):
    """Plugin configuration."""

    enabled: List[str] = Field(default_factory=list, description="List of enabled plugins")


class LoggingConfig(BaseModel):
    """Logging configuration."""

    level: str = Field(default="INFO", description="Logging level")
    format: str = Field(
        default="%(asctime)s %(name)s %(levelname)s %(message)s",
        description="Logging format",
    )


class Config(BaseSettings):
    """Main configuration model."""

    app: AppConfig = Field(description="Application configuration")
    plugins: PluginConfig = Field(description="Plugin configurations")
    logging: LoggingConfig = Field(description="Logging configuration")
    api_key: Optional[str] = Field(default=None, description="API key for AI models")
    gemini_api_key: Optional[str] = Field(default=None, description="API key for Gemini model")
    openrouter_api_key: Optional[str] = Field(default=None, description="API key for OpenRouter")

    @classmethod
    def from_yaml(cls, config_path: Path, **kwargs: Any) -> "Config":
        """Load configuration from YAML file."""
        config = {}
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f) or {}

        return cls(**config, **kwargs)

def load_config(**kwargs: Any) -> Config:
    """Load configuration from YAML file."""
    copy_default_config_if_not_exists()
    config_path = get_global_config_path()
    print(f"Using config file: {config_path}")

    return Config.from_yaml(config_path, **kwargs)

_CONFIG = load_config()

def get_config() -> Config:
    return _CONFIG

