# h-cli

Personal productivity CLI tool with plugin architecture.

## Features

- Plugin-based architecture for extensible functionality
- JSON logging with structlog
- Configuration management via YAML
- Clean architecture following SOLID principles

## Installation

### Global Installation (Recommended)

```bash
# Install globally using pipx
make install-global

# Uninstall if needed
make uninstall-global
```

### Development Installation

```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies for development
make install

# Run tests
make test

# Run linting and type checking
make lint
```

## Usage

```bash
# Show help
h --help

# Run with verbose logging
h --verbose

# Show version
h version
```

## Development

### Project Structure

```
h-cli/
├── config/
│   └── default.yaml     # Configuration settings
├── h/
│   ├── cli.py          # Main CLI entry point
│   ├── config.py       # Configuration management
│   ├── logger.py       # Structured logging setup
│   └── plugins/        # Plugin implementations
└── tests/              # Unit tests
```

### Development Guidelines

- Follow SOLID principles and Clean Architecture
- Write unit tests for all functionality
- Use docstrings for documentation
- Configure via YAML files, not environment variables
- Use structured logging with structlog
- No hardcoding of values

### Available Make Commands

```bash
make help          # Show available commands
make install      # Install development dependencies
make test         # Run tests
make lint         # Run linters
make format       # Format code
make check        # Run all checks
make run -- args  # Run CLI with arguments
