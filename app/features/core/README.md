# 🗝️ **Core Microservice**

## 🛠️ **Overview**

Welcome to the **Core Microservice** of the **Constellation Backend**! 🌟 This foundational service is responsible for managing all CRUD (Create, Read, Update, Delete) operations with the Supabase backend. It serves as the backbone of the system, handling data persistence, retrieval, and complex search functionalities, particularly focusing on blocks and related entities. Importantly, the Core Microservice operates independently, providing essential data and services to other microservices without direct interactions, ensuring a clear separation of concerns and promoting modularity within the architecture.

## 🌟 **Features**

- **CRUD Operations**: Comprehensive creation, retrieval, updating, and deletion of core entities such as Users, Blocks, Edges, Pipelines, Taxonomies, and Vector Embeddings.
- **Advanced Search Capabilities**: Efficient searching and querying mechanisms over blocks and other entities, enabling complex data retrieval based on various filters and criteria.
- **Database Integrity**: Ensures data consistency and integrity through robust validation and transactional operations with Supabase.
- **Standalone Architecture**: Operates independently from other microservices, serving as a reliable data provider without direct dependencies.
- **Dependency Tracking**: Monitors and manages dependencies between different data entities, facilitating seamless data relationships and interactions.
- **Comprehensive Logging**: Utilizes the Constellation Logger for detailed logging of all operations, aiding in debugging and traceability.
- **Scalable Design**: Built to handle increasing loads and complexities, supporting horizontal scaling to maintain performance and reliability.

## 📝 **Design Considerations for Engineers**

### 1. **Separation of Concerns**

- **Independence**: The Core Microservice is designed to function independently, handling all data-related operations without direct interaction with other microservices. It provides necessary data to other services through well-defined interfaces and APIs.
- **Modularity**: By isolating data management responsibilities, the Core Microservice enhances the maintainability and scalability of the overall system, allowing each service to evolve without impacting others.

### 2. **Database Structure and Integrity**

- **Supabase Integration**: Leveraging Supabase as the primary backend, the Core Microservice interacts with PostgreSQL databases, utilizing Supabase's robust features for data management.
- **Data Models**: Defines clear and concise data models in `@models.py`, ensuring that each entity is accurately represented and related within the database.
- **Schemas**: Utilizes `@schemas.py` to define data validation and serialization schemas, maintaining data consistency and integrity across all operations.
- **Transactional Operations**: Implements transactional mechanisms to ensure that complex operations involving multiple entities maintain atomicity and consistency.

### 3. **CRUD Operations**

- **Comprehensive Management**: Provides full CRUD capabilities for core entities, enabling comprehensive data management and manipulation.
- **Validation and Error Handling**: Incorporates robust validation checks and error handling to manage invalid data inputs and ensure smooth operation workflows.

### 4. **Advanced Search Functionality**

- **Efficient Querying**: Implements optimized querying techniques to handle complex search requirements over blocks and other entities.
- **Filtering and Sorting**: Supports advanced filtering and sorting mechanisms, allowing users and other services to retrieve precisely the data they need.
- **Indexing**: Utilizes database indexing strategies to enhance search performance and reduce query response times.

### 5. **Dependency Management**

- **Relationship Handling**: Manages relationships between different entities (e.g., Blocks and Edges) meticulously, ensuring that dependencies are tracked and maintained correctly.
- **Conflict Resolution**: Implements strategies to detect and resolve conflicts arising from inter-entity dependencies, such as preventing cyclical relationships.

### 6. **Logging and Monitoring**

- **Constellation Logger**: Employs the Constellation Logger for structured and consistent logging across all operations, facilitating easy monitoring and debugging.
- **Traceability**: Ensures that all operations are thoroughly logged, providing clear traceability for actions performed within the service.

### 7. **Scalability and Performance**

- **Horizontal Scaling**: Architected to support horizontal scaling, allowing the service to handle increasing loads by adding more instances as needed.
- **Performance Optimization**: Continuously optimized for performance, ensuring that CRUD and search operations remain efficient under load.

## 🏗️ **Database Structure**

The Core Microservice interacts with a well-defined Supabase-backed PostgreSQL database. Below is an overview of the primary tables and their relationships:

### 📦 **Primary Tables**

1. **Users**

   - **Fields**:
     - `user_id` (UUID, Primary Key)
     - `email` (String, Unique)
     - `name` (String)
     - `created_at` (Timestamp)
     - `updated_at` (Timestamp)
   - **Description**: Stores user information and credentials.

2. **Blocks**

   - **Fields**:
     - `block_id` (UUID, Primary Key)
     - `block_type` (String)
     - `content` (JSONB)
     - `created_at` (Timestamp)
     - `updated_at` (Timestamp)
   - **Description**: Represents modular components used within pipelines.

