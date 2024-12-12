"""Base plugin interface for h-cli."""

from abc import ABC, abstractmethod
from typing import Any, Dict

import typer
from rich.console import Console


class Plugin(ABC):
    """Base class for all h-cli plugins.

    This class defines the interface that all plugins must implement.
    Each plugin should subclass this and implement the register method.
    """

    def __init__(self, ctx: typer.Context):
        """Initialize plugin with context.

        Args:
            ctx: Typer context containing configuration and utilities.
        """
        self.ctx = ctx
        self.config: Dict[str, Any] = ctx.obj["config"]
        self.logger = ctx.obj["logger"]
        self.console: Console = ctx.obj["console"]
        self.verbose: bool = ctx.obj["verbose"]

    @abstractmethod
    def register(self, app: typer.Typer) -> None:
        """Register plugin commands with the CLI app.

        This method should be implemented by each plugin to register
        its commands with the main Typer application.

        Args:
            app: The main Typer application instance.
        """
        pass
