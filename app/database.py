# app/database.py

from app.utils.helpers import supabase_manager
from app.config import settings

def get_supabase_client():
    """
    Get the Supabase client instance.
    
    Returns:
        Client: The Supabase client for interacting with the backend.
    """
    return supabase_manager.get_client()

def get_supabase_admin_client():
    """
    Get the Supabase admin client instance.
    
    Returns:
        Client: The Supabase client with admin access.
    """
    # Note: You might need to implement this in SupabaseClientManager
    # if you need different credentials for admin access
    return supabase_manager.get_client()

if __name__ == "__main__":
    print("Testing Supabase connection...")
    try:
        client = get_supabase_client()
        print(f"Supabase client retrieved successfully: {client}")
        
        if client:
            # List all tables
            response = client.table('blocks').select('*').limit(1).execute()
            print("\nSuccessfully connected to Supabase.")
            print(f"Data from 'blocks' table: {response.data}")

            # List all tables in the public schema
            schema = client.table('').select('*').execute()
            print("\nAvailable tables:")
            for table in schema.data['definitions'].keys():
                print(f"- {table}")
        
            # Test admin client
            admin_client = get_supabase_admin_client()
            print(f"\nSupabase admin client retrieved successfully: {admin_client}")
        else:
            print("Failed to retrieve Supabase client.")
        
    except Exception as e:
        print(f"Error connecting to Supabase: {e}")