3. **Edges**

   - **Fields**:
     - `edge_id` (UUID, Primary Key)
     - `source_block_id` (UUID, Foreign Key to Blocks)
     - `target_block_id` (UUID, Foreign Key to Blocks)
     - `relationship_type` (String)
     - `created_at` (Timestamp)
     - `updated_at` (Timestamp)
   - **Description**: Defines relationships between Blocks, outlining the flow of data or control.

4. **Pipelines**

   - **Fields**:
     - `pipeline_id` (UUID, Primary Key)
     - `pipeline_name` (String)
     - `description` (Text)
     - `status` (String)
     - `created_at` (Timestamp)
     - `updated_at` (Timestamp)
   - **Description**: Encapsulates workflows composed of interconnected Blocks and Edges.

5. **Taxonomies**

   - **Fields**:
     - `category_id` (UUID, Primary Key)
     - `name` (String)
     - `parent_id` (UUID, Foreign Key to Taxonomies, Nullable)
     - `created_at` (Timestamp)
     - `updated_at` (Timestamp)
   - **Description**: Manages hierarchical categorization of Blocks and Pipelines.

6. **VectorEmbeddings**
   - **Fields**:
     - `vector_id` (UUID, Primary Key)
     - `entity_type` (String) // e.g., "block", "pipeline"
     - `entity_id` (UUID, Foreign Key to respective entity)
     - `vector` (Vector) // pg-vector type
     - `taxonomy_filter` (JSONB)
     - `created_at` (Timestamp)
     - `updated_at` (Timestamp)
   - **Description**: Stores vector representations for entities to facilitate similarity searches.

### 🔗 **Relationships**

- **Users ↔ Pipelines**: One-to-Many (A user can create multiple pipelines).
- **Pipelines ↔ Blocks**: Many-to-Many (A pipeline comprises multiple blocks, and a block can belong to multiple pipelines) facilitated through Edges.
- **Blocks ↔ Edges**: One-to-Many (A block can have multiple outgoing/incoming edges defining its relationships).

