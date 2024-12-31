import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from app.adapters.base.merge_files import add_merge_files
from app.frameworks.cli import app

pytest_plugins = ["pytest_logging"]

runner = CliRunner()

@pytest.fixture
def setup_test_files(tmp_path):
    # Create test files
    file1 = tmp_path / "file1.txt"
    file1.write_text("File 1 content")
    
    file2 = tmp_path / "file2.py"
    file2.write_text("File 2 content")
    
    # Create a git repository
    os.chdir(tmp_path)
    os.system("git init")
    os.system("git add .")
    os.system("git commit -m 'Initial commit'")
    
    return tmp_path, file1, file2

def test_merge_files_with_input_files(setup_test_files):
    tmp_path, file1, file2 = setup_test_files
    
    result = runner.invoke(app, ["m", "--file", str(file1), "--file", str(file2)])
    
    assert result.exit_code == 0
    assert "Merged Files" in result.output
    
    # Verify merged content
    merged_file = Path(tempfile.gettempdir()) / "merged_files.txt"
    assert merged_file.exists()
    
    content = merged_file.read_text()
    assert "File 1 content" in content
    assert "File 2 content" in content

def test_merge_files_with_mixed_sources(setup_test_files):
    tmp_path, file1, file2 = setup_test_files
    
    # Create a new file not in git
    file3 = tmp_path / "file3.md"
    file3.write_text("File 3 content")
    
    result = runner.invoke(app, ["m", "--file", str(file3)])
    
    assert result.exit_code == 0
    assert "Merged Files" in result.output
    
    # Verify merged content
    merged_file = Path(tempfile.gettempdir()) / "merged_files.txt"
    assert merged_file.exists()
    
    content = merged_file.read_text()
    assert "File 1 content" in content  # From git
    assert "File 2 content" in content  # From git
    assert "File 3 content" in content  # From input file

def test_merge_files_non_git_repository(tmp_path):
    # Create files in a non-git directory
    file1 = tmp_path / "file1.txt"
    file1.write_text("File 1 content")
    
    os.chdir(tmp_path)
    
    result = runner.invoke(app, ["m", "--file", str(file1)])
    
    assert result.exit_code == 0
    assert "Merged Files" in result.output
    
    # Verify merged content
    merged_file = Path(tempfile.gettempdir()) / "merged_files.txt"
    assert merged_file.exists()
    
    content = merged_file.read_text()
    assert "File 1 content" in content

def test_merge_files_with_invalid_files(setup_test_files, caplog):
    tmp_path, _, _ = setup_test_files
    
    # Try to merge non-existent file
    invalid_file = tmp_path / "nonexistent.txt"
    
    result = runner.invoke(app, ["m", "--file", str(invalid_file)])
    
    assert result.exit_code == 0
    # Check logs for warning message
    caplog.clear()
    result = runner.invoke(app, ["m", "--file", str(invalid_file)])
    assert any("File not found, skipping" in record.message for record in caplog.records)