# 🛠️ Building a Hybrid Python API with Supabase-py 🐍🚀

Welcome to the **Hybrid Model Application** setup guide! This document outlines the comprehensive directory structure, necessary packages, and initial setup steps to integrate a custom Python API with Supabase. Our goal is to leverage Supabase's robust REST API for standard CRUD operations while implementing custom logic for advanced functionalities like logging and versioning.

## Agentic Intelligence

## 🌟 **Table of Contents**

1. [📁 Project Directory Structure](https://www.notion.so/how-the-backend-is-built-c1638929cc454c57ac9e7485baeef5bc?pvs=21)
2. [🔧 Packages and Technologies](https://www.notion.so/how-the-backend-is-built-c1638929cc454c57ac9e7485baeef5bc?pvs=21)
3. [🛠️ Initial Setup and Installation](https://www.notion.so/how-the-backend-is-built-c1638929cc454c57ac9e7485baeef5bc?pvs=21)
4. [📝 Detailed Component Explanation](https://www.notion.so/how-the-backend-is-built-c1638929cc454c57ac9e7485baeef5bc?pvs=21)
5. [🔗 Example Code Snippets](https://www.notion.so/how-the-backend-is-built-c1638929cc454c57ac9e7485baeef5bc?pvs=21)
6. [🚀 Next Steps](https://www.notion.so/how-the-backend-is-built-c1638929cc454c57ac9e7485baeef5bc?pvs=21)

---

## 1. 📁 **Project Directory Structure**

A well-organized directory structure enhances maintainability, scalability, and collaboration. Below is the proposed structure tailored to our Hybrid Model Application:

```markdown
markdown
Copy code
hybrid_api_project/
├── app/
│ ├── **init**.py
│ ├── main.py
│ ├── config.py
│ ├── models.py
│ ├── schemas.py
│ ├── database.py
│ ├── logger.py
│ ├── utils/
│ │ ├── **init**.py
│ │ └── helpers.py
│ ├── routes/
│ │ ├── **init**.py
│ │ ├── users.py
│ │ ├── blocks.py
│ │ ├── edges.py
│ │ ├── pipelines.py
│ │ └── audit_logs.py
│ └── services/
│ ├── **init**.py
│ ├── user_service.py
│ ├── block_service.py
│ ├── edge_service.py
│ ├── pipeline_service.py
│ └── audit_service.py
├── tests/
│ ├── **init**.py
│ ├── test_users.py
│ ├── test_blocks.py
│ ├── test_edges.py
│ ├── test_pipelines.py
│ └── test_audit_logs.py
├── logs/
│ └── app.log
├── .env
├── requirements.txt
├── Dockerfile
├── README.md
└── setup.py
```

### 📂 **Directory Breakdown**

- **app/**: Core application directory containing all the main components.
  - **main.py**: Entry point of the FastAPI application.
  - **config.py**: Configuration settings, including environment variables.
  - **models.py**: SQLAlchemy models if using ORM; however, with Supabase-py, interactions are direct.
  - **schemas.py**: Pydantic models for data validation.
  - **database.py**: Supabase client initialization and database interaction logic.
  - **logger.py**: Dedicated logging setup accessible across the application.
  - **utils/**: Utility functions and helpers.
  - **routes/**: API route definitions for different entities.
  - **services/**: Business logic and interaction with the database.
- **tests/**: Contains all unit and integration tests.
- **logs/**: Directory to store log files.
- **.env**: Environment variables file (ensure this is added to `.gitignore`).
- **requirements.txt**: Python dependencies.
- **Dockerfile**: Containerization setup for deployment.
- **README.md**: Project documentation.
- **setup.py**: Package setup script for distribution if needed.

---

## 2. 🔧 **Packages and Technologies**

To build a robust and maintainable Hybrid Model Application, the following packages and technologies are recommended:

### 🐍 **Python Packages**

- **FastAPI**: Modern, fast (high-performance) web framework for building APIs with Python.
- **Uvicorn**: Lightning-fast ASGI server for serving FastAPI applications.
- **supabase-py**: Python client for interacting with Supabase services.
- **Pydantic**: Data validation and settings management using Python type annotations.
- **python-dotenv**: Reads key-value pairs from a `.env` file and can set them as environment variables.
- **SQLAlchemy** _(Optional)_: SQL toolkit and ORM for Python, if needed for advanced database interactions.
- **Loguru** or **structlog** _(Optional)_: Advanced logging libraries for more flexible logging capabilities.
- **pytest**: Framework for writing and running tests.
- **requests**: HTTP library for making API requests (if needed).
- **Alembic** _(Optional)_: Database migrations tool if using SQLAlchemy.

### 🖥️ **Technologies**

- **Supabase**: Backend-as-a-Service platform providing PostgreSQL database, authentication, and real-time APIs.
- **PostgreSQL**: Relational database management system.
- **Docker**: Containerization platform for deploying applications consistently across environments.
- **Git**: Version control system for tracking changes in source code.
- **Notion**: Collaboration tool for documentation and project management (optional but recommended).

---

## 3. 🛠️ **Initial Setup and Installation**

### 🖥️ **Prerequisites**

- **Python 3.8+**: Ensure Python is installed on your machine.
- **Docker** _(Optional)_: For containerizing the application.
- **Git**: For version control.

### 📦 **Step-by-Step Installation**

1. **Clone the Repository**

   ```bash
   bash
   Copy code
   git clone https://github.com/yourorg/hybrid_api_project.git
   cd hybrid_api_project

   ```

2. **Create a Virtual Environment**

   ```bash
   bash
   Copy code
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

   ```

3. **Create `requirements.txt`**

   Create a `requirements.txt` file with the following content:

   ```
   txt
   Copy code
   fastapi
   uvicorn[standard]
   supabase-py
   pydantic
   python-dotenv
   loguru
   pytest
   requests

   ```

4. **Install Dependencies**

   ```bash
   bash
   Copy code
   pip install -r requirements.txt

   ```

5. **Set Up Environment Variables**

   Create a `.env` file in the root directory with the following content:

   ```
   env
   Copy code
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_KEY=your-supabase-service-role-key
   LOG_LEVEL=INFO

   ```

   > Note: Replace your-project.supabase.co and your-supabase-service-role-key with your actual Supabase project URL and service role key. Never expose your service role key in client-side applications.

6. **Initialize Git Repository**

   ```bash
   bash
   Copy code
   git init
   git add .
   git commit -m "Initial commit with project structure and dependencies"

   ```

7. **Docker Setup** _(Optional)_

   If you plan to containerize your application, ensure Docker is installed and build the Docker image.

   ```
   dockerfile
   Copy code
   # Dockerfile
   FROM python:3.11-slim

   # Set environment variables
   ENV PYTHONDONTWRITEBYTECODE=1
   ENV PYTHONUNBUFFERED=1

   # Set work directory
   WORKDIR /code

   # Install dependencies
   COPY requirements.txt .
   RUN pip install --upgrade pip
   RUN pip install -r requirements.txt

   # Copy project
   COPY . .

   # Expose port
   EXPOSE 8000

   # Run the application
   CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

   ```

   Build and run the Docker container:

   ```bash
   bash
   Copy code
   docker build -t hybrid_api_project .
   docker run -d -p 8000:8000 hybrid_api_project

   ```

---

## 4. 📝 **Detailed Component Explanation**

### 🧰 **Core Components**

1. **Configuration (`config.py`)**

   Manages environment variables and configuration settings.

   ```python
   python
   Copy code
   # app/config.py
   from pydantic import BaseSettings

   class Settings(BaseSettings):
       SUPABASE_URL: str
       SUPABASE_KEY: str
       LOG_LEVEL: str = "INFO"

       class Config:
           env_file = ".env"

   settings = Settings()

   ```

2. **Logger (`logger.py`)**

   Provides a centralized logging mechanism accessible throughout the application.

   ```python
   python
   Copy code
   # app/logger.py
   from loguru import logger
   from app.config import settings
   import sys

   # Configure logger
   logger.remove()  # Remove the default logger
   logger.add(sys.stdout, level=settings.LOG_LEVEL)
   logger.add("logs/app.log", rotation="10 MB", retention="10 days", level=settings.LOG_LEVEL)

   def get_logger():
       return logger

   ```

   > Usage:
   >
   > ```python
   > python
   > Copy code
   > from app.logger import get_logger
   >
   > logger = get_logger()
   > logger.info("This is an info message")
   >
   > ```

3. **Database Interaction (`database.py`)**

   Initializes the Supabase client for database operations.

   ```python
   python
   Copy code
   # app/database.py
   from supabase import create_client, Client
   from app.config import settings
   from app.logger import get_logger

   logger = get_logger()

   supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

   def get_supabase_client() -> Client:
       return supabase

   ```

4. **Schemas (`schemas.py`)**

   Defines Pydantic models for request validation and response formatting.

   ```python
   python
   Copy code
   # app/schemas.py
   from pydantic import BaseModel, EmailStr
   from typing import Optional, List
   from uuid import UUID
   from datetime import datetime

   # User Schemas
   class UserBase(BaseModel):
       username: str
       email: EmailStr
       role: str

   class UserCreate(UserBase):
       password_hash: str

   class UserUpdate(BaseModel):
       username: Optional[str]
       email: Optional[EmailStr]
       role: Optional[str]

   class User(UserBase):
       user_id: UUID
       created_at: datetime
       updated_at: datetime

       class Config:
           orm_mode = True

   # Similar schemas for API_KEYS, BLOCKS, BLOCK_VERSIONS, etc.

   ```

5. **Routes (`routes/`)**

   Contains API route definitions for different entities like Users, Blocks, Edges, etc.

   ```python
   python
   Copy code
   # app/routes/users.py
   from fastapi import APIRouter, HTTPException
   from app.schemas import UserCreate, User, UserUpdate
   from app.services.user_service import create_user_service, get_user_service, update_user_service, delete_user_service
   from uuid import UUID

   router = APIRouter(
       prefix="/users",
       tags=["Users"],
   )

   @router.post("/", response_model=User)
   async def create_user(user: UserCreate):
       created_user = create_user_service(user)
       if not created_user:
           raise HTTPException(status_code=400, detail="User creation failed")
       return created_user

   @router.get("/{user_id}", response_model=User)
   async def get_user(user_id: UUID):
       user = get_user_service(user_id)
       if not user:
           raise HTTPException(status_code=404, detail="User not found")
       return user

   @router.patch("/{user_id}", response_model=User)
   async def update_user(user_id: UUID, user: UserUpdate):
       updated_user = update_user_service(user_id, user)
       if not updated_user:
           raise HTTPException(status_code=404, detail="User not found or no changes made")
       return updated_user

   @router.delete("/{user_id}", response_model=dict)
   async def delete_user(user_id: UUID):
       success = delete_user_service(user_id)
       if not success:
           raise HTTPException(status_code=404, detail="User not found")
       return {"detail": "User deleted successfully"}

   ```

6. **Services (`services/`)**

   Implements the business logic and interacts with the database.

   ```python
   python
   Copy code
   # app/services/user_service.py
   from app.schemas import UserCreate, User, UserUpdate
   from app.database import supabase
   from app.logger import get_logger
   from uuid import UUID
   from typing import Optional

   logger = get_logger()

   def create_user_service(user: UserCreate) -> Optional[User]:
       data = user.dict()
       response = supabase.table("users").insert(data).execute()
       if response.status_code == 201 and response.data:
           logger.info(f"User created: {response.data[0]['user_id']}")
           return User(**response.data[0])
       logger.error("Failed to create user")
       return None

   def get_user_service(user_id: UUID) -> Optional[User]:
       response = supabase.table("users").select("*").eq("user_id", str(user_id)).single().execute()
       if response.status_code == 200 and response.data:
           return User(**response.data)
       logger.warning(f"User not found: {user_id}")
       return None

   def update_user_service(user_id: UUID, user: UserUpdate) -> Optional[User]:
       data = user.dict(exclude_unset=True)
       response = supabase.table("users").update(data).eq("user_id", str(user_id)).execute()
       if response.status_code == 200 and response.data:
           logger.info(f"User updated: {user_id}")
           return User(**response.data[0])
       logger.warning(f"Failed to update user: {user_id}")
       return None

   def delete_user_service(user_id: UUID) -> bool:
       response = supabase.table("users").delete().eq("user_id", str(user_id)).execute()
       if response.status_code == 200 and response.count > 0:
           logger.info(f"User deleted: {user_id}")
           return True
       logger.warning(f"Failed to delete user: {user_id}")
       return False

   ```

7. **Main Application (`main.py`)**

   Integrates all routes and initializes the FastAPI application.

   ```python
   python
   Copy code
   # app/main.py
   from fastapi import FastAPI
   from app.routes import users, blocks, edges, pipelines, audit_logs

   app = FastAPI(
       title="Hybrid Model Application API",
       description="API for managing Blocks, Edges, Pipelines, and more.",
       version="1.0.0",
   )

   # Include routers
   app.include_router(users.router)
   app.include_router(blocks.router)
   app.include_router(edges.router)
   app.include_router(pipelines.router)
   app.include_router(audit_logs.router)

   @app.get("/")
   async def root():
       return {"message": "Welcome to the Hybrid Model Application API!"}

   ```

---

## 5. 🔗 **Example Code Snippets**

### 📝 **Dedicated Logger Implementation**

A centralized logger ensures consistent logging across all modules.

```python
python
Copy code
# app/logger.py
from loguru import logger
from app.config import settings
import sys

# Remove the default logger
logger.remove()

# Add a stdout logger
logger.add(sys.stdout, level=settings.LOG_LEVEL, format="{time} {level} {message}", enqueue=True)

# Add a file logger with rotation and retention
logger.add(
    "logs/app.log",
    rotation="10 MB",
    retention="10 days",
    level=settings.LOG_LEVEL,
    format="{time} {level} {message}",
    enqueue=True
)

def get_logger():
    return logger

```

> Usage Across Any File:

```python
python
Copy code
from app.logger import get_logger

logger = get_logger()

def some_function():
    logger.info("This is an info message")
    logger.error("This is an error message")

```

### 📦 **Supabase Client Setup**

```python
python
Copy code
# app/database.py
from supabase import create_client, Client
from app.config import settings
from app.logger import get_logger

logger = get_logger()

supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

def get_supabase_client() -> Client:
    return supabase

```

### 🔄 **Handling CRUD Operations for Blocks**

```python
python
Copy code
# app/routes/blocks.py
from fastapi import APIRouter, HTTPException
from app.schemas import BlockCreate, Block, BlockUpdate
from app.services.block_service import (
    create_block_service,
    get_block_service,
    update_block_service,
    delete_block_service
)
from uuid import UUID

router = APIRouter(
    prefix="/blocks",
    tags=["Blocks"],
)

@router.post("/", response_model=Block)
async def create_block(block: BlockCreate):
    created_block = create_block_service(block)
    if not created_block:
        raise HTTPException(status_code=400, detail="Block creation failed")
    return created_block

@router.get("/{block_id}", response_model=Block)
async def get_block(block_id: UUID):
    block = get_block_service(block_id)
    if not block:
        raise HTTPException(status_code=404, detail="Block not found")
    return block

@router.patch("/{block_id}", response_model=Block)
async def update_block(block_id: UUID, block: BlockUpdate):
    updated_block = update_block_service(block_id, block)
    if not updated_block:
        raise HTTPException(status_code=404, detail="Block not found or no changes made")
    return updated_block

@router.delete("/{block_id}", response_model=dict)
async def delete_block(block_id: UUID):
    success = delete_block_service(block_id)
    if not success:
        raise HTTPException(status_code=404, detail="Block not found")
    return {"detail": "Block deleted successfully"}

```

---

## 6. 🚀 **Next Steps**

1. **Implement Remaining Routes and Services**:
   - Develop routes and services for **Edges**, **Pipelines**, and **Audit Logs** following the pattern established for **Users** and **Blocks**.
2. **Integrate Logging into All Services**:
   - Ensure that each service logs significant actions, errors, and important state changes.
3. **Handle Versioning Logic**:

   - Implement logic within your services to manage `BLOCK_VERSIONS` and `EDGE_VERSIONS`. For example, when updating a Block, create a new version entry instead of directly modifying the existing one.

   ```python
   python
   Copy code
   # app/services/block_service.py
   from app.schemas import BlockCreate, Block, BlockUpdate
   from app.database import supabase
   from app.logger import get_logger
   from uuid import UUID
   from typing import Optional

   logger = get_logger()

   def create_block_service(block: BlockCreate) -> Optional[Block]:
       data = block.dict()
       response = supabase.table("blocks").insert(data).execute()
       if response.status_code == 201 and response.data:
           logger.info(f"Block created: {response.data[0]['block_id']}")
           return Block(**response.data[0])
       logger.error("Failed to create block")
       return None

   # Similar functions for get, update (with versioning), delete

   ```

4. **Implement Audit Logging**:

   - Use middleware or decorators to automatically log user actions into the `AUDIT_LOGS` table.

   ```python
   python
   Copy code
   # app/middleware/audit_middleware.py
   from fastapi import Request
   from app.logger import get_logger
   from app.database import supabase
   from uuid import UUID
   import json

   logger = get_logger()

   async def audit_middleware(request: Request, call_next):
       response = await call_next(request)
       # Example: Log POST requests to /blocks/
       if request.method == "POST" and request.url.path.startswith("/blocks"):
           user_id = request.headers.get("user_id")  # Assuming user_id is passed in headers
           action_type = "CREATE"
           entity_type = "block"
           entity_id = "extracted from response or request body"
           details = {"method": request.method, "path": request.url.path}
           supabase.table("audit_logs").insert({
               "user_id": user_id,
               "action_type": action_type,
               "entity_type": entity_type,
               "entity_id": entity_id,
               "details": json.dumps(details)
           }).execute()
           logger.info(f"Audit log created for {entity_type}: {entity_id}")
       return response

   ```

   **Integrate Middleware in `main.py`**:

   ```python
   python
   Copy code
   # app/main.py
   from fastapi import FastAPI
   from app.routes import users, blocks, edges, pipelines, audit_logs
   from app.middleware.audit_middleware import audit_middleware

   app = FastAPI(
       title="Hybrid Model Application API",
       description="API for managing Blocks, Edges, Pipelines, and more.",
       version="1.0.0",
   )

   # Include routers
   app.include_router(users.router)
   app.include_router(blocks.router)
   app.include_router(edges.router)
   app.include_router(pipelines.router)
   app.include_router(audit_logs.router)

   # Add middleware
   app.middleware("http")(audit_middleware)

   @app.get("/")
   async def root():
       return {"message": "Welcome to the Hybrid Model Application API!"}

   ```

5. **Testing**

   - Write unit and integration tests for all routes and services to ensure reliability.
   - Use **pytest** for running tests.

   ```python
   python
   Copy code
   # tests/test_users.py
   from fastapi.testclient import TestClient
   from app.main import app

   client = TestClient(app)

   def test_create_user():
       response = client.post(
           "/users/",
           json={
               "username": "johndoe",
               "email": "john.doe@example.com",
               "password_hash": "hashed_password",
               "role": "developer"
           }
       )
       assert response.status_code == 200
       assert response.json()["username"] == "johndoe"

   ```

6. **Deployment**
   - Deploy your application using platforms like **Heroku**, **AWS Elastic Beanstalk**, **Google App Engine**, or container orchestration systems like **Kubernetes**.
   - Ensure environment variables are securely managed in the deployment environment.
7. **Documentation**

   - Maintain comprehensive documentation in **README.md** and use tools like **Swagger UI** (integrated with FastAPI) for interactive API documentation.

   ```markdown
   markdown
   Copy code

   # Hybrid Model Application API

   ## Overview

   This API manages Users, Blocks, Edges, Pipelines, and Audit Logs for the Hybrid Model Application.

   ## Getting Started

   1. Clone the repository
   2. Set up the virtual environment
   3. Install dependencies
   4. Configure environment variables
   5. Run the application

   ## API Documentation

   Access the interactive API docs at `/docs` after running the application.
   ```

---

## 🚀 **Next Steps**

1.  **Finalize All Routes and Services**
    - Complete the implementation of all necessary API routes and corresponding service functions for each entity (Blocks, Edges, Pipelines, etc.).
2.  **Enhance Security**
    - Implement authentication mechanisms such as JWT tokens.
    - Define **Row Level Security (RLS)** policies in Supabase to control data access based on user roles.
3.  **Optimize Performance**
    - Utilize indexing in Supabase for frequently queried fields.
    - Implement caching strategies if necessary.
4.  **Continuous Integration and Deployment (CI/CD)** - Set up CI/CD pipelines

        ```mermaid

    erDiagram
    %% Entities
    USERS {
    UUID user_id PK "Primary Key"
    String username "Unique Username"
    String email "User Email Address"
    String password_hash "Hashed Password"
    String role "User Role (e.g., admin, developer)"
    Timestamp created_at "Record Creation Timestamp"
    Timestamp updated_at "Record Update Timestamp"
    }

        API_KEYS {
            UUID api_key_id PK "Primary Key"
            UUID user_id FK "Foreign Key to USERS"
            String encrypted_api_key "Encrypted API Key"
            Timestamp created_at "Record Creation Timestamp"
            Timestamp expires_at "API Key Expiration Timestamp"
            Boolean is_active "API Key Active Status"
        }

        BLOCKS {
            UUID block_id PK "Primary Key"
            String name "Unique Block Name"
            Enum block_type "Values: 'dataset', 'model'"
            Text description "Block Description"
            Timestamp created_at "Record Creation Timestamp"
            Timestamp updated_at "Record Update Timestamp"
            UUID current_version_id FK "Foreign Key to BLOCK_VERSIONS"
        }

        BLOCK_VERSIONS {
            UUID version_id PK "Primary Key"
            UUID block_id FK "Foreign Key to BLOCKS"
            Integer version_number "Sequential Version Number"
            JSONB metadata "Version-specific Metadata"
            Timestamp created_at "Version Creation Timestamp"
            UUID created_by FK "Foreign Key to USERS"
            Boolean is_active "Active Version Indicator"
        }

        TAXONOMY_CATEGORIES {
            UUID category_id PK "Primary Key"
            String name "Category Name"
            UUID parent_id FK "Self-referencing Foreign Key for Hierarchy"
            Timestamp created_at "Record Creation Timestamp"
            Timestamp updated_at "Record Update Timestamp"
        }

        BLOCK_TAXONOMIES {
            UUID block_taxonomy_id PK "Primary Key"
            UUID block_id FK "Foreign Key to BLOCKS"
            UUID category_id FK "Foreign Key to TAXONOMY_CATEGORIES"
            Timestamp created_at "Association Creation Timestamp"
        }

        CODE_REPOS {
            UUID repo_id PK "Primary Key"
            Enum entity_type "Values: 'block', 'edge'"
            UUID entity_id "References BLOCKS or EDGES based on entity_type"
            String repo_url "GitHub Repository URL"
            String branch "Default Branch (e.g., 'main')"
            Timestamp last_updated "Last Repository Update Timestamp"
        }

        DOCKER_IMAGES {
            UUID image_id PK "Primary Key"
            Enum entity_type "Values: 'block', 'edge'"
            UUID entity_id "References BLOCKS or EDGES based on entity_type"
            String image_tag "Docker Image Tag (e.g., 'v1.0.0')"
            String registry_url "Docker Registry URL"
            Enum build_status "Values: 'pending', 'success', 'failed'"
            Text build_logs "Build Logs for Docker Image"
            Timestamp created_at "Image Creation Timestamp"
            Timestamp updated_at "Image Update Timestamp"
        }

        DEPENDENCIES {
            UUID dependency_id PK "Primary Key"
            Enum entity_type "Values: 'block', 'edge'"
            UUID entity_id "References BLOCKS or EDGES based on entity_type"
            Enum dependency_type "Values: 'internal', 'external'"
            Text dependency_detail "Details about the Dependency"
        }

        EDGES {
            UUID edge_id PK "Primary Key"
            String name "Unique Edge Name"
            Text description "Edge Description"
            UUID current_version_id FK "Foreign Key to EDGE_VERSIONS"
            Timestamp created_at "Record Creation Timestamp"
            Timestamp updated_at "Record Update Timestamp"
        }

        EDGE_VERSIONS {
            UUID version_id PK "Primary Key"
            UUID edge_id FK "Foreign Key to EDGES"
            Integer version_number "Sequential Version Number"
            JSONB metadata "Version-specific Metadata"
            Timestamp created_at "Version Creation Timestamp"
            UUID created_by FK "Foreign Key to USERS"
            Boolean is_active "Active Version Indicator"
        }

        EDGE_VERIFICATIONS {
            UUID verification_id PK "Primary Key"
            UUID edge_version_id FK "Foreign Key to EDGE_VERSIONS"
            Enum verification_status "Values: 'pending', 'passed', 'failed'"
            Text verification_logs "Logs from Verification Process"
            Timestamp verified_at "Verification Completion Timestamp"
            UUID verified_by FK "Foreign Key to USERS"
            Timestamp created_at "Verification Record Creation Timestamp"
            Timestamp updated_at "Verification Record Update Timestamp"
        }

        PIPELINES {
            UUID pipeline_id PK "Primary Key"
            String name "Unique Pipeline Name"
            Text description "Pipeline Description"
            Timestamp created_at "Record Creation Timestamp"
            Timestamp updated_at "Record Update Timestamp"
            JSONB dagster_pipeline_config "Dagster-specific Configuration"
            UUID created_by FK "Foreign Key to USERS"
            Integer times_run "Total Times Pipeline has Run"
            Float average_runtime "Average Runtime of Pipeline Executions"
        }

        PIPELINE_BLOCKS {
            UUID pipeline_block_id PK "Primary Key"
            UUID pipeline_id FK "Foreign Key to PIPELINES"
            UUID block_id FK "Foreign Key to BLOCKS"
            Timestamp created_at "Association Creation Timestamp"
            Timestamp updated_at "Association Update Timestamp"
        }

        PIPELINE_EDGES {
            UUID pipeline_edge_id PK "Primary Key"
            UUID pipeline_id FK "Foreign Key to PIPELINES"
            UUID edge_id FK "Foreign Key to EDGES"
            UUID source_block_id FK "Foreign Key to BLOCKS (Source)"
            UUID target_block_id FK "Foreign Key to BLOCKS (Target)"
            Timestamp created_at "Association Creation Timestamp"
            Timestamp updated_at "Association Update Timestamp"
        }

        BLOCK_VECTOR_REPRESENTATIONS {
            UUID vector_id PK "Primary Key"
            UUID block_id FK "Foreign Key to BLOCKS"
            String vector_db "Vector Database Name (e.g., Pinecone)"
            String vector_key "Identifier in Vector Database"
            JSONB taxonomy_filter "Taxonomy Constraints for RAG Search"
            Timestamp created_at "Record Creation Timestamp"
            Timestamp updated_at "Record Update Timestamp"
        }

        EDGE_VECTOR_REPRESENTATIONS {
            UUID vector_id PK "Primary Key"
            UUID edge_id FK "Foreign Key to EDGES"
            String vector_db "Vector Database Name (e.g., Pinecone)"
            String vector_key "Identifier in Vector Database"
            JSONB taxonomy_filter "Taxonomy Constraints for RAG Search"
            Timestamp created_at "Record Creation Timestamp"
            Timestamp updated_at "Record Update Timestamp"
        }

        AUDIT_LOGS {
            UUID log_id PK "Primary Key"
            UUID user_id FK "Foreign Key to USERS"
            Enum action_type "Values: 'CREATE', 'READ', 'UPDATE', 'DELETE'"
            Enum entity_type "Values: 'block', 'edge', 'pipeline', 'taxonomy', 'metadata', 'user', 'api_key', 'code_repo', 'docker_image', 'verification'"
            UUID entity_id "ID of the Affected Entity"
            Timestamp timestamp "Action Timestamp"
            JSONB details "Additional Details About the Action"
        }

        %% Relationships
        USERS ||--o{ API_KEYS : "has"
        USERS ||--o{ BLOCK_VERSIONS : "created_by"
        USERS ||--o{ EDGE_VERSIONS : "created_by"
        USERS ||--o{ PIPELINES : "created_by"
        USERS ||--o{ EDGE_VERIFICATIONS : "verified_by"

        BLOCKS ||--o{ BLOCK_VERSIONS : "has"
        BLOCKS ||--o{ BLOCK_TAXONOMIES : "categorized_in"
        BLOCKS ||--o{ CODE_REPOS : "has"
        BLOCKS ||--o{ DOCKER_IMAGES : "has"
        BLOCKS ||--o{ DEPENDENCIES : "has"
        BLOCKS ||--o{ BLOCK_VECTOR_REPRESENTATIONS : "has"
        BLOCKS ||--o{ PIPELINE_BLOCKS : "included_in"

        TAXONOMY_CATEGORIES ||--o{ BLOCK_TAXONOMIES : "categorizes"

        EDGES ||--o{ EDGE_VERSIONS : "has"
        EDGES ||--o{ CODE_REPOS : "has"
        EDGES ||--o{ DOCKER_IMAGES : "has"
        EDGES ||--o{ DEPENDENCIES : "has"
        EDGES ||--o{ EDGE_VERIFICATIONS : "has"
        EDGES ||--o{ EDGE_VECTOR_REPRESENTATIONS : "has"
        EDGES ||--o{ PIPELINE_EDGES : "included_in"

        PIPELINES ||--o{ PIPELINE_BLOCKS : "includes"
        PIPELINES ||--o{ PIPELINE_EDGES : "includes"

        PIPELINE_BLOCKS ||--|| BLOCKS : "references"
        PIPELINE_EDGES ||--|| EDGES : "references"
        PIPELINE_EDGES ||--|| BLOCKS : "source_block_id"
        PIPELINE_EDGES ||--|| BLOCKS : "target_block_id"

        BLOCK_VECTOR_REPRESENTATIONS ||--|| BLOCKS : "references_block"
        EDGE_VECTOR_REPRESENTATIONS ||--|| EDGES : "references_edge"

        AUDIT_LOGS ||--|| USERS : "performed_by"

````

[how the backend is built ](https://www.notion.so/how-the-backend-is-built-c1638929cc454c57ac9e7485baeef5bc?pvs=21)

# 🗂️ Comprehensive Database Schema Guide 📚

Welcome to the **Database Schema Guide** for our project! This document is designed to help all team members understand the structure, components, and functionalities of our database. Whether you're a developer, designer, or stakeholder, this guide will provide you with the necessary insights to work effectively with our system.

---

## 🌟 **Overview: Understanding the Core Concepts**

In plain English, our database schema is the backbone of our application, organizing and managing the data that powers our system. Here's a simplified breakdown of the key concepts:

- **Users & Authentication**: Managing user accounts, roles, and secure access through API keys.
- **Blocks & Edges**: Representing modular components (Blocks) and their interactions or dependencies (Edges) within our pipelines.
- **Pipelines**: Structured workflows that connect various Blocks and Edges to perform complex tasks.
- **Code Repositories & Docker Images**: Linking our codebase to containerized environments for consistent and scalable deployments.
- **Dependencies**: Tracking relationships and dependencies between different Blocks and Edges to ensure smooth operations.
- **Audit Logs**: Keeping a detailed history of all significant actions for transparency and accountability.

---

## 🔍 **Technical Deep Dive: Detailed Schema Breakdown**

Let's delve into each component of our schema, explaining the tables, their relationships, and the types of data they handle.

### 🧑‍💻 **1. Users & Authentication**

### **📄 USERS Table**

- **Purpose**: Stores information about each user who interacts with the system.
- **Fields**:
    - `user_id` (UUID): Unique identifier for each user.
    - `username` (String): User's unique name.
    - `email` (String): User's email address.
    - `password_hash` (String): Securely hashed password.
    - `role` (String): Defines user roles (e.g., admin, developer).
    - `created_at` (Timestamp): When the user account was created.
    - `updated_at` (Timestamp): When the user account was last updated.

### **🔑 API_KEYS Table**

- **Purpose**: Manages API keys for secure interactions with our system.
- **Fields**:
    - `api_key_id` (UUID): Unique identifier for each API key.
    - `user_id` (UUID): Links the API key to a specific user.
    - `encrypted_api_key` (String): The secure API key.
    - `created_at` (Timestamp): When the API key was created.
    - `expires_at` (Timestamp): When the API key will expire.
    - `is_active` (Boolean): Status of the API key (active/inactive).

---

### 🧱 **2. Blocks & Versions**

### **🧩 BLOCKS Table**

- **Purpose**: Represents modular components in our system, such as datasets or models.
- **Fields**:
    - `block_id` (UUID): Unique identifier for each block.
    - `name` (String): Unique name of the block.
    - `block_type` (Enum: 'dataset', 'model'): Type of the block.
    - `description` (Text): Detailed description of the block.
    - `created_at` (Timestamp): When the block was created.
    - `updated_at` (Timestamp): When the block was last updated.
    - `current_version_id` (UUID): Links to the latest version of the block.

### **📦 BLOCK_VERSIONS Table**

- **Purpose**: Tracks different versions of each block to manage updates and changes.
- **Fields**:
    - `version_id` (UUID): Unique identifier for each block version.
    - `block_id` (UUID): Links to the corresponding block.
    - `version_number` (Integer): Sequential number indicating the version.
    - `metadata` (JSONB): Additional data related to the version.
    - `created_at` (Timestamp): When the version was created.
    - `created_by` (UUID): User who created the version.
    - `is_active` (Boolean): Indicates if this version is currently active.

---

### 🔗 **3. Edges & Verifications**

### **🔗 EDGES Table**

- **Purpose**: Defines interactions or dependencies between different blocks within pipelines.
- **Fields**:
    - `edge_id` (UUID): Unique identifier for each edge.
    - `name` (String): Unique name of the edge.
    - `description` (Text): Detailed description of the edge.
    - `current_version_id` (UUID): Links to the latest version of the edge.
    - `created_at` (Timestamp): When the edge was created.
    - `updated_at` (Timestamp): When the edge was last updated.

### **🔍 EDGE_VERIFICATIONS Table**

- **Purpose**: Ensures that each edge version is functioning correctly before being used in pipelines.
- **Fields**:
    - `verification_id` (UUID): Unique identifier for each verification record.
    - `edge_version_id` (UUID): Links to the specific edge version being verified.
    - `verification_status` (Enum: 'pending', 'passed', 'failed'): Status of the verification.
    - `verification_logs` (Text): Logs detailing the verification process.
    - `verified_at` (Timestamp): When the verification was completed.
    - `verified_by` (UUID): User who performed the verification.
    - `created_at` (Timestamp): When the verification record was created.
    - `updated_at` (Timestamp): When the verification record was last updated.

---

### 🛠️ **4. Code Repositories & Docker Images**

### **📂 CODE_REPOS Table**

- **Purpose**: Links our Blocks and Edges to their respective code repositories, ensuring consistent and version-controlled deployments.
- **Fields**:
    - `repo_id` (UUID): Unique identifier for each code repository.
    - `entity_type` (Enum: 'block', 'edge'): Specifies whether the repository is for a block or an edge.
    - `entity_id` (UUID): Links to the corresponding block or edge.
    - `repo_url` (String): URL of the GitHub repository.
    - `branch` (String): Default branch of the repository (e.g., 'main').
    - `last_updated` (Timestamp): When the repository was last updated.

### **🐳 DOCKER_IMAGES Table**

- **Purpose**: Manages Docker images associated with Blocks and Edges, facilitating consistent environments for execution.
- **Fields**:
    - `image_id` (UUID): Unique identifier for each Docker image.
    - `entity_type` (Enum: 'block', 'edge'): Specifies whether the image is for a block or an edge.
    - `entity_id` (UUID): Links to the corresponding block or edge.
    - `image_tag` (String): Tag for the Docker image (e.g., 'v1.0.0').
    - `registry_url` (String): URL of the Docker registry where the image is stored.
    - `build_status` (Enum: 'pending', 'success', 'failed'): Status of the Docker image build process.
    - `build_logs` (Text): Logs from the Docker image build process.
    - `created_at` (Timestamp): When the Docker image was created.
    - `updated_at` (Timestamp): When the Docker image was last updated.

---

### 📈 **5. Dependencies & Taxonomy**

### **🔗 DEPENDENCIES Table**

- **Purpose**: Tracks the relationships and dependencies between different Blocks and Edges, enabling comprehensive impact analysis.
- **Fields**:
    - `dependency_id` (UUID): Unique identifier for each dependency.
    - `entity_type` (Enum: 'block', 'edge'): Specifies whether the dependency is for a block or an edge.
    - `entity_id` (UUID): Links to the corresponding block or edge.
    - `dependency_type` (Enum: 'internal', 'external'): Type of dependency.
    - `dependency_detail` (Text): Detailed information about the dependency.

### **🗂️ TAXONOMY_CATEGORIES Table**

- **Purpose**: Organizes Blocks into hierarchical categories for efficient classification and retrieval.
- **Fields**:
    - `category_id` (UUID): Unique identifier for each taxonomy category.
    - `name` (String): Name of the category.
    - `parent_id` (UUID): References the parent category, enabling hierarchical structures.
    - `created_at` (Timestamp): When the category was created.
    - `updated_at` (Timestamp): When the category was last updated.

### **📚 BLOCK_TAXONOMIES Table**

- **Purpose**: Associates Blocks with their respective taxonomy categories.
- **Fields**:
    - `block_taxonomy_id` (UUID): Unique identifier for each taxonomy association.
    - `block_id` (UUID): Links to the corresponding block.
    - `category_id` (UUID): Links to the corresponding taxonomy category.
    - `created_at` (Timestamp): When the association was created.

---

### 🔄 **6. Pipelines & Their Components**

### **🚀 PIPELINES Table**

- **Purpose**: Defines the workflows that connect various Blocks and Edges to perform complex tasks.
- **Fields**:
    - `pipeline_id` (UUID): Unique identifier for each pipeline.
    - `name` (String): Unique name of the pipeline.
    - `description` (Text): Detailed description of the pipeline.
    - `created_at` (Timestamp): When the pipeline was created.
    - `updated_at` (Timestamp): When the pipeline was last updated.
    - `dagster_pipeline_config` (JSONB): Configuration specific to Dagster (our pipeline orchestration tool).
    - `created_by` (UUID): User who created the pipeline.
    - `times_run` (Integer): Number of times the pipeline has been executed.
    - `average_runtime` (Float): Average runtime of the pipeline executions.

### **🔗 PIPELINE_BLOCKS Table**

- **Purpose**: Links Blocks to Pipelines, defining which Blocks are part of which Pipelines.
- **Fields**:
    - `pipeline_block_id` (UUID): Unique identifier for each pipeline-block association.
    - `pipeline_id` (UUID): Links to the corresponding pipeline.
    - `block_id` (UUID): Links to the corresponding block.
    - `created_at` (Timestamp): When the association was created.
    - `updated_at` (Timestamp): When the association was last updated.

### **🔗 PIPELINE_EDGES Table**

- **Purpose**: Links Edges to Pipelines, defining how different Blocks interact within Pipelines.
- **Fields**:
    - `pipeline_edge_id` (UUID): Unique identifier for each pipeline-edge association.
    - `pipeline_id` (UUID): Links to the corresponding pipeline.
    - `edge_id` (UUID): Links to the corresponding edge.
    - `source_block_id` (UUID): Block where the edge starts.
    - `target_block_id` (UUID): Block where the edge ends.
    - `created_at` (Timestamp): When the association was created.
    - `updated_at` (Timestamp): When the association was last updated.

---

### 🧬 **7. Vector Representations**

### **🔮 BLOCK_VECTOR_REPRESENTATIONS Table**

- **Purpose**: Stores vector representations of Blocks for advanced search and retrieval using technologies like RAG (Retrieval-Augmented Generation).
- **Fields**:
    - `vector_id` (UUID): Unique identifier for each vector representation.
    - `block_id` (UUID): Links to the corresponding block.
    - `vector_db` (String): Name of the vector database (e.g., Pinecone).
    - `vector_key` (String): Identifier in the vector database.
    - `taxonomy_filter` (JSONB): Constraints based on taxonomy for search operations.
    - `created_at` (Timestamp): When the vector representation was created.
    - `updated_at` (Timestamp): When the vector representation was last updated.

### **🔮 EDGE_VECTOR_REPRESENTATIONS Table**

- **Purpose**: Stores vector representations of Edges for advanced search and retrieval.
- **Fields**:
    - `vector_id` (UUID): Unique identifier for each vector representation.
    - `edge_id` (UUID): Links to the corresponding edge.
    - `vector_db` (String): Name of the vector database (e.g., Pinecone).
    - `vector_key` (String): Identifier in the vector database.
    - `taxonomy_filter` (JSONB): Constraints based on taxonomy for search operations.
    - `created_at` (Timestamp): When the vector representation was created.
    - `updated_at` (Timestamp): When the vector representation was last updated.

---

### 📝 **8. Audit Logs**

### **🕵️‍♂️ AUDIT_LOGS Table**

- **Purpose**: Maintains a detailed history of all significant actions performed within the system for transparency and accountability.
- **Fields**:
    - `log_id` (UUID): Unique identifier for each audit log entry.
    - `user_id` (UUID): Links to the user who performed the action.
    - `action_type` (Enum: 'CREATE', 'READ', 'UPDATE', 'DELETE'): Type of action performed.
    - `entity_type` (Enum: 'block', 'edge', 'pipeline', 'taxonomy', 'metadata', 'user', 'api_key', 'code_repo', 'docker_image', 'verification'): Type of entity affected by the action.
    - `entity_id` (UUID): Identifier of the affected entity.
    - `timestamp` (Timestamp): When the action was performed.
    - `details` (JSONB): Additional details about the action.

---

## 🔌 **API Interactions: How to Make Requests**

Our database is hosted on **Supabase**, which provides a powerful and secure way to interact with your data via APIs. Supabase automatically generates RESTful APIs based on your database schema, making it easy to perform CRUD (Create, Read, Update, Delete) operations.

### 🛠️ **Setting Up Supabase for API Access**

1. **Obtain Supabase Credentials**:
    - Navigate to your Supabase project dashboard.
    - Go to **Settings > API** to find your API URL and `anon` public key.
2. **Configure Supabase Client**:
    - Use Supabase's client libraries (available in JavaScript, Python, etc.) to interact with the API.
    - **Example in Python**:

        ```python
        python
        Copy code
        from supabase import create_client, Client

        url: str = "https://your-project.supabase.co"
        key: str = "your-anon-public-key"
        supabase: Client = create_client(url, key)

        ```


### 📬 **Making API Requests**

Supabase's APIs follow standard REST conventions. Below are examples of how to perform CRUD operations using both **HTTP requests** and **Python**.

### 📥 **Create (Insert) Data**

- **HTTP Request**:

    ```
    http
    Copy code
    POST https://your-project.supabase.co/rest/v1/users
    Content-Type: application/json
    apikey: your-anon-public-key

    {
        "username": "johndoe",
        "email": "john.doe@example.com",
        "password_hash": "hashed_password",
        "role": "developer"
    }

    ```

- **Python Example**:

    ```python
    python
    Copy code
    data = {
        "username": "johndoe",
        "email": "john.doe@example.com",
        "password_hash": "hashed_password",
        "role": "developer"
    }

    response = supabase.table("users").insert(data).execute()
    print(response)

    ```


### 📖 **Read (Select) Data**

- **HTTP Request**:

    ```
    http
    Copy code
    GET https://your-project.supabase.co/rest/v1/users?email=eq.john.doe@example.com
    apikey: your-anon-public-key

    ```

- **Python Example**:

    ```python
    python
    Copy code
    response = supabase.table("users").select("*").eq("email", "john.doe@example.com").execute()
    print(response.data)

    ```


### ✏️ **Update Data**

- **HTTP Request**:

    ```
    http
    Copy code
    PATCH https://your-project.supabase.co/rest/v1/users?user_id=eq.uuid-of-user
    Content-Type: application/json
    apikey: your-anon-public-key

    {
        "role": "admin"
    }

    ```

- **Python Example**:

    ```python
    python
    Copy code
    data = {
        "role": "admin"
    }

    response = supabase.table("users").update(data).eq("user_id", "uuid-of-user").execute()
    print(response)

    ```


### 🗑️ **Delete Data**

- **HTTP Request**:

    ```
    http
    Copy code
    DELETE https://your-project.supabase.co/rest/v1/users?user_id=eq.uuid-of-user
    apikey: your-anon-public-key

    ```

- **Python Example**:

    ```python
    python
    Copy code
    response = supabase.table("users").delete().eq("user_id", "uuid-of-user").execute()
    print(response)

    ```


---

### 🔐 **Security Best Practices**

- **Authentication**: Use Supabase's authentication mechanisms to secure your API endpoints.
- **Row Level Security (RLS)**: Enable RLS to enforce fine-grained access controls based on user roles and permissions.
    - **Example**:

        ```sql
        sql
        Copy code
        -- Enable RLS on the users table
        ALTER TABLE users ENABLE ROW LEVEL SECURITY;

        -- Create a policy that allows users to select their own data
        CREATE POLICY "Allow users to view their own data" ON users
            FOR SELECT
            USING (auth.uid() = user_id);

        -- Similarly, define policies for other tables based on your security requirements

        ```

- **Encrypted Connections**: Ensure all API requests are made over HTTPS to encrypt data in transit.
- **API Keys Management**: Keep your `anon` and `service_role` keys secure. Do not expose the `service_role` key in client-side code.

---

## 🛡️ **How This Works on Supabase**

Supabase acts as a backend-as-a-service platform that provides:

- **Database Management**: Uses PostgreSQL for robust and scalable data storage.
- **Authentication**: Secure user authentication and authorization mechanisms.
- **Auto-generated APIs**: Automatically creates RESTful APIs based on your database schema.
- **Real-time Capabilities**: Supports real-time subscriptions for live data updates.
- **Storage**: Manages file storage if needed.

### 🔧 **Key Features Leveraged**

- **PostgREST**: Powers the RESTful APIs, translating HTTP requests into SQL queries.
- **Row Level Security (RLS)**: Ensures data access is controlled and secure.
- **Extensions**: Utilizes PostgreSQL extensions like `uuid-ossp` for UUID generation.

---

## 📊 **Additional Tips for Developers**

1. **Testing API Endpoints**:
    - Use tools like **Postman** or **Insomnia** to test your API endpoints before integrating them into your application.
2. **Handling Relationships**:
    - When retrieving data with relationships, use Supabase's **foreign table embedding**.
    - **Example**:

        ```python
        python
        Copy code
        response = supabase.table("blocks").select("*, block_versions(*), block_taxonomies(*)").execute()
        print(response.data)

        ```

3. **Optimizing Performance**:
    - **Indexing**: Ensure that frequently queried fields are indexed to speed up read operations.
    - **Pagination**: Implement pagination for endpoints that return large datasets to improve performance and reduce load.
4. **Error Handling**:
    - Always handle potential errors gracefully in your application code to provide a smooth user experience.
    - **Example in Python**:

        ```python
        python
        Copy code
        try:
            response = supabase.table("users").insert(data).execute()
        except Exception as e:
            print(f"Error inserting data: {e}")

        ```

5. **Documentation & Collaboration**:
    - Maintain up-to-date documentation of your database schema and API endpoints.
    - Use collaborative tools like **Notion** to keep the team informed and aligned.

---

## 🛠️ **Conclusion**

Our comprehensive database schema is meticulously designed to support robust, scalable, and secure operations within our application. By understanding each component and leveraging Supabase's powerful features, we can ensure efficient data management, seamless integrations, and a solid foundation for our project's success.

**Next Steps**:

1. **Implement the Schema**: Use the provided SQL scripts to set up the database in Supabase.
2. **Configure Security Policies**: Define Row Level Security policies tailored to your access requirements.
3. **Integrate with Your Application**: Connect your frontend and backend services to interact with the Supabase APIs.
4. **Monitor & Optimize**: Continuously monitor database performance and optimize queries and indexes as needed.
5. **Collaborate & Document**: Keep the team informed through detailed documentation and regular updates.
````