- **controllers/**: Handles API endpoint logic, delegating business operations to services.
- **services/**: Encapsulates business logic and interacts directly with the Supabase backend.
- **models.py**: Defines ORM models representing database tables.
- **schemas.py**: Defines Pydantic schemas for data validation and serialization.
- **database.py**: Manages database connections and interactions.
- **logger.py**: Configures and provides logging utilities.
- **utils/**: Contains helper functions and utilities for serialization and other common tasks.

## 📚 **Models and Schemas**

### 🛠️ **Models (`models.py`)**

Defines the structure of the data entities corresponding to the database tables. Each model represents a table with fields mapped to database columns.

### 📄 **Schemas (`schemas.py`)**

Defines the data validation and serialization schemas using Pydantic. These schemas are used for request validation and response formatting.

### 🔍 **Defined Routes and Methods**

#### 1. **Users**

- **Create User**

  - **Endpoint**: `POST /users/`
  - **Description**: Creates a new user.
  - **Request Body**:
    ```json
    {
      "email": "user@example.com",
      "name": "John Doe"
    }
    ```
  - **Response**:
    ```json
    {
      "user_id": "UUID",
      "email": "user@example.com",
      "name": "John Doe",
      "created_at": "2023-10-05T14:48:00Z",
      "updated_at": "2023-10-05T14:48:00Z"
    }
    ```

- **Retrieve User**

  - **Endpoint**: `GET /users/{user_id}/`
  - **Description**: Retrieves details of a specific user.
  - **Path Parameters**:
    - `user_id` (UUID): Unique identifier of the user.
  - **Response**:
    ```json
    {
      "user_id": "UUID",
      "email": "user@example.com",
      "name": "John Doe",
      "created_at": "2023-10-05T14:48:00Z",
      "updated_at": "2023-10-05T14:48:00Z"
    }
    ```

- **Update User**

  - **Endpoint**: `PUT /users/{user_id}/`
  - **Description**: Updates details of a specific user.
  - **Path Parameters**:
    - `user_id` (UUID): Unique identifier of the user.
  - **Request Body**:
    ```json
    {
      "name": "Jane Doe"
    }
    ```
  - **Response**:
    ```json
    {
      "user_id": "UUID",
      "email": "user@example.com",
      "name": "Jane Doe",
      "created_at": "2023-10-05T14:48:00Z",
      "updated_at": "2023-10-05T15:00:00Z"
    }
    ```

- **Delete User**

  - **Endpoint**: `DELETE /users/{user_id}/`
  - **Description**: Deletes a specific user.
  - **Path Parameters**:
    - `user_id` (UUID): Unique identifier of the user.
  - **Response**:
    ```json
    {
      "message": "User deleted successfully."
    }
    ```

- **List All Users**
  - **Endpoint**: `GET /users/`
  - **Description**: Retrieves a list of all users.
  - **Response**:
    ```json
    {
      "users": [
        {
          "user_id": "UUID",
          "email": "user@example.com",
          "name": "John Doe",
          "created_at": "2023-10-05T14:48:00Z",
          "updated_at": "2023-10-05T14:48:00Z"
        }
        // ... more users
      ]
    }
    ```

#### 2. **Blocks**

- **Create Block**

  - **Endpoint**: `POST /blocks/`
  - **Description**: Creates a new block.
  - **Request Body**:
    ```json
    {
      "block_type": "data_ingestion",
      "content": {
        "source": "s3://bucket/data.csv",
        "format": "csv"
      }
    }
    ```
  - **Response**:
    ```json
    {
      "block_id": "UUID",
      "block_type": "data_ingestion",
      "content": {
        "source": "s3://bucket/data.csv",
        "format": "csv"
      },
      "created_at": "2023-10-05T14:50:00Z",
      "updated_at": "2023-10-05T14:50:00Z"
    }
    ```

- **Retrieve Block**

  - **Endpoint**: `GET /blocks/{block_id}/`
  - **Description**: Retrieves details of a specific block.
  - **Path Parameters**:
    - `block_id` (UUID): Unique identifier of the block.
  - **Response**:
    ```json
    {
      "block_id": "UUID",
      "block_type": "data_ingestion",
      "content": {
        "source": "s3://bucket/data.csv",
        "format": "csv"
      },
      "created_at": "2023-10-05T14:50:00Z",
      "updated_at": "2023-10-05T14:50:00Z"
    }
    ```

- **Update Block**

  - **Endpoint**: `PUT /blocks/{block_id}/`
  - **Description**: Updates details of a specific block.
  - **Path Parameters**:
    - `block_id` (UUID): Unique identifier of the block.
  - **Request Body**:
    ```json
    {
      "content": {
        "source": "s3://bucket/new_data.csv",
        "format": "csv"
      }
    }
    ```
  - **Response**:
    ```json
    {
      "block_id": "UUID",
      "block_type": "data_ingestion",
      "content": {
        "source": "s3://bucket/new_data.csv",
        "format": "csv"
      },
      "created_at": "2023-10-05T14:50:00Z",
      "updated_at": "2023-10-05T15:10:00Z"
    }
    ```

- **Delete Block**

  - **Endpoint**: `DELETE /blocks/{block_id}/`
  - **Description**: Deletes a specific block.
  - **Path Parameters**:
    - `block_id` (UUID): Unique identifier of the block.
  - **Response**:
    ```json
    {
      "message": "Block deleted successfully."
    }
    ```

- **List All Blocks**
  - **Endpoint**: `GET /blocks/`
  - **Description**: Retrieves a list of all blocks.
  - **Response**:
    ```json
    {
      "blocks": [
        {
          "block_id": "UUID",
          "block_type": "data_ingestion",
          "content": {
            "source": "s3://bucket/data.csv",
            "format": "csv"
          },
          "created_at": "2023-10-05T14:50:00Z",
          "updated_at": "2023-10-05T14:50:00Z"
        }
        // ... more blocks
      ]
    }
    ```

#### 3. **Edges**

- **Create Edge**

  - **Endpoint**: `POST /edges/`
  - **Description**: Creates a new edge between two blocks.
  - **Request Body**:
    ```json
    {
      "source_block_id": "UUID",
      "target_block_id": "UUID",
      "relationship_type": "data_flow"
    }
    ```
  - **Response**:
    ```json
    {
      "edge_id": "UUID",
      "source_block_id": "UUID",
      "target_block_id": "UUID",
      "relationship_type": "data_flow",
      "created_at": "2023-10-05T14:55:00Z",
      "updated_at": "2023-10-05T14:55:00Z"
    }
    ```

- **Retrieve Edge**

  - **Endpoint**: `GET /edges/{edge_id}/`
  - **Description**: Retrieves details of a specific edge.
  - **Path Parameters**:
    - `edge_id` (UUID): Unique identifier of the edge.
  - **Response**:
    ```json
    {
      "edge_id": "UUID",
      "source_block_id": "UUID",
      "target_block_id": "UUID",
      "relationship_type": "data_flow",
      "created_at": "2023-10-05T14:55:00Z",
      "updated_at": "2023-10-05T14:55:00Z"
    }
    ```

- **Update Edge**

  - **Endpoint**: `PUT /edges/{edge_id}/`
  - **Description**: Updates details of a specific edge.
  - **Path Parameters**:
    - `edge_id` (UUID): Unique identifier of the edge.
  - **Request Body**:
    ```json
    {
      "relationship_type": "control_flow"
    }
    ```
  - **Response**:
    ```json
    {
      "edge_id": "UUID",
      "source_block_id": "UUID",
      "target_block_id": "UUID",
      "relationship_type": "control_flow",
      "created_at": "2023-10-05T14:55:00Z",
      "updated_at": "2023-10-05T15:20:00Z"
    }
    ```

- **Delete Edge**

  - **Endpoint**: `DELETE /edges/{edge_id}/`
  - **Description**: Deletes a specific edge.
  - **Path Parameters**:
    - `edge_id` (UUID): Unique identifier of the edge.
  - **Response**:
    ```json
    {
      "message": "Edge deleted successfully."
    }
    ```

- **List All Edges**
  - **Endpoint**: `GET /edges/`
  - **Description**: Retrieves a list of all edges.
  - **Response**:
    ```json
    {
      "edges": [
        {
          "edge_id": "UUID",
          "source_block_id": "UUID",
          "target_block_id": "UUID",
          "relationship_type": "data_flow",
          "created_at": "2023-10-05T14:55:00Z",
          "updated_at": "2023-10-05T14:55:00Z"
        }
        // ... more edges
      ]
    }
    ```

#### 4. **Pipelines**

- **Create Pipeline**

  - **Endpoint**: `POST /pipelines/`
  - **Description**: Creates a new pipeline by associating blocks.
  - **Request Body**:
    ```json
    {
      "pipeline_name": "Data Processing Pipeline",
      "description": "Pipeline to process and analyze data.",
      "block_ids": ["UUID1", "UUID2", "UUID3"]
    }
    ```
  - **Response**:
    ```json
    {
      "pipeline_id": "UUID",
      "pipeline_name": "Data Processing Pipeline",
      "description": "Pipeline to process and analyze data.",
      "status": "created",
      "created_at": "2023-10-05T15:00:00Z",
      "updated_at": "2023-10-05T15:00:00Z"
    }
    ```

- **Retrieve Pipeline**

  - **Endpoint**: `GET /pipelines/{pipeline_id}/`
  - **Description**: Retrieves details of a specific pipeline.
  - **Path Parameters**:
    - `pipeline_id` (UUID): Unique identifier of the pipeline.
  - **Response**:
    ```json
    {
      "pipeline_id": "UUID",
      "pipeline_name": "Data Processing Pipeline",
      "description": "Pipeline to process and analyze data.",
      "status": "created",
      "created_at": "2023-10-05T15:00:00Z",
      "updated_at": "2023-10-05T15:00:00Z"
    }
    ```

- **Update Pipeline**

  - **Endpoint**: `PUT /pipelines/{pipeline_id}/`
  - **Description**: Updates details of a specific pipeline.
  - **Path Parameters**:
    - `pipeline_id` (UUID): Unique identifier of the pipeline.
  - **Request Body**:
    ```json
    {
      "description": "Updated description for the pipeline.",
      "block_ids": ["UUID1", "UUID2", "UUID4"]
    }
    ```
  - **Response**:
    ```json
    {
      "pipeline_id": "UUID",
      "pipeline_name": "Data Processing Pipeline",
      "description": "Updated description for the pipeline.",
      "status": "updated",
      "created_at": "2023-10-05T15:00:00Z",
      "updated_at": "2023-10-05T15:30:00Z"
    }
    ```

- **Delete Pipeline**

  - **Endpoint**: `DELETE /pipelines/{pipeline_id}/`
  - **Description**: Deletes a specific pipeline.
  - **Path Parameters**:
    - `pipeline_id` (UUID): Unique identifier of the pipeline.
  - **Response**:
    ```json
    {
      "message": "Pipeline deleted successfully."
    }
    ```

- **List All Pipelines**
  - **Endpoint**: `GET /pipelines/`
  - **Description**: Retrieves a list of all pipelines.
  - **Response**:
    ```json
    {
      "pipelines": [
        {
          "pipeline_id": "UUID",
          "pipeline_name": "Data Processing Pipeline",
          "description": "Pipeline to process and analyze data.",
          "status": "created",
          "created_at": "2023-10-05T15:00:00Z",
          "updated_at": "2023-10-05T15:00:00Z"
        }
        // ... more pipelines
      ]
    }
    ```

#### 5. **Taxonomies**

- **Create Taxonomy Category**

  - **Endpoint**: `POST /taxonomies/`
  - **Description**: Creates a new taxonomy category.
  - **Request Body**:
    ```json
    {
      "name": "Climate Data",
      "parent_id": "UUID" // Optional
    }
    ```
  - **Response**:
    ```json
    {
      "category_id": "UUID",
      "name": "Climate Data",
      "parent_id": "UUID",
      "created_at": "2023-10-05T15:10:00Z",
      "updated_at": "2023-10-05T15:10:00Z"
    }
    ```

- **Retrieve Taxonomy Category**

  - **Endpoint**: `GET /taxonomies/{category_id}/`
  - **Description**: Retrieves details of a specific taxonomy category.
  - **Path Parameters**:
    - `category_id` (UUID): Unique identifier of the category.
  - **Response**:
    ```json
    {
      "category_id": "UUID",
      "name": "Climate Data",
      "parent_id": "UUID",
      "created_at": "2023-10-05T15:10:00Z",
      "updated_at": "2023-10-05T15:10:00Z"
    }
    ```

- **Update Taxonomy Category**

  - **Endpoint**: `PUT /taxonomies/{category_id}/`
  - **Description**: Updates details of a specific taxonomy category.
  - **Path Parameters**:
    - `category_id` (UUID): Unique identifier of the category.
  - **Request Body**:
    ```json
    {
      "name": "Environmental Data",
      "parent_id": null
    }
    ```
  - **Response**:
    ```json
    {
      "category_id": "UUID",
      "name": "Environmental Data",
      "parent_id": null,
      "created_at": "2023-10-05T15:10:00Z",
      "updated_at": "2023-10-05T15:40:00Z"
    }
    ```

- **Delete Taxonomy Category**

  - **Endpoint**: `DELETE /taxonomies/{category_id}/`
  - **Description**: Deletes a specific taxonomy category.
  - **Path Parameters**:
    - `category_id` (UUID): Unique identifier of the category.
  - **Response**:
    ```json
    {
      "message": "Taxonomy category deleted successfully."
    }
    ```

- **List All Taxonomy Categories**
  - **Endpoint**: `GET /taxonomies/`
  - **Description**: Retrieves a list of all taxonomy categories.
  - **Response**:
    ```json
    {
      "taxonomies": [
        {
          "category_id": "UUID",
          "name": "Climate Data",
          "parent_id": "UUID",
          "created_at": "2023-10-05T15:10:00Z",
          "updated_at": "2023-10-05T15:10:00Z"
        }
        // ... more categories
      ]
    }
    ```

#### 6. **Vector Embeddings**

- **Create Vector Embedding**

  - **Endpoint**: `POST /vectors/`
  - **Description**: Creates a new vector embedding for an entity.
  - **Request Body**:
    ```json
    {
        "entity_type": "block",
        "entity_id": "UUID",
        "vector": [0.1, 0.2, ..., 0.512],
        "taxonomy_filter": {
            "category": "Climate Data"
        }
    }
    ```
  - **Response**:
    ```json
    {
        "vector_id": "UUID",
        "entity_type": "block",
        "entity_id": "UUID",
        "vector": [0.1, 0.2, ..., 0.512],
        "taxonomy_filter": {
            "category": "Climate Data"
        },
        "created_at": "2023-10-05T15:20:00Z",
        "updated_at": "2023-10-05T15:20:00Z"
    }
    ```

- **Retrieve Vector Embedding**

  - **Endpoint**: `GET /vectors/{vector_id}/`
  - **Description**: Retrieves details of a specific vector embedding.
  - **Path Parameters**:
    - `vector_id` (UUID): Unique identifier of the vector.
  - **Response**:
    ```json
    {
        "vector_id": "UUID",
        "entity_type": "block",
        "entity_id": "UUID",
        "vector": [0.1, 0.2, ..., 0.512],
        "taxonomy_filter": {
            "category": "Climate Data"
        },
        "created_at": "2023-10-05T15:20:00Z",
        "updated_at": "2023-10-05T15:20:00Z"
    }
    ```

- **Update Vector Embedding**

  - **Endpoint**: `PUT /vectors/{vector_id}/`
  - **Description**: Updates details of a specific vector embedding.
  - **Path Parameters**:
    - `vector_id` (UUID): Unique identifier of the vector.
  - **Request Body**:
    ```json
    {
        "vector": [0.2, 0.3, ..., 0.612],
        "taxonomy_filter": {
            "category": "Environmental Data"
        }
    }
    ```
  - **Response**:
    ```json
    {
        "vector_id": "UUID",
        "entity_type": "block",
        "entity_id": "UUID",
        "vector": [0.2, 0.3, ..., 0.612],
        "taxonomy_filter": {
            "category": "Environmental Data"
        },
        "created_at": "2023-10-05T15:20:00Z",
        "updated_at": "2023-10-05T16:00:00Z"
    }
    ```

- **Delete Vector Embedding**

  - **Endpoint**: `DELETE /vectors/{vector_id}/`
  - **Description**: Deletes a specific vector embedding.
  - **Path Parameters**:
    - `vector_id` (UUID): Unique identifier of the vector.
  - **Response**:
    ```json
    {
      "message": "Vector embedding deleted successfully."
    }
    ```

- **List All Vector Embeddings**

  - **Endpoint**: `GET /vectors/`
  - **Description**: Retrieves a list of all vector embeddings.
  - **Response**:
    ```json
    {
        "vectors": [
            {
                "vector_id": "UUID",
                "entity_type": "block",
                "entity_id": "UUID",
                "vector": [0.1, 0.2, ..., 0.512],
                "taxonomy_filter": {
                    "category": "Climate Data"
                },
                "created_at": "2023-10-05T15:20:00Z",
                "updated_at": "2023-10-05T15:20:00Z"
            },
            // ... more vectors
        ]
    }
    ```

- **Search Similar Blocks**
  - **Endpoint**: `POST /vectors/search/`
  - **Description**: Performs a similarity search over vector embeddings to find similar blocks.
  - **Request Body**:
    ```json
    {
        "query_vector": [0.1, 0.2, ..., 0.512],
        "taxonomy_filters": {
            "category": "Climate Data"
        },
        "top_k": 5
    }
    ```
  - **Response**:
    ```json
    {
      "results": [
        {
          "block_id": "UUID",
          "similarity_score": 0.95
        }
        // ... more results
      ]
    }
    ```

## 🛠️ **Method Implementations**

### 1. **User Service**

- **Function**: `create_user(user_data: UserCreateSchema) -> UserResponseSchema`

  - **Description**: Creates a new user in the Supabase backend. Validates the input data, ensures email uniqueness, and logs the operation.

- **Function**: `get_user(user_id: UUID) -> Optional[UserResponseSchema]`

  - **Description**: Retrieves a user's details based on their unique identifier.

- **Function**: `update_user(user_id: UUID, user_data: UserUpdateSchema) -> Optional[UserResponseSchema]`

  - **Description**: Updates a user's information. Validates the input and ensures data integrity.

- **Function**: `delete_user(user_id: UUID) -> bool`

  - **Description**: Deletes a user from the backend, ensuring that all related data is appropriately handled.

- **Function**: `list_all_users() -> List[UserResponseSchema]`
  - **Description**: Retrieves a list of all users in the system.

### 2. **Block Service**

- **Function**: `create_block(block_data: BlockCreateSchema) -> BlockResponseSchema`

  - **Description**: Creates a new block, validating its type and content before persisting it to the database.

- **Function**: `get_block(block_id: UUID) -> Optional[BlockResponseSchema]`

  - **Description**: Retrieves a block's details based on its unique identifier.

- **Function**: `update_block(block_id: UUID, block_data: BlockUpdateSchema) -> Optional[BlockResponseSchema]`

  - **Description**: Updates a block's information, ensuring that changes do not violate business rules.

- **Function**: `delete_block(block_id: UUID) -> bool`

  - **Description**: Deletes a block, handling any dependencies or relationships gracefully.

- **Function**: `list_all_blocks() -> List[BlockResponseSchema]`
  - **Description**: Retrieves a list of all blocks in the system.

### 3. **Edge Service**

- **Function**: `create_edge(edge_data: EdgeCreateSchema) -> EdgeResponseSchema`

  - **Description**: Creates a new edge between two blocks, ensuring that the relationship type is valid and that no cyclical dependencies are introduced.

- **Function**: `get_edge(edge_id: UUID) -> Optional[EdgeResponseSchema]`

  - **Description**: Retrieves an edge's details based on its unique identifier.

- **Function**: `update_edge(edge_id: UUID, edge_data: EdgeUpdateSchema) -> Optional[EdgeResponseSchema]`

  - **Description**: Updates an edge's information, ensuring that changes maintain data integrity.

- **Function**: `delete_edge(edge_id: UUID) -> bool`

  - **Description**: Deletes an edge, removing the relationship between the associated blocks.

- **Function**: `list_all_edges() -> List[EdgeResponseSchema]`
  - **Description**: Retrieves a list of all edges in the system.

### 4. **Pipeline Service**

- **Function**: `create_pipeline(pipeline_data: PipelineCreateSchema) -> PipelineResponseSchema`

  - **Description**: Constructs a new pipeline by associating the provided blocks. Validates the pipeline structure to prevent cycles and ensures all specified blocks exist.

- **Function**: `get_pipeline(pipeline_id: UUID) -> Optional[PipelineResponseSchema]`

  - **Description**: Retrieves a pipeline's details based on its unique identifier.

- **Function**: `update_pipeline(pipeline_id: UUID, pipeline_data: PipelineUpdateSchema) -> Optional[PipelineResponseSchema]`

  - **Description**: Updates a pipeline's information, handling additions or removals of blocks as needed.

- **Function**: `delete_pipeline(pipeline_id: UUID) -> bool`

  - **Description**: Deletes a pipeline, ensuring that all associated edges and relationships are appropriately handled.

- **Function**: `list_all_pipelines() -> List[PipelineResponseSchema]`
  - **Description**: Retrieves a list of all pipelines in the system.

### 5. **Taxonomy Service**

- **Function**: `create_taxonomy_category(category_data: TaxonomyCreateSchema) -> TaxonomyResponseSchema`

  - **Description**: Creates a new taxonomy category, optionally assigning it a parent category to establish a hierarchy.

- **Function**: `get_taxonomy_category(category_id: UUID) -> Optional[TaxonomyResponseSchema]`

  - **Description**: Retrieves a taxonomy category's details based on its unique identifier.

- **Function**: `update_taxonomy_category(category_id: UUID, category_data: TaxonomyUpdateSchema) -> Optional[TaxonomyResponseSchema]`

  - **Description**: Updates a taxonomy category's information, ensuring hierarchical integrity.

- **Function**: `delete_taxonomy_category(category_id: UUID) -> bool`

  - **Description**: Deletes a taxonomy category, handling any child categories or associated entities appropriately.

- **Function**: `list_all_taxonomy_categories() -> List[TaxonomyResponseSchema]`
  - **Description**: Retrieves a list of all taxonomy categories in the system.

### 6. **Vector Embedding Service**

- **Function**: `create_vector_embedding(vector_data: VectorRepresentationSchema) -> VectorEmbeddingResponseSchema`

  - **Description**: Creates a new vector embedding for a given entity, ensuring that the vector dimensions match the required specifications.

- **Function**: `get_vector_embedding(vector_id: UUID) -> Optional[VectorEmbeddingResponseSchema]`

  - **Description**: Retrieves a vector embedding's details based on its unique identifier.

- **Function**: `update_vector_embedding(vector_id: UUID, vector_data: VectorRepresentationSchema) -> Optional[VectorEmbeddingResponseSchema]`

  - **Description**: Updates a vector embedding's information, allowing for changes in the vector values or taxonomy filters.

- **Function**: `delete_vector_embedding(vector_id: UUID) -> bool`

  - **Description**: Deletes a vector embedding, removing it from the database.

- **Function**: `search_similar_blocks(query_vector: List[float], taxonomy_filters: Optional[Dict] = None, top_k: int = 5) -> List[Dict]`
  - **Description**: Performs a similarity search over vector embeddings to find the most similar blocks based on the provided query vector and optional taxonomy filters.

## 🔗 **Integration and Independence**

The **Core Microservice** is architected to function as an autonomous unit within the **Constellation Backend**. It does not directly interact with other microservices, ensuring a clear separation of concerns. Instead, it serves data and services to other microservices through well-defined APIs, acting as a reliable data provider. This design promotes modularity, facilitates easier maintenance, and allows each microservice to evolve independently without disrupting others.

## 🧑‍💻 **Developer Guidelines**

### 1. **Setting Up the Development Environment**

- **Prerequisites**:

  - Python 3.8+
  - PostgreSQL database with Supabase integration
  - Docker (optional, for containerized environments)

- **Installation Steps**:
  1. **Clone the Repository**:
     ```bash
     git clone https://github.com/your-repo/constellation-backend.git
     cd constellation-backend/app/core
     ```
  2. **Create a Virtual Environment**:
     ```bash
     python -m venv venv
     source venv/bin/activate
     ```
  3. **Install Dependencies**:
     ```bash
     pip install -r requirements.txt
     ```
  4. **Configure Environment Variables**:
     - Create a `.env` file in the `app/core/` directory with the following variables:
       ```
       SUPABASE_URL=your_supabase_url
       SUPABASE_KEY=your_supabase_anon_key
       DATABASE_URL=your_database_url
       ```
  5. **Run Database Migrations** (if applicable):
     ```bash
     alembic upgrade head
     ```
  6. **Start the Service**:
     ```bash
     uvicorn app.core.main:app --reload
     ```

### 2. **Developing Routes and Controllers**

- **Defining Routes**:

  - Routes are defined within the `app/core/routes/` directory.
  - Each entity (Users, Blocks, Edges, etc.) has its own route file (e.g., `user_routes.py`, `block_routes.py`).
  - Use FastAPI's `APIRouter` to define endpoints, ensuring clear and organized API structures.

- **Implementing Controllers**:
  - Controllers handle the request processing logic.
  - Located in the `app/core/controllers/` directory, each corresponding to a route file.
  - Controllers interact with services to perform business operations.

### 3. **Implementing Services**

- **Service Classes**:

  - Located in the `app/core/services/` directory.
  - Each service class (e.g., `UserService`, `BlockService`) encapsulates business logic for a specific entity.
  - Services interact directly with the Supabase backend, performing CRUD operations and complex queries.

- **Example**:

  ```python
  # app/core/services/user_service.py

  from app.schemas import UserCreateSchema, UserResponseSchema
  from app.models import User
  from app.database import get_supabase_client
  from app.logger import ConstellationLogger
  from uuid import UUID

  class UserService:
      def __init__(self):
          self.supabase = get_supabase_client()
          self.logger = ConstellationLogger("UserService")

      def create_user(self, user_data: UserCreateSchema) -> UserResponseSchema:
          try:
              response = self.supabase.table("users").insert(user_data.dict()).execute()
              user = User(**response.data[0])
              self.logger.info(f"User created: {user.email}")
              return UserResponseSchema(**user.dict())
          except Exception as e:
              self.logger.error(f"Error creating user: {e}")
              raise e
  ```

### 4. **Database Interactions**

- **Connection Management**:

  - Managed via `app/core/database.py` using Supabase's client.
  - Example:

    ```python
    # app/core/database.py

    from supabase import create_client, Client
    import os

    def get_supabase_client() -> Client:
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        return create_client(url, key)
    ```

- **ORM Models**:
  - Defined in `models.py` as Pydantic models.
  - Ensure that models accurately reflect the database schema.

### 5. **Logging and Monitoring**

- **Logger Configuration**:

  - Configured in `app/core/logger.py` using the Constellation Logger.
  - Ensures consistent logging across all services.
  - Example:

    ```python
    # app/core/logger.py

    import logging

    class ConstellationLogger:
        def __init__(self, name: str):
            self.logger = logging.getLogger(name)
            self.logger.setLevel(logging.INFO)
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

        def info(self, message: str):
            self.logger.info(message)

        def error(self, message: str):
            self.logger.error(message)

        def warning(self, message: str):
            self.logger.warning(message)
    ```

- **Monitoring Tools**:
  - Integrate with tools like Prometheus and Grafana for real-time monitoring and alerting.
  - Set up dashboards to visualize key metrics such as request rates, error rates, and response times.

### 6. **Testing**

- **Testing Framework**:

  - Utilize `pytest` for writing and executing tests.
  - Located in `app/core/tests/`.

- **Types of Tests**:

  - **Unit Tests**: Test individual functions and methods within services.
  - **Integration Tests**: Test interactions between services and the Supabase backend.
  - **End-to-End Tests**: Validate the complete workflow from API requests to database operations.

- **Running Tests**:
  ```bash
  pytest
  ```

### 7. **Best Practices**

- **Code Quality**:

  - Adhere to PEP 8 standards for Python code.
  - Use meaningful variable and function names for clarity.
  - Implement type hinting for better code readability and maintenance.

- **Error Handling**:

  - Implement comprehensive error handling to manage exceptions gracefully.
  - Return meaningful error messages to API consumers.

- **Documentation**:
  - Maintain up-to-date documentation within the codebase.
  - Utilize docstrings and comments to explain complex logic and decisions.

### 8. **Security Practices**

- **Authentication and Authorization**:

  - Implement secure authentication mechanisms (e.g., JWT tokens) for API endpoints.
  - Ensure that sensitive operations are restricted to authorized users only.

- **Data Protection**:

  - Encrypt sensitive data both in transit and at rest.
  - Utilize environment variables to manage secret keys and sensitive configurations.

- **Input Validation**:
  - Rigorously validate all incoming data to prevent injection attacks and ensure data integrity.

### 9. **Scalability Considerations**

- **Load Balancing**:

  - Deploy the Core Microservice behind a load balancer to distribute incoming traffic evenly across instances.

- **Horizontal Scaling**:

  - Design the service to support horizontal scaling, allowing additional instances to be added seamlessly as demand increases.

- **Caching Strategies**:
  - Implement caching mechanisms (e.g., Redis) to store frequently accessed data, reducing database load and improving response times.

## 🔧 **Future Enhancements**

1. **Enhanced Search Capabilities**:

   - Implement full-text search functionalities to allow more flexible and powerful querying over blocks and other entities.

2. **Advanced Analytics**:

   - Integrate analytics tools to provide insights into data usage patterns, user behaviors, and system performance.

3. **GraphQL Integration**:

   - Introduce GraphQL APIs to offer more flexible and efficient data retrieval options compared to RESTful APIs.

4. **Automated Dependency Management**:

   - Develop automated tools to manage and resolve dependencies between entities, ensuring consistency and preventing conflicts.

5. **Improved Error Recovery**:

   - Implement advanced error recovery mechanisms to handle failures gracefully and ensure system resilience.

6. **Extended Security Measures**:

   - Incorporate additional security layers, such as intrusion detection systems and automated vulnerability scanning, to enhance data protection.

7. **Microservice Communication Enhancements**:
   - Explore asynchronous communication methods (e.g., message queues) to facilitate more efficient interactions with other microservices when needed.

## 📝 **Conclusion**

The **Core Microservice** is the heart of the **Constellation Backend**, meticulously managing all data-related operations with the Supabase backend. By providing robust CRUD functionalities, advanced search capabilities, and ensuring data integrity, it serves as a reliable foundation for the entire system. Its standalone architecture promotes modularity and maintainability, allowing other microservices to leverage its data services seamlessly without direct dependencies.

With comprehensive design considerations, a clear database structure, and detailed developer guidelines, the Core Microservice is well-equipped to handle the evolving data management needs of the Constellation ecosystem. Whether you're onboarding as a new developer or enhancing existing functionalities, this README serves as your roadmap to understanding and effectively working with the Core Microservice.

🚀 **Happy Coding!**
