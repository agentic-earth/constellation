# LLM Microservice for Constellation Backend

## Overview

This microservice is a crucial component of the Constellation Backend, designed to manage interactions with Language Learning Models (LLMs). It facilitates intelligent conversations, enabling reasoning over our graph of models and data sources to assist in building and suggesting pipelines.

## Design Considerations for Engineers

1. **Schema Integration**:

   - Utilize existing schemas from `app/schemas.py`.
   - Define new schemas as needed, following the established patterns.
   - Key schemas to consider:
     - `UserResponseSchema` for user information
     - `PipelineResponseSchema` for pipeline details
     - `BlockResponseSchema` and `EdgeResponseSchema` for graph components

2. **State Management**:

   - Implement efficient session state handling.
   - Consider using Redis or a similar in-memory data store for fast access.

3. **Concurrency**:

   - Design for high concurrency using asynchronous programming.
   - Implement proper locking mechanisms for shared resources.

4. **LLM Integration**:

   - Abstract LLM interactions to allow easy switching between providers.
   - Implement retry logic and error handling for LLM API calls.

5. **Scalability**:

   - Design with horizontal scalability in mind.
   - Implement stateless architecture where possible.

6. **Security**:

   - Ensure proper authentication and authorization.
   - Implement rate limiting to prevent abuse.

7. **Logging and Monitoring**:
   - Use structured logging for easy parsing and analysis.
   - Implement comprehensive monitoring and alerting.

## Technical Stack

### Core Framework

- **FastAPI**: High-performance, easy-to-use framework for building APIs with Python 3.6+ based on standard Python type hints.

### ASGI Server

- **Uvicorn**: Lightweight ASGI server, for use with asyncio frameworks.

### Database

- **Supabase**: PostgreSQL database with real-time capabilities.

### Caching

- **Redis**: In-memory data structure store, used for caching and session management.

### LLM Integration

Options to consider:

1. **Haystack**: many great build in features and easy to use API and switch between models easy
2. **Raw GPT API**: enough said
3. **Langchain**: also enough said

### Additional Libraries

- **Pydantic**: Data validation using Python type annotations.
- **SQLAlchemy**: SQL toolkit and Object-Relational Mapping (ORM) library.
- **Alembic**: Database migration tool for SQLAlchemy.
- **Loguru**: Logging library offering a simple API.
- **Pytest**: Testing framework for writing and running tests.

## API Endpoints

1. **Start Conversation**

   - `POST /llm/chat/`
   - Payload: `{"user_id": UUID, "initial_message": str}`
   - Response: `{"session_id": UUID, "message": str}`

2. **Send Message**

   - `POST /llm/chat/{session_id}/message/`
   - Payload: `{"user_message": str}`
   - Response: `{"response_message": str, "updated_session": str}`

3. **Retrieve Conversation History**

   - `GET /llm/chat/{session_id}/history/`
   - Response: List of message objects

4. **End Conversation**

   - `DELETE /llm/chat/{session_id}/`
   - Response: Confirmation message

5. **List Active Sessions**
   - `GET /llm/chat/sessions/`
   - Response: List of active session objects

# LLM Microservice for Constellation Backend

## Critical Requirement: Dynamic JSON Generation for API Communication

A key feature of this microservice is the ability to have the LLM dynamically generate JSON structures for communication with other APIs in the Constellation Backend. This capability is crucial for several reasons:

1. **Flexible Integration**: It allows the LLM to interact with various components of the system without hardcoding API structures.
2. **Adaptive Responses**: The LLM can generate appropriate API calls based on user input and context.
3. **Extensibility**: As new APIs are added to the system, the LLM can be trained to generate JSON for these without code changes.

We will use Pydantic for defining and validating these dynamic JSON structures. This approach offers several advantages:

- **Type Safety**: Pydantic ensures that the generated JSON conforms to expected schemas.
- **Automatic Validation**: Invalid structures are caught early, preventing downstream errors.
- **Clear Documentation**: Pydantic models serve as both runtime validators and clear documentation of expected data structures.

### Pydantic Models for Dynamic JSON

Create a set of Pydantic models that represent the various API request and response structures in your system. For example:

```python
from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID

class BlockAPIRequest(BaseModel):
    block_type: str
    name: str
    description: Optional[str] = None

class EdgeAPIRequest(BaseModel):
    source_block_id: UUID
    target_block_id: UUID
    edge_type: str

class PipelineAPIRequest(BaseModel):
    name: str
    blocks: List[UUID]
    edges: List[EdgeAPIRequest]

# ... more models as needed ...
```

