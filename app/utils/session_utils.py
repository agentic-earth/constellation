from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from fastapi import Depends
from app.config import settings
import asyncio
from sqlalchemy import text

# Create an async engine and session
DATABASE_URL = settings.POSTGRES_URL
DATABASE_URL = DATABASE_URL.replace("[YOUR-PASSWORD]", settings.DATABASE_PWD)
DATABASE_URL = DATABASE_URL.split(":", 1)[0] + "+asyncpg" + ":" + DATABASE_URL.split(":", 1)[1]

# DATABASE_URL = f"postgresql+asyncpg://postgres.xxikoihjvqzqjjzbjboj:{settings.DATABASE_PWD}@aws-0-us-west-1.pooler.supabase.com:6543/postgres"
print(DATABASE_URL)

engine = create_async_engine(DATABASE_URL, echo=True, future=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Dependency to get the async session
async def get_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
            yield session

async def main():
    async for session in get_session():
        print(session)
        result = await session.execute(text("SELECT 1"))
        assert result.scalar() == 1

if __name__ == "__main__":
    asyncio.run(main())