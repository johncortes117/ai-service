# Contributing to AI-Powered Tender Analyst

Thank you for your interest in contributing! This guide will help you set up your development environment and understand the project structure.

## Development Environment Setup

This project uses **uv** for Python dependency management and **npm** for the frontend.

### 1. Python Environment (Backend)

Ensure you have `uv` installed. If not:
```bash
pip install uv
```

Install dependencies:
```bash
uv sync
```

### 2. Environment Variables

Copy the example configuration:
```bash
cp .env.example .env
```

Required variables:
- `OPENAI_API_KEY`: Your OpenAI API key for the agents.
- `SRI_API_URL` (Optional): For RUC validation integration.

### 3. Running Tests

We use `pytest` for testing. The test suite includes system health checks and API endpoint verification.

To run all tests:
```bash
uv run pytest
```

To run detailed verbose tests:
```bash
uv run pytest -v
```

**Key Test Files:**
- `tests/test_system_health.py`: Checks environment variables, directory permissions, and critical imports.
- `tests/test_api_basic.py`: Verifies API endpoints are up and responding correctly.

## Project Architecture

### 🧠 Agent System (`app/agents/`)

The core logic lies in `app/agents/tenderAnalyzer/`. We use **LangGraph** to manage the state and workflow.

- **`mainGraph.py`**: Defines the state machine node transitions.
- **`specialistNodes.py`**: Contains the logic for the Legal, Financial, and Technical agents.
- **`tools.py`**: Custom tools available to agents (e.g., `validateRuc`).

### 🔌 API Layer (`app/api/`)

Built with **FastAPI**.

- **`main.py`**: Entry point. **Note**: Uses `lifespan` context manager for startup events.
- **`services/`**: Business logic separated from HTTP handlers.
    - `tender_service.py`: Handles file uploads and organization.
    - `sse_service.py`: Manages real-time streaming to the frontend.

## Submitting Changes

1.  Fork the repository.
2.  Create a feature branch: `git checkout -b feature/amazing-feature`.
3.  Commit your changes.
4.  Run tests to ensure nothing is broken.
5.  Push to the branch.
6.  Open a Pull Request.

## Code Style

- **Python**: Follow PEP 8.
- **Frontend**: Use the existing ESLint/Prettier configuration.

## Support

If you encounter any issues, please open an issue on the GitHub repository.
