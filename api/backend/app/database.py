from supabase import create_client, Client
from backend.app.config import settings
from backend.app.logger import ConstellationLogger
from prisma import Prisma
import traceback
import os

logger = ConstellationLogger()

supabase_client: Client | None = None
supabase_admin_client: Client | None = None
prisma_client = Prisma()
def connect_supabase() -> Client:

    try:
        url: str = os.environ.get('SUPABASE_URL')
        key: str = os.environ.get('SUPABASE_KEY')

        if not url or not key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in configuration.")

        logger.log("Database", "info", f"Attempting to connect to Supabase with URL: {url}")
        client = create_client(url, key)
        logger.log("Database", "info", "Supabase Client connected successfully.")
        return client
    except Exception as e:
        logger.log("Database", "critical", f"Failed to connect Supabase Client: {str(e)}")
        raise

def get_supabase_client() -> Client:
    global supabase_client
    if supabase_client is None:
        supabase_client = connect_supabase()
    return supabase_client

def connect_supabase_admin() -> Client:
    try:
        print('@'*100)
        print(settings)
        print('@'*100)
        url: str = os.environ.get('SUPABASE_URL')
        service_key: str = os.environ.get('SUPABASE_SERVICE_KEY')

        if not url or not service_key:
            raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_KEY must be set in configuration.")

        logger.log("Database", "info", f"Attempting to connect to Supabase Admin with URL: {url}")
        client = create_client(url, service_key)
        logger.log("Database", "info", "Supabase Admin Client connected successfully.")
        return client
    except Exception as e:
        logger.log("Database", "critical", f"Failed to connect Supabase Admin Client: {str(e)}")
        raise

def get_supabase_admin_client() -> Client:
    global supabase_admin_client
    if supabase_admin_client is None:
        supabase_admin_client = connect_supabase_admin()
    return supabase_admin_client

async def connect_db():
    try:
        database_url = settings.DATABASE_URL
        if not database_url:
            raise ValueError("DATABASE_URL must be set in configuration.")

        logger.log(
            "Database",
            "info",
            f"Attempting to connect to database with URL: {database_url}"
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