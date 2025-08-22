# Contributing

Thanks for your interest in contributing!

## Development setup
- Create a virtualenv and install dev dependencies:
  ```bash
  pip install -r requirements.txt
  pip install -U black isort ruff pre-commit
  pre-commit install
  ```
- Run the app:
  ```bash
  uvicorn app.main:app --reload --port 8000
  ```

## Commit style
- Keep commits small and focused.
- Include tests when adding features or fixing bugs.

## Pull Requests
- Ensure `pytest -q` passes.
- Lint passes: `ruff check .`, `black --check .`, `isort --check-only .`.
- Describe what changed and why.
# Contributing

Thanks for your interest in contributing!

## Development setup
- Create a virtualenv and install dev dependencies:
  ```bash
  pip install -r requirements.txt
  pip install -U black isort ruff pre-commit
  pre-commit install
  ```
- Run the app:
  ```bash
  uvicorn app.main:app --reload --port 8000
  ```

## Commit style
- Keep commits small and focused.
- Include tests when adding features or fixing bugs.

## Pull Requests
- Ensure `pytest -q` passes.
- Lint passes: `ruff check .`, `black --check .`, `isort --check-only .`.
- Describe what changed and why.
