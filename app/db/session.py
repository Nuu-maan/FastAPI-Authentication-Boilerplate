from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# Synchronous SQLAlchemy engine/session for FastAPI dependencies
db_url = settings.DATABASE_URL
if not db_url:
    if settings.DB_BACKEND == "sqlite":
        db_url = f"sqlite:///{settings.SQLITE_PATH}"
    else:
        # default to local postgres if not provided
        db_url = "postgresql+psycopg://postgres:postgres@db:5432/fastapi_auth"

connect_args = {}
if db_url.startswith("sqlite:"):
    # Needed for SQLite when used with multiple threads
    connect_args["check_same_thread"] = False

engine = create_engine(db_url, pool_pre_ping=True, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
