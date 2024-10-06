import asyncio
from prisma import Prisma
from api.backend.app.config import settings

class PrismaClientManager:
    _instance = None
    _client = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def connect(self):
        if self._client is None:
            self._client = Prisma(datasource={'url': settings.POSTGRES_URL})
            await self._client.connect()
        return self._client

    async def disconnect(self):
        if self._client is not None:
            await self._client.disconnect()
            self._client = None

    @property
    def client(self):
        if self._client is None:
            raise RuntimeError("Prisma client is not connected. Call connect() first.")
        return self._client

# Create a global instance of the PrismaClientManager
prisma_manager = PrismaClientManager()

# Create a prisma client
async def get_prisma():
    return await prisma_manager.connect()

async def main():
    db = await get_prisma()
    
    # Your database operations here
    print("Connected to the database successfully!")

    await prisma_manager.disconnect()

if __name__ == "__main__":
    asyncio.run(main())