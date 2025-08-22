# PowerShell Makefile-style helpers

function Run-Dev {
  uvicorn app.main:app --reload --port 8000
}

function Test {
  pytest -q
}

function Format {
  # Optional: install black/isort or use ruff if you prefer
  python -m black .
  python -m isort .
}

function Lint {
  # If ruff is installed
  ruff check .
  
}

function DB-Migrate {
  alembic upgrade head
}

function DB-Revision {
  param([string]$message = "auto")
  alembic revision --autogenerate -m $message
}

Export-ModuleMember -Function *
