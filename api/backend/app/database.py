# database.py

from prisma import Prisma
from backend.app.logger import ConstellationLogger
from backend.app.config import settings
import traceback

prisma_client = Prisma(datasource={"url": str(settings.DATABASE_URL)})

logger = ConstellationLogger()

async def connect_db():
    try:
        logger.log(
            "Database",
            "info",
            f"Attempting to connect to database with URL: {str(settings.DATABASE_URL)}"
        )
        await prisma_client.connect()
        logger.log(
            "Database",
            "info",
            "Prisma Client connected successfully."
        )
    except Exception as e:
        logger.log(
            "Database",
            "critical",
            f"Failed to connect Prisma Client: {str(e)}",
            extra={"traceback": traceback.format_exc()}
        )
        raise

async def disconnect_db():
    try:
        await prisma_client.disconnect()
        logger.log(
            "Database",
            "info",
            "Prisma Client disconnected successfully."
        )
    except Exception as e:
        logger.log(
            "Database",
            "error",
            f"Failed to disconnect Prisma Client: {str(e)}",
            extra={"traceback": traceback.format_exc()}
        )