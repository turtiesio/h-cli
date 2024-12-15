"""Configuration management for h-cli."""

import os
from pathlib import Path
from typing import Any, Dict

import yaml
from dotenv import load_dotenv


def get_config_path() -> Path:
    """Get the path to the config file.

    Returns:
        Path object pointing to the config file.
    """
    config_dir = Path("config")
    return config_dir / "default.yaml"


def get_env_path() -> Path:
    """Get the path to the .env file.

    Returns:
        Path object pointing to the .env file.
    """
    return Path(os.path.expanduser("~")) / ".config" / "h-cli" / ".env"


def create_config_dir() -> None:
    """Create the config directory if it doesn't exist."""
    env_path = get_env_path()
    env_dir = env_path.parent
    if not env_dir.exists():
        env_dir.mkdir(parents=True, exist_ok=True)


def load_config() -> Dict[str, Any]:
    """Load configuration from YAML file and .env file.

    Returns:
        Dictionary containing configuration values.
        Empty dict if config file doesn't exist.
    """
    create_config_dir()
    env_path = get_env_path()
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
    else:
        raise FileNotFoundError(f"Config file not found: {env_path}")

    config_path = get_config_path()
    config = {}
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f) or {}

    # Merge environment variables into config
    for key, value in os.environ.items():
        config[key] = value

    return config
