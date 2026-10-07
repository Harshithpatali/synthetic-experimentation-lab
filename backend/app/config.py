import os
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql+psycopg://synthetic:synthetic@localhost:5432/synthetic_lab")
CORS_ORIGINS = [x.strip() for x in os.environ.get("CORS_ORIGINS", "*").split(",") if x.strip()]
