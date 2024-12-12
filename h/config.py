"""Configuration management for h-cli."""

from pathlib import Path
from typing import Any, Dict

import yaml


def get_config_path() -> Path:
    """Get the path to the config file.

    Returns:
        Path object pointing to the config file.
    """
    config_dir = Path("config")
    return config_dir / "default.yaml"


def load_config() -> Dict[str, Any]:
    """Load configuration from YAML file.

    Returns:
        Dictionary containing configuration values.
        Empty dict if config file doesn't exist.
    """
    config_path = get_config_path()

    if not config_path.exists():
        return {}

    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}
