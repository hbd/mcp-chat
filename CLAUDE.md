# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MCP Chat is a Python-based MCP (Model Context Protocol) server that enables direct chat between users through MCP tool calls. It demonstrates using MCP's tool-calling interface for real-time human communication.

## Development Setup

This is a Python project using the following tools and conventions:

### Package Management
- **uv**: Use `uv` for all package management tasks
  - Install dependencies: `uv sync`
  - Add new dependencies: `uv add <package>`
  - Create virtual environment: `uv venv`

### MCP Framework
- **FastMCP**: This project uses the FastMCP framework for building the MCP server
  - Follow FastMCP conventions for handlers and server setup
  - Use FastMCP's built-in decorators and utilities

### Code Quality Tools
- **mypy**: Type checking
  - Run with: `mypy .`
  - Ensure all code has proper type annotations
  - Fix all type errors before committing
  
- **Ruff**: Linting and formatting
  - Format code: `ruff format .`
  - Lint code: `ruff check .`
  - Fix linting issues: `ruff check --fix .`
  - Always run both before committing changes

## Development Commands

```bash
# Set up environment
uv venv
source .venv/bin/activate  # On Unix/macOS
# or
.venv\Scripts\activate  # On Windows

# Install dependencies
uv sync

# Type checking
mypy .

# Linting and formatting
ruff format .
ruff check --fix .

# Run the MCP server
python -m mcp_chat.server
```

## Project Structure

```
mcp-chat/
├── mcp_chat/
│   ├── __init__.py
│   ├── server.py          # Main MCP server entry point
│   ├── handlers/          # MCP request handlers
│   ├── matching/          # Interest matching algorithms
│   └── models/            # Data models and types
├── tests/
├── pyproject.toml         # Project configuration and dependencies
└── README.md
```

## Code Conventions

- Use type hints for all functions and class methods
- Follow PEP 8 style guide (enforced by Ruff)
- Write docstrings for all public functions and classes
- Keep functions focused and single-purpose
- Use descriptive variable and function names
- **Always use absolute import paths** (e.g., `from mcp_chat.models import User` not `from .models import User`)

## Claude Configuration

The project contains a `.claude/settings.local.json` file that manages permissions for the Bash tool.