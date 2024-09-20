# app/database.py

from app.utils.helpers import SupabaseClientManager
from app.logger import ConstellationLogger
from app.config import settings

# Initialize the logger instance
logger = ConstellationLogger()

# Initialize the Supabase client manager
supabase_manager = SupabaseClientManager()

def get_supabase_client() -> 'Client':
    """
    Retrieve the Supabase client instance.
    
    Returns:
        Client: The Supabase client for interacting with the backend.
    """
    if supabase_manager.is_connected():
        return supabase_manager.client
    else:
        logger.log("database", "error", "Supabase client is not connected.")
        raise ConnectionError("Supabase client is not connected.")
