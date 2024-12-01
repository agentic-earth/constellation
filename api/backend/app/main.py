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
  - `POST /pipelines/with-dependencies/`
  - `DELETE /pipelines/with-dependencies/{pipeline_id}`
  - `POST /pipelines/verify/{pipeline_id}`

- **Blocks:**  
  CRUD operations for managing blocks.  
  - `POST /blocks/`  
  - `GET /blocks/{block_id}`  
  - `PUT /blocks/{block_id}`  
  - `DELETE /blocks/{block_id}`  
  - `POST /blocks/search-by-filters/`  
  - `POST /blocks/search-by-vector/`

- **Edges:**  
  CRUD operations for managing edges.  
  - `POST /edges/`  
  - `GET /edges/{edge_id}`  
  - `PUT /edges/{edge_id}`  
  - `DELETE /edges/{edge_id}`  
  - `GET /edges/`  
  - `POST /edges/search-by-filters/`  
  - `POST /edges/search-by-vector/`   

"""

# main.py

import uvicorn
from fastapi import FastAPI, HTTPException
from backend.app.features.core.routes import blocks, edges, pipelines
from backend.app.database import connect_db, disconnect_db, prisma_client
from backend.app.logger import ConstellationLogger
# from backend.app.utils.helpers import SupabaseClientManager
from fastapi.middleware.cors import CORSMiddleware

logger = ConstellationLogger()

app = FastAPI(
    title="Constellation API",
    description="API for managing Users, Blocks, Edges, Pipelines, and Audit Logs.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def on_startup():
    await connect_db()

@app.on_event("shutdown")
async def on_shutdown():
    await disconnect_db()


# Include all the API routers
app.include_router(blocks.router, prefix="/blocks", tags=["Blocks"])
app.include_router(edges.router, prefix="/edges", tags=["Edges"])
app.include_router(pipelines.router, prefix="/pipelines", tags=["Pipelines"])
# app.include_router(users.router, prefix="/users", tags=["Users"])

@app.get("/", tags=["Root"])
async def root():
    return {"message": "Welcome to the Constellation API!"}

@app.get("/database_stats")
async def get_database_stats():
    return {"status": "ok"}

@app.get("/info")
async def get_info():
    return {"status": "ok"}

@app.get("/ping")
async def ping():
    return {"status": "pong"}

@app.get("/health", tags=["Health Check"])
async def health_check():
    try:
        # Simple query to check database connectivity
        result = prisma_client.is_connected()
        if result:
            return {"status": "healthy"}
        else:
            raise HTTPException(
                status_code=503, detail="Database query failed."
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
        "api.backend.app.main:app",
        host="0.0.0.0",
        port=8081,
        reload=True,
        log_level="info",
    )


if __name__ == "__main__":
    main()
