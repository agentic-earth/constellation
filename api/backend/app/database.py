# app/database.py

import traceback
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