# app/database.py

import traceback
from prisma import Prisma
from supabase import create_client, Client
from backend.app.logger import ConstellationLogger
from backend.app.config import settings

class Database:
    """
    Singleton Database Class to manage the Prisma Client and Supabase Client instances.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
            # Convert MultiHostUrl to string for Prisma
            database_url = str(settings.DATABASE_URL)
            cls._instance.prisma = Prisma(datasource={"url": database_url})
            cls._instance.logger = ConstellationLogger()
            
            # Initialize Supabase client
            cls._instance.supabase: Client = create_client(
                str(settings.SUPABASE_URL),
                settings.SUPABASE_KEY
            )
        return cls._instance

    async def connect(self):
        """
        Asynchronously connects the Prisma Client to the database.
        """
        try:
            self.logger.log(
                "Database",
                "info",
                f"Attempting to connect to database with URL: {str(settings.DATABASE_URL)}"
            )
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

# Make Supabase client easily accessible
supabase = database.supabase
print('connected to supabase')