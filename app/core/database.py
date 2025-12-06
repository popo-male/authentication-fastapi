from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.config import settings

engine = create_async_engine(str(settings.DATABASE_URL))

async_session_local = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


async def get_db():
    async with async_session_local() as session:
        yield session
