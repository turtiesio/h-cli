import pytest
from typer.testing import CliRunner
from app.frameworks.cli import app

@pytest.fixture
def cli_app():
    return app

@pytest.fixture
def runner():
    return CliRunner()

def test_version_command(cli_app, runner):
    result = runner.invoke(cli_app, ["--version"])
    assert result.exit_code == 0
    assert "h-cli version" in result.output