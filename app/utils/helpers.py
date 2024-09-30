# app/utils/helpers.py

from supabase import create_client, Client
from app.config import settings
from app.logger import ConstellationLogger

class SupabaseClientManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SupabaseClientManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.logger = ConstellationLogger()
        self.client = self.connect()

    def connect(self) -> Client:
        try:
            client = create_client(str(settings.SUPABASE_URL), settings.SUPABASE_KEY)
            self.logger.log("SupabaseClientManager", "info", "Supabase client connected successfully.")
            return client
        except Exception as e:
            self.logger.log("SupabaseClientManager", "critical", f"Failed to connect Supabase client: {e}")
            return None

    def get_client(self) -> Client:
        if not self.client:
            self.client = self.connect()
        return self.client

    def disconnect(self):
        pass

# Initialize the Supabase client manager
supabase_manager = SupabaseClientManager()


if __name__ == "__main__":
    manager = SupabaseClientManager()
    
    print("Checking Supabase connection...")
    if manager.is_connected():
        print("Supabase client is connected.")
    else:
        print("Supabase client is not connected.")
    
    print("\nTesting Supabase connection...")
    if manager.test_connection():
        print("Successfully connected to Supabase and queried the database.")
    else:
        print("Failed to connect to Supabase or query the database.")
    
    print("\nChecking Supabase health...")
    if manager.check_health():
        print("Supabase health check passed.")
    else:
        print("Supabase health check failed.")
    
    print("\nRetrieving Supabase statistics...")
    stats = manager.get_statistics()
    if stats:
        print(f"Statistics: {stats}")
    else:
        print("Failed to retrieve statistics.")