The LLM will be responsible for generating JSON that conforms to these models. You can then use Pydantic to validate and process the LLM's output:

```python
async def process_llm_output(llm_json_str: str) -> PipelineAPIRequest:
    try:
        # Parse and validate the LLM's JSON output
        pipeline_request = PipelineAPIRequest.parse_raw(llm_json_str)
        # Use the validated object to make API calls or process further
        return pipeline_request
    except ValidationError as e:
        # Handle validation errors, possibly by asking the LLM to correct its output
        logger.error(f"LLM generated invalid JSON: {e}")
        # Implement error handling strategy (e.g., retry, fallback, or user notification)
```

By implementing this dynamic JSON generation with Pydantic validation, you create a powerful and flexible system for LLM-driven API interactions within the Constellation Backend.

## Schema Usage and Definition

1. Utilize existing schemas from `app/schemas.py`:

   ```python
   from app.schemas import UserResponseSchema, PipelineResponseSchema, BlockResponseSchema, EdgeResponseSchema
   ```

2. Define new schemas specific to LLM interactions:

   ```python
   from pydantic import BaseModel, Field
   from uuid import UUID
   from datetime import datetime

   class ChatSessionSchema(BaseModel):
       session_id: UUID = Field(..., description="Unique identifier for the chat session")
       user_id: UUID = Field(..., description="UUID of the user associated with this session")
       created_at: datetime = Field(..., description="Timestamp of session creation")
       last_active: datetime = Field(..., description="Timestamp of last activity in the session")

   class ChatMessageSchema(BaseModel):
       message_id: UUID = Field(..., description="Unique identifier for the message")
       session_id: UUID = Field(..., description="UUID of the associated chat session")
       sender: str = Field(..., description="Identifier of the message sender (user or LLM)")
       content: str = Field(..., description="Content of the message")
       timestamp: datetime = Field(..., description="Timestamp of when the message was sent/received")
   ```

## LLM Integration Considerations

1. **API Abstraction**:
   Create an abstract base class for LLM interactions to allow easy switching between providers:

   ```python
   from abc import ABC, abstractmethod

   class LLMProvider(ABC):
       @abstractmethod
       async def generate_response(self, prompt: str) -> str:
           pass

   class OpenAIProvider(LLMProvider):
       async def generate_response(self, prompt: str) -> str:
           # Implementation for OpenAI

   class HuggingFaceProvider(LLMProvider):
       async def generate_response(self, prompt: str) -> str:
           # Implementation for Hugging Face
   ```

2. **Prompt Engineering**:
   Develop a robust system for constructing prompts that incorporate context from the Constellation graph:

   ```python
   async def construct_prompt(user_message: str, context: dict) -> str:
       # Logic to construct a prompt using user message and graph context
   ```

3. **Response Parsing**:
   Implement parsing logic to extract structured information from LLM responses:
   ```python
   async def parse_llm_response(response: str) -> dict:
       # Logic to parse LLM response into structured data
   ```

## Concurrency and State Management

1. Use FastAPI's built-in support for asynchronous request handling.
2. Implement a Redis-based session store:

   ```python
   import aioredis

   redis = aioredis.from_url("redis://localhost")

   async def get_session(session_id: UUID) -> dict:
       return await redis.get(str(session_id))

   async def update_session(session_id: UUID, data: dict):
       await redis.set(str(session_id), data)
   ```

## Testing Strategy

1. Unit Tests: Test individual components in isolation.
2. Integration Tests: Test the interaction between components.
3. End-to-End Tests: Test the entire flow from user input to LLM response.

## Deployment Considerations

1. Use Docker for containerization to ensure consistency across environments.
2. Implement a CI/CD pipeline for automated testing and deployment.
3. Consider using Kubernetes for orchestration in a production environment.

## Monitoring and Logging

1. Implement structured logging using Loguru:

   ```python
   from loguru import logger

   logger.add("llm_service.log", rotation="500 MB")

   async def some_function():
       logger.info("Processing request", extra={"user_id": user_id, "session_id": session_id})
   ```

2. Set up monitoring using Prometheus and Grafana for real-time insights into service performance.

## Future Enhancements

1. Implement more sophisticated context management for multi-turn conversations.
2. Explore fine-tuning LLMs on domain-specific data for improved performance.
3. Implement a feedback loop system for continuous improvement of LLM responses.
4. Consider streaming efficiently to the frontend!!!

By following these guidelines and considerations, you'll be well-equipped to develop a robust and scalable LLM microservice for the Constellation Backend. Remember to maintain clear documentation and adhere to established coding standards throughout the development process.
