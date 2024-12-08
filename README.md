# 🌌 **Constellation Master Program**

## 🚀 **Overview**

Welcome to the **Constellation Master Program**! 🌟 This master application orchestrates a suite of microservices to automate the use of machine learning models for satellite image inference. Our service allows users to connect datasets with models, and evaluate their outputs through a simple drag-and-drop interface supported by an integrated LLM. 

## 🛠️ **High-Level Design**

Constellation relies on a Microservice Architecture with four component services: A Dagster Microservice, a Core-Backend Microservice, a Large Language Model (LLM) Microservice, and a Model Hosting Microservice.

### 📦 **Microservices Composition**

1. **Core Backend Microservice**

   - **Role**: Acts as the backbone of Constellation, this microservice provides data persistence, and facilitates interactions between other microservices as well as the front-end of our application.
   - **Responsibilities**:
     - Stores datasets, models, and user-created pipelines.
     - Manages interactions between the Dagster, LLM, and Model Hosting Microservice

2. **Model Hosting Microservice**

   - **Role**: Leverages the Modal Cloud compute platform to  facilitate the containerization and deployment of machine learning models. 
   - **Responsibilities**:
     - Model containerization and versioning.
     - Deployment of inference endpoints.
     - Manages the deletion and creation of deployed model services.

3. **Dagster Microservice**

   - **Role**: Utilizes the task orchestration capabilities of Dagster to create end-to-end piplines starting with data preprocessing and outputting the results of model inference.
   - **Responsibilities**:
     - Imports data from cloud storage platforms
     - Automates data preprocessing and transformation.
     - Exports model inference results to cloud storage platforms

4. **Agent (LLM) Microservice**
   - **Role**: Leverages Large Language Model (LLM) capabilities to present users with database and model options that meet their prompt constraints.
   - **Responsibilities**:
     - Streamlines model and database selection for the user.
     - Dynamic JSON generation for pipline invocation.

## 🗝️ **Core Types and Schemas**

At the heart of Constellation lies the **Core Microservice**, which defines essential data types and schemas critical for the seamless operation of all microservices. These types ensure consistent data handling and facilitate communication between different components of the system.


### 📂 **Type Integration Across Microservices**

All microservices reference and utilize the types defined in the **Core Microservice** to maintain data consistency and integrity. This centralized type management allows:

- **Uniform Data Handling**: Ensures that all services interpret and process data uniformly.
- **Ease of Maintenance**: Facilitates updates and modifications to data structures without impacting individual services drastically.
- **Enhanced Interoperability**: Simplifies interactions between microservices by providing a common language and structure.

