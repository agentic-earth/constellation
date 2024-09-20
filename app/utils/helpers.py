# app/utils/helpers.py

from supabase import create_client, Client
from app.config import Settings
from app.logger import ConstellationLogger
from typing import Optional, Dict, Any
import requests


class SupabaseClientManager:
    """
    Manages the Supabase client instance for the application.

    Implements the Singleton pattern to ensure only one instance exists.
    Provides methods to connect, check health, retrieve statistics, and manage the client.
    """

    _instance = None

    def __new__(cls) -> 'SupabaseClientManager':
        if cls._instance is None:
            cls._instance = super(SupabaseClientManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.config = Settings()
        self.logger = ConstellationLogger()
        self.client: Optional[Client] = None
        self.connect()

    def connect(self) -> None:
        """
        Initialize the Supabase client using the provided configuration.
        """
        try:
            self.client = create_client(self.config.SUPABASE_URL, self.config.SUPABASE_KEY)
            self.logger.log("SupabaseClientManager", "info", "Supabase client connected successfully.")
        except Exception as e:
            self.logger.log("SupabaseClientManager", "critical", f"Failed to connect Supabase client: {e}")

    def disconnect(self) -> None:
        """
        Disconnect the Supabase client.
        Note: supabase-py does not require explicit disconnection as it operates over HTTP.
        This method clears the client instance.
        """
        if self.client:
            self.logger.log("SupabaseClientManager", "info", "Supabase client disconnected.")
            self.client = None
        else:
            self.logger.log("SupabaseClientManager", "warning", "Supabase client was not connected.")

    def check_health(self) -> bool:
        """
        Check the health of the Supabase backend by making a lightweight request.

        Returns:
            bool: True if the backend is responsive, False otherwise.
        """
        if not self.client:
            self.logger.log("SupabaseClientManager", "error", "Supabase client is not connected.")
            return False

        try:
            # Attempt to fetch a lightweight resource, such as the current user
            response = self.client.auth.api.get_user()
            if response.status_code == 200:
                self.logger.log("SupabaseClientManager", "info", "Supabase health check passed.")
                return True
            else:
                self.logger.log("SupabaseClientManager", "error", f"Supabase health check failed with status code {response.status_code}.")
                return False
        except requests.exceptions.RequestException as e:
            self.logger.log("SupabaseClientManager", "critical", f"Supabase health check encountered an exception: {e}")
            return False

    def get_statistics(self) -> Optional[Dict[str, Any]]:
        """
        Retrieve general statistics from the Supabase backend.

        Returns:
            Optional[Dict[str, Any]]: A dictionary containing statistics if successful, None otherwise.
        """
        if not self.client:
            self.logger.log("SupabaseClientManager", "error", "Supabase client is not connected.")
            return None

        try:
            # Example: Fetch the number of users
            users_response = self.client.table("users").select("user_id").execute()
            if users_response.status_code == 200:
                user_count = len(users_response.data)
                self.logger.log("SupabaseClientManager", "info", f"Retrieved user count: {user_count}")
            else:
                user_count = None
                self.logger.log("SupabaseClientManager", "error", f"Failed to retrieve user count with status code {users_response.status_code}.")

            # Add more statistics as needed
            statistics = {
                "user_count": user_count,
                # Add other statistics here
            }

            return statistics
        except Exception as e:
            self.logger.log("SupabaseClientManager", "critical", f"Failed to retrieve statistics: {e}")
            return None

    def is_connected(self) -> bool:
        """
        Check if the Supabase client is currently connected.

        Returns:
            bool: True if connected, False otherwise.
        """
        connected = self.client is not None
        self.logger.log("SupabaseClientManager", "info", f"Supabase client connected: {connected}")
        return connected
