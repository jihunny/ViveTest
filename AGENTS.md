# Repository Guidelines

## Project Structure & Module Organization
- Root Python app: `main.py` (entry point).
- Project metadata: `pyproject.toml` (Python >=3.12).
- Repo docs: `README.md`.
- Tests (add as needed): place under `tests/` (e.g., `tests/test_main.py`).

Example layout:
```
.
├─ main.py
├─ pyproject.toml
├─ README.md
└─ tests/              # add when tests are introduced
```

## Build, Test, and Development Commands
- Run app: `python main.py` (or `uv run python main.py` if using uv).
- Lint (optional if installed): `ruff check .`
- Format (optional if installed): `ruff format .` or `black .`
- Tests (when added): `pytest -q` (or `uv run pytest -q`).

Tip: uv users can run tools without local install, e.g., `uvx ruff check .`.

## Coding Style & Naming Conventions
- Python style: 4-space indent, UTF-8, Unix newlines where possible.
- Typing: prefer type hints for public functions; keep functions small.
- Naming: `snake_case` for functions/vars, `PascalCase` for classes, `UPPER_SNAKE_CASE` for constants, modules in `snake_case`.
- Lint/format: prefer `ruff` for linting and formatting; keep code clean and imports sorted.
- Structure: keep the entry logic in `main()`; avoid side effects at import time.

## Testing Guidelines
- Framework: `pytest`.
- Location: all tests in `tests/`.
- Naming: files `test_*.py`, tests `test_*` functions, fixtures in `conftest.py`.
- Coverage: aim for critical-path coverage (main flows and error cases). Add regression tests for fixed bugs.
- Run: `pytest -q` locally and before PRs.

## Commit & Pull Request Guidelines
- Commits: imperative mood, short subject (<72 chars), meaningful body when needed. Group related changes.
- Examples: `fix: handle empty input in main()`, `chore: add ruff config`.
- PRs: clear description, linked issues (e.g., `Closes #12`), steps to test, and before/after output or screenshots when relevant. Keep PRs focused and small.

## Security & Configuration Tips
- Python: require `>=3.12` (see `pyproject.toml`).
- Do not commit secrets or `.venv/`, `__pycache__/`, or `*.pyc` files. Add to `.gitignore` as needed.
- Use environment variables for credentials and configuration.
