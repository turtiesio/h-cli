"""app - Core application package following Clean Architecture."""
from .core.config import load_config
from .frameworks.logger import setup_logger

__version__ = "0.1.0"

__all__ = ["load_config", "setup_logger", "__version__"]