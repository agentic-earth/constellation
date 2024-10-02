```python:api/backend/app/database.py
# app/database.py

"""
Database Module

This module initializes and provides a singleton instance of the Prisma Client.
It ensures that a single connection to the database is maintained throughout the application's lifecycle,
optimizing resource usage and maintaining consistency across services.
"""
import traceback
import asyncio
from prisma import Prisma
from backend.app.logger import ConstellationLogger

class Database:
    """
    Singleton Database Class to manage the Prisma Client instance.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
            cls._instance.prisma = Prisma()
            cls._instance.logger = ConstellationLogger()
        return cls._instance

    async def connect(self):
        """
        Asynchronously connects the Prisma Client to the database.
        """
        try:
            await self.prisma.connect()
            self.logger.log(
                "Database",
                "info",
                "Prisma Client connected successfully."
            )
        except Exception as e:
            self.logger.log(
                "Database",
                "critical",
                f"Failed to connect Prisma Client: {str(e)}",
                extra={"traceback": traceback.format_exc()}
            )
            raise

    async def disconnect(self):
        """
        Asynchronously disconnects the Prisma Client from the database.
        """
        try:
            await self.prisma.disconnect()
            self.logger.log(
                "Database",
                "info",
                "Prisma Client disconnected successfully."
            )
        except Exception as e:
            self.logger.log(
                "Database",
                "error",
                f"Failed to disconnect Prisma Client: {str(e)}",
                extra={"traceback": traceback.format_exc()}
            )

# Initialize the Database Singleton
database = Database()

# Connect to the database when the module is imported
async def init_db():
    await database.connect()

# Ensure the database is connected upon starting the application
import asyncio
asyncio.create_task(init_db())