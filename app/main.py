# app/main.py

from fastapi import FastAPI, HTTPException
from app.routes import users, blocks, edges, pipelines, audit_logs
from app.utils.helpers import SupabaseClientManager
from app.logger import ConstellationLogger
from app.database import get_supabase_client
from app.config import settings

# Initialize the logger
logger = ConstellationLogger()

# Initialize the Supabase client manager
supabase_manager = SupabaseClientManager()

# Create the FastAPI application instance
app = FastAPI(
    title="Hybrid Model Application API",
    description="API for managing Users, Blocks, Edges, Pipelines, and Audit Logs.",
    version="1.0.0",
)

# Include all the API routers
app.include_router(users.router)
app.include_router(blocks.router)
app.include_router(edges.router)
app.include_router(pipelines.router)
app.include_router(audit_logs.router)

@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint that returns a welcome message.
    
    Returns:
        dict: A dictionary containing a welcome message.
    """
    return {"message": "Welcome to the Hybrid Model Application API!"}

@app.get("/health", tags=["Health Check"])
async def health_check():
    """
    Health check endpoint to verify the application's connectivity with Supabase.
    
    Returns:
        dict: A dictionary containing the health status.
    """
    try:
        if supabase_manager.check_health():
            return {"status": "healthy"}
        else:
            raise HTTPException(status_code=503, detail="Supabase backend is unreachable.")
    except Exception as e:
        logger.log("main", "critical", f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error.")

@app.on_event("startup")
async def startup_event():
    """
    Event handler that runs on application startup.
    
    Ensures that the Supabase client is connected and logs the event.
    """
    if supabase_manager.is_connected():
        logger.log("main", "info", "Application startup successful. Supabase client is connected.")
    else:
        logger.log("main", "critical", "Application startup failed. Supabase client is not connected.")
        raise RuntimeError("Supabase client is not connected.")

@app.on_event("shutdown")
async def shutdown_event():
    """
    Event handler that runs on application shutdown.
    
    Disconnects the Supabase client and logs the event.
    """
    supabase_manager.disconnect()
    logger.log("main", "info", "Application shutdown. Supabase client disconnected.")
