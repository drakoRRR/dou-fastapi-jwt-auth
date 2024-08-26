import os
from dotenv import load_dotenv

from pydantic import PostgresDsn


load_dotenv()

DEBUG: int = os.getenv("DEBUG", 1)
SECRET_KEY: str = os.getenv("SECRET_KEY", "secret_key")

POSTGRES_USER: str = os.getenv("POSTGRES_USER", default="postgres")
POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", default="postgres")
DB_HOST: str = os.getenv("DB_HOST", default="0.0.0.0")
DB_PORT: int = os.getenv("DB_PORT", default=5432)
DB_NAME: str = os.getenv("POSTGRES_DB", default="db")

DATABASE_URL: PostgresDsn = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

POSTGRES_TEST_USER: str = os.getenv("POSTGRES_TEST_USER", default="postgres_test")
POSTGRES_TEST_PASSWORD: str = os.getenv("POSTGRES_TEST_PASSWORD", default="postgres_test")
DB_TEST_PORT: int = os.getenv("DB_TEST_PORT", default=5433)
DB_TEST_HOST: str = os.getenv("DB_TEST_HOST", default="0.0.0.0")
DB_TEST_NAME: str = os.getenv("POSTGRES_DB_TEST", default="db_test")

DATABASE_TEST_ASYNC_URL: PostgresDsn = f"postgresql+asyncpg://{POSTGRES_TEST_USER}:{POSTGRES_TEST_PASSWORD}@{DB_TEST_HOST}:{DB_TEST_PORT}/{DB_TEST_NAME}"
DATABASE_TEST_SYNC_URL: PostgresDsn = f"postgresql://{POSTGRES_TEST_USER}:{POSTGRES_TEST_PASSWORD}@{DB_TEST_HOST}:{DB_TEST_PORT}/{DB_TEST_NAME}"