# database.py

from prisma import Prisma
from backend.app.logger import ConstellationLogger
from backend.app.config import settings
import traceback
from supabase import create_client, Client

prisma_client = Prisma(datasource={"url": str(settings.DATABASE_URL)})
supabase_client: Client = None

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

def connect_supabase():
    global supabase_client
    try:
        logger.log(
            "Database",
            "info",
            f"Attempting to connect to Supabase with URL: {settings.SUPABASE_URL}"
        )
        supabase_client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        logger.log(
            "Database",
            "info",
            "Supabase Client connected successfully."
        )
        return supabase_client
    except Exception as e:
        logger.log(
            "Database",
            "critical",
            f"Failed to connect Supabase Client: {str(e)}",
            extra={"traceback": traceback.format_exc()}
        )
        raise

def get_supabase_client() -> Client:
    global supabase_client
    if supabase_client is None:
        supabase_client = connect_supabase()
    return supabase_client