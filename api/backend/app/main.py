# app/main.py
"""
==============================================
    Constellation API Documentation
==============================================

**Version:** 1.0.0  
**Port:** 8081

**Description:**  
The Constellation API is a FastAPI-based application designed to manage pipelines, blocks, edges, and audit logs. It supports comprehensive CRUD operations and advanced search functionalities based on various taxonomies and classifications. The API leverages Supabase's RESTful capabilities for efficient data management and querying.

**Table of Contents:**
1. [Getting Started](#getting-started)
2. [API Endpoints](#api-endpoints)
    - [Root & Health Check](#root--health-check)
    - [Pipelines](#pipelines)
    - [Blocks](#blocks)
    - [Edges](#edges)
    - [Audit Logs](#audit-logs)
3. [Running the Application](#running-the-application)
4. [Logging](#logging)
5. [Shutdown](#shutdown)

**API Endpoints:**

- **Root Endpoint:**  
  `GET /`  
  Returns a welcome message.

- **Health Check:**  
  `GET /health`  
  Checks the health status of the API.

- **Pipelines:**  
  CRUD operations for managing pipelines.  
  - `POST /pipelines/`  
  - `GET /pipelines/{pipeline_id}`  
  - `PUT /pipelines/{pipeline_id}`  
  - `DELETE /pipelines/{pipeline_id}`  
  - `GET /pipelines/`  
  - `POST /pipelines/search/`  
  - `POST /pipelines/{pipeline_id}/assign-version/`  

- **Blocks:**  
  CRUD operations for managing blocks.  
  - `POST /blocks/`  
  - `GET /blocks/{block_id}`  
  - `PUT /blocks/{block_id}`  
  - `DELETE /blocks/{block_id}`  
  - `GET /blocks/`  
  - `GET /blocks/search/`  
  - `POST /blocks/{block_id}/assign-version/`  

- **Edges:**  
  CRUD operations for managing edges.  
  - `POST /edges/`  
  - `GET /edges/{edge_id}`  
  - `PUT /edges/{edge_id}`  
  - `DELETE /edges/{edge_id}`  
  - `GET /edges/`  
  - `GET /edges/search/`  
  - `POST /edges/{edge_id}/assign-version/`  

- **Audit Logs:**  
  CRUD operations for managing audit logs.  
  - `POST /audit-logs/`  
  - `GET /audit-logs/{log_id}`  
  - `PUT /audit-logs/{log_id}`  
  - `DELETE /audit-logs/{log_id}`  
  - `GET /audit-logs/`  

"""

import uvicorn
from fastapi import FastAPI, HTTPException
from backend.app.features.core.routes import blocks, edges, pipelines, audit_logs, users
from backend.app.utils.helpers import SupabaseClientManager
from backend.app.logger import ConstellationLogger
from backend.app.database import get_supabase_client
from backend.app.config import settings

# Initialize the logger
logger = ConstellationLogger()

# Initialize the Supabase client manager
supabase_manager = SupabaseClientManager()
supabase_manager.connect()

# Create the FastAPI application instance with Lifespan context manager
app = FastAPI(
    title="Constellation API",
    description="API for managing Users, Blocks, Edges, Pipelines, and Audit Logs.",
    version="1.0.0",
)

# Include all the API routers
app.include_router(blocks.router)
app.include_router(edges.router)
app.include_router(pipelines.router)
app.include_router(audit_logs.router)
app.include_router(users.router)


@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint that returns a welcome message.

    Returns:
    dict: A dictionary containing a welcome message.
    """
    return {"message": "Welcome to the Constellation API!"}


@app.get("/health", tags=["Health Check"])
async def health_check():
    """
    Health check endpoint to verify the application's connectivity with Supabase.

    Returns:
    dict: A dictionary containing the health status.
    """
    try:
        if supabase_manager._initialized:
            return {"status": "healthy"}
        else:
            raise HTTPException(
                status_code=503, detail="Supabase backend is unreachable."
            )
    except Exception as e:
        logger.log("main", "critical", f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error.")


def main():
    """
    Main function to launch the FastAPI application using Uvicorn.
    The API will be accessible at http://localhost:8081
    """
    logger.log("main", "info", "Starting Constellation API on port 8081.")
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8081,
        reload=True,
        log_level="info",
    )


if __name__ == "__main__":
    main()
