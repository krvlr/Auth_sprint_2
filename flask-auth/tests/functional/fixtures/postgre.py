import pytest_asyncio
from settings import postgre_settings
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine


async def _delete_from_tables(engine):
    async with engine.connect() as conn, conn.begin():
        for table in postgre_settings.get_tables():
            await conn.execute(text(f"DELETE FROM {table};"))


@pytest_asyncio.fixture(scope="function")
async def postgre_engine():
    engine = create_async_engine(postgre_settings.get_db_uri())
    yield engine
    await _delete_from_tables(engine)