- **app/**: Contains all microservices and their respective components.
- **core/**: Houses the Core Microservice, managing data interactions and types.
- **docker/**, **dagster/**, **agent/**: Each directory represents a microservice with its controllers, services, routes, and specific README documentation.
- **tests/**: Organized by microservice, containing unit, integration, and end-to-end tests.
- **docker-compose.yml**: Facilitates the orchestration of microservices in development and production environments.
- **README.md**: This master README, providing an overview and integration details.

## 🛠️ **Technologies and Tools**

- **[FastAPI](https://fastapi.tiangolo.com/)** 🚀: High-performance web framework for building APIs with Python.
- **[Dagster](https://dagster.io/)** 🛠️: Orchestrator for building, managing, and executing data pipelines.
- **[Docker](https://www.docker.com/)** 🐳: Containerization platform for consistent deployment environments.
- **[Supabase](https://supabase.com/)** ☁️: Backend-as-a-Service platform for database and authentication.
- **[Pydantic](https://pydantic-docs.helpmanual.io/)** 📄: Data validation and settings management using Python type annotations.
- **[Loguru](https://loguru.readthedocs.io/en/stable/)** 📝: Advanced logging library for Python.
- **[Redis](https://redis.io/)** ⚡: In-memory data structure store for caching and state management.
- **[Pytest](https://docs.pytest.org/en/7.1.x/)** 🧪: Testing framework for Python.
- **[Uvicorn](https://www.uvicorn.org/)** 🌪️: ASGI server for running FastAPI applications.
- **[Prometheus](https://prometheus.io/)** 📊 _(Optional)_: Monitoring and alerting toolkit.
- **[Grafana](https://grafana.com/)** 📈 _(Optional)_: Platform for monitoring and observability.

## 🧑‍💻 **Getting Started**

### Prerequisites

- **Python 3.8+**
- **Docker & Docker Compose**
- **Supabase Account**
- **Redis Instance** _(for state management)_

### Installation Steps

1. **Clone the Repository**

   ```bash
   git clone https://github.com/your-repo/constellation-backend.git
   cd constellation-backend
   ```

2. **Set Up Environment Variables**

   - Create a `.env` file in the root directory with the following:
     ```
     SUPABASE_URL=your_supabase_url
     SUPABASE_KEY=your_supabase_anon_key
     DATABASE_URL=your_database_url
     REDIS_URL=redis://localhost:6379
     ```

3. **Install Dependencies**

   ```bash
   pip install -r app/requirements.txt
   ```

4. **Run Docker Containers**

   ```bash
   docker-compose up --build
   ```

5. **Access Services**
   - **Core Microservice**: `http://localhost:8000/core/`
   - **Docker Microservice**: `http://localhost:8001/docker/`
   - **Dagster Microservice**: `http://localhost:8002/dagster/`
   - **Agent Microservice**: `http://localhost:8003/agent/`

## 🔍 **Detailed Microservices Interaction**

### 1. **Core Microservice**

- **Purpose**: Centralized data management and CRUD operations.
- **Interaction**:
  - Provides data endpoints consumed by Docker, Dagster, and Agent microservices.
  - Defines core data types used across the ecosystem.

### 2. **Docker Microservice**

- **Purpose**: Manages ML model containerization and deployment.
- **Interaction**:
  - Retrieves model data from the Core Microservice.
  - Deploys models as inference endpoints.
  - Integrates with the Dagster Microservice for automated pipeline environments.

### 3. **Dagster Microservice**

- **Purpose**: Orchestrates data pipelines based on user-defined blocks.
- **Interaction**:
  - Fetches pipeline configurations and block relationships from the Core Microservice.
  - Deploys and monitors pipelines, reporting statuses back to the Core Microservice.

### 4. **Agent (LLM) Microservice**

- **Purpose**: Enables intelligent conversations and assists in pipeline creation.
- **Interaction**:
  - Interfaces with the Core Microservice to fetch data and provide context-aware suggestions.
  - Utilizes types defined in Core for consistent data exchange and operations.

## 📚 **Types and Schemas Integration**

The **Core Microservice** defines a set of Pydantic schemas and types that serve as the foundation for data exchange across all microservices. These definitions ensure that each component interprets and processes data consistently, fostering seamless interoperability.

### 🔑 **Key Schemas**

- **User Schemas**: Manage user data, authentication, and authorization.
- **Pipeline Schemas**: Define the structure and configurations of data pipelines.
- **Block and Edge Schemas**: Represent the building blocks and their interconnections within pipelines.
- **Vector Embedding Schemas**: Facilitate similarity searches and advanced data querying.

### 🔄 **Usage Across Microservices**

- **Docker**: Utilizes `ModelPackageSchema` and `DeploymentStatusSchema` from Core for model packaging and deployment.
- **Dagster**: Employs `PipelineCreateSchema` and `PipelineStatusSchema` for pipeline management.
- **Agent**: Leverages `UserResponseSchema` and conversation-related schemas for managing intelligent interactions.

## 📈 **Monitoring and Logging**

To maintain the health and performance of the Constellation ecosystem, comprehensive monitoring and logging strategies are employed:

- **Logging**: Each microservice utilizes `Loguru` for structured and detailed logging, capturing critical events and errors.
- **Monitoring**: Integration with **Prometheus** and **Grafana** (optional) provides real-time insights into system performance, resource utilization, and operational metrics.

## 📝 **Conclusion**

The **Constellation Master Program** serves as the orchestrating force behind a suite of specialized microservices, delivering a robust and scalable backend solution for sophisticated data management and analytics. By leveraging the strengths of each microservice and ensuring seamless integration through well-defined types and schemas, Constellation provides a powerful platform tailored for modern data-driven applications.

Whether you're deploying complex machine learning models, orchestrating intricate data pipelines, or engaging in intelligent interactions, Constellation's modular architecture ensures flexibility, reliability, and efficiency. Embrace the power of interconnected microservices and explore the endless possibilities within the Constellation ecosystem! 🚀

---
