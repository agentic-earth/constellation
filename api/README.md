# how the backend is built

# 🛠️ Hybrid Python API with Supabase-py

Welcome to the **Hybrid Model Application** backend! This README provides an overview of the project, setup instructions, technologies used, and project structure.

## 🌟 Table of Contents

1. [Project Overview](https://www.notion.so/how-the-backend-is-built-c1638929cc454c57ac9e7485baeef5bc?pvs=21)
2. [Technologies](https://www.notion.so/how-the-backend-is-built-c1638929cc454c57ac9e7485baeef5bc?pvs=21)
3. [Installation](https://www.notion.so/how-the-backend-is-built-c1638929cc454c57ac9e7485baeef5bc?pvs=21)
4. [Project Structure](https://www.notion.so/how-the-backend-is-built-c1638929cc454c57ac9e7485baeef5bc?pvs=21)
5. [Backend Components](https://www.notion.so/how-the-backend-is-built-c1638929cc454c57ac9e7485baeef5bc?pvs=21)
6. [Testing](https://www.notion.so/how-the-backend-is-built-c1638929cc454c57ac9e7485baeef5bc?pvs=21)
7. [Deployment](https://www.notion.so/how-the-backend-is-built-c1638929cc454c57ac9e7485baeef5bc?pvs=21)

## Project Overview

The Hybrid Model Application integrates a custom Python API with Supabase to leverage Supabase's robust REST API for standard CRUD operations while implementing custom logic for advanced functionalities like logging and versioning. The backend is fully developed with all necessary routes, services, and controllers, ensuring a scalable and maintainable architecture.

## Technologies

- **Python 3.8+**
- **FastAPI**
- **Supabase-py**
- **Uvicorn**
- **Pydantic**
- **Prisma**
- **Docker**
- **PostgreSQL**

## Installation

### Prerequisites

- **Python 3.8+**
- **Git**
- **Docker** (optional)

### Steps

1. **Clone the Repository**
    
    ```bash
    bash
    Copy code
    git clone https://github.com/yourorg/hybrid_api_project.git
    cd hybrid_api_project
    
    ```
    
2. **Create and Activate Virtual Environment**
    
    ```bash
    bash
    Copy code
    python3 -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    
    ```
    
3. **Install Dependencies**
    
    ```bash
    bash
    Copy code
    pip install -r requirements.txt
    
    ```
    
4. **Configure Environment Variables**
    
    Create a `.env` file in the root directory:
    
    ```
    env
    Copy code
    SUPABASE_URL=https://your-project.supabase.co
    SUPABASE_KEY=your-supabase-service-role-key
    LOG_LEVEL=INFO
    
    ```
    
    > Note: Replace your-project.supabase.co and your-supabase-service-role-key with your actual Supabase project URL and service role key. Never expose your service role key in client-side applications.
    > 
5. **Run the Application**
    
    ```bash
    bash
    Copy code
    uvicorn app.main:app --reload
    
    ```
    
6. **(Optional) Docker Setup**
    
    Build and run the Docker container:
    
    ```bash
    bash
    Copy code
    docker build -t hybrid_api_project .
    docker run -d -p 8000:8000 hybrid_api_project
    
    ```
    

## Project Structure

```arduino
arduino
Copy code
hybrid_api_project/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── models.py
│   ├── schemas.py
│   ├── database.py
│   ├── logger.py
│   ├── utils/
│   │   └── helpers.py
│   ├── routes/
│   │   ├── users.py
│   │   ├── blocks.py
│   │   ├── edges.py
│   │   ├── pipelines.py
│   │   └── audit_logs.py
│   └── services/
│       ├── user_service.py
│       ├── block_service.py
│       ├── edge_service.py
│       ├── pipeline_service.py
│       └── audit_service.py
├── tests/
│   ├── test_users.py
│   ├── test_blocks.py
│   ├── test_edges.py
│   ├── test_pipelines.py
│   └── test_audit_logs.py
├── logs/
│   └── app.log
├── .env
├── requirements.txt
├── Dockerfile
├── README.md
└── setup.py

```

## Backend Components

### Core Modules

- **`app/main.py`**: Initializes the FastAPI application, includes all API routers, and sets up middleware.
- **`app/config.py`**: Manages configuration settings and environment variables using Pydantic.
- **`app/database.py`**: Sets up the Supabase client for database interactions.
- **`app/logger.py`**: Configures centralized logging using Loguru, ensuring consistent logging across the application.

### Functional Modules

- **Routes (`app/routes/`)**: Defines API endpoints for various entities such as Users, Blocks, Edges, Pipelines, and Audit Logs. Each route handles HTTP requests and delegates business logic to the corresponding service.
- **Services (`app/services/`)**: Contains business logic and interacts with the database through Supabase. Services handle operations like creating, retrieving, updating, and deleting records, as well as implementing advanced functionalities like versioning and audit logging.
- **Schemas (`app/schemas.py`)**: Defines Pydantic models for request validation and response formatting, ensuring data integrity and type safety.
- **Utilities (`app/utils/`)**: Includes helper functions and utilities that support various parts of the application, enhancing code reusability and organization.

## Testing

Run tests using **pytest**:

```bash
bash
Copy code
pytest

```

## Deployment

Deploy the application using Docker or cloud platforms like Heroku, AWS, or Google Cloud. Ensure environment variables are securely managed in the deployment environment.
