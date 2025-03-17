from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import settings

engine = create_async_engine(
    str(settings.ASYNC_SQLALCHEMY_DATABASE_URI),
    pool_size=20,
    max_overflow=10,
    pool_recycle=3600,  # recycle connections after 1 hour
)
