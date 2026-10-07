import os

APP_ENV = os.getenv("APP_ENV", "development").strip().lower()


def normalize_database_url(value: str) -> str:
    """Accept the standard Neon PostgreSQL URL and SQLAlchemy psycopg URLs."""
    value = value.strip()
    if value.startswith("postgres://"):
        return "postgresql+psycopg://" + value[len("postgres://") :]
    if value.startswith("postgresql://"):
        return "postgresql+psycopg://" + value[len("postgresql://") :]
    return value


_raw_database_url = os.getenv("DATABASE_URL", "").strip()

if _raw_database_url:
    DATABASE_URL = normalize_database_url(_raw_database_url)
elif APP_ENV == "development":
    DATABASE_URL = "postgresql+psycopg://synthetic:synthetic@localhost:5432/synthetic_lab"
else:
    raise RuntimeError("DATABASE_URL must be configured for non-development environments.")

CORS_ORIGINS = [
    item.strip()
    for item in os.getenv("CORS_ORIGINS", "*").split(",")
    if item.strip()
]

DB_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "3"))
DB_MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "2"))
