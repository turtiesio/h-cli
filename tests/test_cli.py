"""Tests for the main CLI functionality."""

from typing import Any, Dict

import pytest
from typer.testing import CliRunner

from h.cli import app, get_context_data


@pytest.fixture
def runner() -> CliRunner:
    """Fixture providing a Typer CLI runner.

    Returns:
        CliRunner instance.
    """
    return CliRunner()


@pytest.fixture
def context_data() -> Dict[str, Any]:
    """Fixture providing common context data.

    Returns:
        Dictionary containing context data.
    """
    return get_context_data()


def test_cli_help(runner: CliRunner) -> None:
    """Test that the CLI help command works.

    Args:
        runner: CliRunner fixture.
    """
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Personal productivity CLI tool" in result.stdout


def test_context_data(context_data: Dict[str, Any]) -> None:
    """Test that context data contains required keys.

    Args:
        context_data: Context data fixture.
    """
    assert "config" in context_data
    assert "logger" in context_data
    assert "console" in context_data
