from starlette.config import Config
from starlette.datastructures import Secret

config = Config(".env")

DB_DSN = "postgresql://postgres:postgres@db:5432/monitoring"

DB_DRIVER = config("DB_DRIVER", default="postgresql")
DB_HOST = config("DB_HOST", default="localhost")
DB_PORT = config("DB_PORT", cast=int, default=5432)
DB_USER = config("DB_USER", default="postgres")
DB_PASSWORD = config("DB_PASSWORD", cast=Secret, default="postgres")
DB_DATABASE = config("DB_DATABASE", default="monitoring")

DB_POOL_MIN_SIZE = config("DB_POOL_MIN_SIZE", cast=int, default=1)
DB_POOL_MAX_SIZE = config("DB_POOL_MAX_SIZE", cast=int, default=16)
DB_ECHO = config("DB_ECHO", cast=bool, default=False)
DB_SSL = config("DB_SSL", default=None)
DB_USE_CONNECTION_FOR_REQUEST = config(
    "DB_USE_CONNECTION_FOR_REQUEST", cast=bool, default=True
)
DB_RETRY_LIMIT = config("DB_RETRY_LIMIT", cast=int, default=10)
DB_RETRY_INTERVAL = config("DB_RETRY_INTERVAL", cast=int, default=1)
