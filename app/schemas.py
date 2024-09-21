# app/schemas.py

from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime

from app.models import (
    BlockTypeEnum,
    EntityTypeEnum,
    BuildStatusEnum,
    DependencyTypeEnum,
    VerificationStatusEnum,
    ActionTypeEnum,
    AuditEntityTypeEnum,
    EdgeTypeEnum,  # Ensure EdgeTypeEnum is imported
)


# Base configuration for all schemas
class BaseSchema(BaseModel):
    """
    BaseSchema serves as the foundational schema for all other Pydantic models.
    It enables ORM mode for seamless integration with database models.
    """
    class Config:
        from_attributes = True  

# -------------------
# User Schemas
# -------------------

class UserCreateSchema(BaseSchema):
    """
    Schema for creating a new user.
    """
    username: str = Field(..., description="Unique username for the user.")
    email: EmailStr = Field(..., description="Valid email address for the user.")
    password: str = Field(..., description="Password for the user account.")

    @field_validator('password')
    def password_strength(cls, v):
        """
        Validates the strength of the password.
        """
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        # Add more checks (e.g., uppercase, numbers, special characters) if needed
        return v

    @field_validator('username')
    def username_no_spaces(cls, v):
        """
        Ensures the username does not contain spaces.
        """
        if ' ' in v:
            raise ValueError('Username must not contain spaces')
        return v


class UserUpdateSchema(BaseSchema):
    """
    Schema for updating an existing user.
    """
    username: Optional[str] = Field(None, description="New username for the user.")
    email: Optional[EmailStr] = Field(None, description="New email address for the user.")
    password_hash: Optional[str] = Field(None, description="New hashed password for the user.")
    role: Optional[str] = Field(None, description="Role of the user (e.g., admin, developer).")


class UserResponseSchema(BaseSchema):
    """
    Schema for returning user details.
    """
    user_id: UUID = Field(..., description="Unique identifier for the user.")
    username: str = Field(..., description="Username of the user.")
    email: EmailStr = Field(..., description="Email address of the user.")
    role: str = Field(..., description="Role of the user.")
    created_at: datetime = Field(..., description="Timestamp when the user was created.")
    updated_at: datetime = Field(..., description="Timestamp when the user was last updated.")

    class Config:
        exclude = ['password_hash']


# -------------------
# API Key Schemas
# -------------------

class APIKeyCreateSchema(BaseSchema):
    """
    Schema for creating a new API key.
    """
    user_id: UUID = Field(..., description="UUID of the user associated with the API key.")
    encrypted_api_key: str = Field(..., description="Encrypted API key string.")
    expires_at: datetime = Field(..., description="Expiration timestamp for the API key.")


class APIKeyResponseSchema(BaseSchema):
    """
    Schema for returning API key details.
    """
    api_key_id: UUID = Field(..., description="Unique identifier for the API key.")
    user_id: UUID = Field(..., description="UUID of the user associated with the API key.")
    encrypted_api_key: str = Field(..., description="Encrypted API key string.")
    created_at: datetime = Field(..., description="Timestamp when the API key was created.")
    expires_at: datetime = Field(..., description="Expiration timestamp for the API key.")
    is_active: bool = Field(..., description="Status indicating if the API key is active.")


# -------------------
# Taxonomy Category Schemas
# -------------------

class TaxonomyCategoryCreateSchema(BaseSchema):
    """
    Schema for creating a new taxonomy category.
    """
    name: str = Field(..., description="Name of the taxonomy category.")
    parent_id: Optional[UUID] = Field(None, description="UUID of the parent category, if any.")


class TaxonomyCategoryResponseSchema(BaseSchema):
    """
    Schema for returning taxonomy category details.
    """
    category_id: UUID = Field(..., description="Unique identifier for the taxonomy category.")
    name: str = Field(..., description="Name of the taxonomy category.")
    parent_id: Optional[UUID] = Field(None, description="UUID of the parent category, if any.")
    created_at: datetime = Field(..., description="Timestamp when the category was created.")
    updated_at: datetime = Field(..., description="Timestamp when the category was last updated.")


# -------------------
# Block Schemas
# -------------------

class BlockCreateSchema(BaseSchema):
    """
    Schema for creating a new block.
    """
    name: str = Field(..., description="Unique name for the block.")
    block_type: BlockTypeEnum = Field(..., description="Type of the block (e.g., 'dataset', 'model').")
    description: Optional[str] = Field(None, description="Description of the block.")
    created_by: Optional[UUID] = Field(None, description="UUID of the user creating the block.")


class BlockUpdateSchema(BaseSchema):
    """
    Schema for updating an existing block.
    """
    name: Optional[str] = Field(None, description="New name for the block.")
    block_type: Optional[BlockTypeEnum] = Field(None, description="New type for the block.")
    description: Optional[str] = Field(None, description="New description for the block.")


class BlockResponseSchema(BaseSchema):
    """
    Schema for returning block details, including taxonomy and vector embedding.
    """
    block_id: UUID = Field(..., description="Unique identifier for the block.")
    name: str = Field(..., description="Name of the block.")
    block_type: str = Field(..., description="Type of the block.")
    description: str = Field(..., description="Description of the block.")
    created_at: datetime = Field(..., description="Timestamp when the block was created.")
    updated_at: datetime = Field(..., description="Timestamp when the block was last updated.")
    current_version_id: UUID = Field(..., description="UUID of the current version of the block.")
    taxonomy: Optional[Dict[str, Any]] = Field(None, description="Taxonomy details associated with the block.")
    vector_embedding: Optional["VectorRepresentationSchema"] = Field(None, description="Vector embedding associated with the block.")



# -------------------
# Block Version Schemas
# -------------------

class BlockVersionCreateSchema(BaseSchema):
    """
    Schema for creating a new block version.
    """
    block_id: UUID = Field(..., description="UUID of the block to which this version belongs.")
    version_number: int = Field(..., description="Sequential version number.")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Metadata specific to this block version.")
    created_by: UUID = Field(..., description="UUID of the user creating this version.")


class BlockVersionResponseSchema(BaseSchema):
    """
    Schema for returning block version details.
    """
    version_id: UUID = Field(..., description="Unique identifier for the block version.")
    block_id: UUID = Field(..., description="UUID of the associated block.")
    version_number: int = Field(..., description="Sequential version number.")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Metadata specific to this block version.")
    created_at: datetime = Field(..., description="Timestamp when the version was created.")
    created_by: UUID = Field(..., description="UUID of the user who created this version.")
    is_active: bool = Field(..., description="Indicator if this is the active version.")


# -------------------
# Block Taxonomy Schemas
# -------------------

class BlockTaxonomyCreateSchema(BaseSchema):
    """
    Schema for associating a taxonomy category with a block.
    """
    block_id: UUID = Field(..., description="UUID of the block.")
    category_id: UUID = Field(..., description="UUID of the taxonomy category.")


class BlockTaxonomyResponseSchema(BaseSchema):
    """
    Schema for returning block taxonomy association details.
    """
    block_taxonomy_id: UUID = Field(..., description="Unique identifier for the block-taxonomy association.")
    block_id: UUID = Field(..., description="UUID of the associated block.")
    category_id: UUID = Field(..., description="UUID of the associated taxonomy category.")
    created_at: datetime = Field(..., description="Timestamp when the association was created.")


# -------------------
# Code Repo Schemas
# -------------------

class CodeRepoCreateSchema(BaseSchema):
    """
    Schema for creating a new code repository association.
    """
    entity_type: EntityTypeEnum = Field(..., description="Type of the entity ('block' or 'edge').")
    entity_id: UUID = Field(..., description="UUID of the associated entity.")
    repo_url: str = Field(..., description="URL of the GitHub repository.")
    branch: Optional[str] = Field("main", description="Default branch of the repository.")


class CodeRepoResponseSchema(BaseSchema):
    """
    Schema for returning code repository association details.
    """
    repo_id: UUID = Field(..., description="Unique identifier for the code repository association.")
    entity_type: EntityTypeEnum = Field(..., description="Type of the associated entity.")
    entity_id: UUID = Field(..., description="UUID of the associated entity.")
    repo_url: str = Field(..., description="URL of the GitHub repository.")
    branch: str = Field(..., description="Default branch of the repository.")
    last_updated: datetime = Field(..., description="Timestamp of the last repository update.")


# -------------------
# Docker Image Schemas
# -------------------

class DockerImageCreateSchema(BaseSchema):
    """
    Schema for creating a new Docker image association.
    """
    entity_type: EntityTypeEnum = Field(..., description="Type of the entity ('block' or 'edge').")
    entity_id: UUID = Field(..., description="UUID of the associated entity.")
    image_tag: str = Field(..., description="Tag of the Docker image (e.g., 'v1.0.0').")
    registry_url: str = Field(..., description="URL of the Docker registry.")


class DockerImageResponseSchema(BaseSchema):
    """
    Schema for returning Docker image association details.
    """
    image_id: UUID = Field(..., description="Unique identifier for the Docker image association.")
    entity_type: EntityTypeEnum = Field(..., description="Type of the associated entity.")
    entity_id: UUID = Field(..., description="UUID of the associated entity.")
    image_tag: str = Field(..., description="Tag of the Docker image.")
    registry_url: str = Field(..., description="URL of the Docker registry.")
    build_status: BuildStatusEnum = Field(..., description="Status of the Docker image build.")
    build_logs: Optional[str] = Field(None, description="Logs from the Docker image build process.")
    created_at: datetime = Field(..., description="Timestamp when the Docker image was created.")
    updated_at: datetime = Field(..., description="Timestamp when the Docker image was last updated.")


# -------------------
# Dependency Schemas
# -------------------

class DependencyCreateSchema(BaseSchema):
    """
    Schema for creating a new dependency association.
    """
    entity_type: EntityTypeEnum = Field(..., description="Type of the entity ('block' or 'edge').")
    entity_id: UUID = Field(..., description="UUID of the associated entity.")
    dependency_type: DependencyTypeEnum = Field(..., description="Type of the dependency ('internal' or 'external').")
    dependency_detail: str = Field(..., description="Detailed information about the dependency.")


class DependencyResponseSchema(BaseSchema):
    """
    Schema for returning dependency association details.
    """
    dependency_id: UUID = Field(..., description="Unique identifier for the dependency association.")
    entity_type: EntityTypeEnum = Field(..., description="Type of the associated entity.")
    entity_id: UUID = Field(..., description="UUID of the associated entity.")
    dependency_type: DependencyTypeEnum = Field(..., description="Type of the dependency.")
    dependency_detail: str = Field(..., description="Detailed information about the dependency.")


# -------------------
# Edge Schemas
# -------------------

class EdgeCreateSchema(BaseSchema):
    """
    Schema for creating a new edge.
    """
    name: str = Field(..., description="Unique name for the edge.")
    edge_type: EdgeTypeEnum = Field(..., description="Type of the edge.")
    description: Optional[str] = Field(None, description="Description of the edge.")
    created_by: Optional[UUID] = Field(None, description="UUID of the user creating the edge.")

    @field_validator('name')
    def name_no_spaces(cls, v):
        """
        Ensures the edge name does not contain spaces.
        """
        if ' ' in v:
            raise ValueError('Edge name must not contain spaces')
        return v

    @field_validator('edge_type')
    def validate_edge_type(cls, v):
        """
        Validates the edge type against the EdgeTypeEnum.
        """
        if not EdgeTypeEnum.has_value(v):
            raise ValueError(f'Invalid edge_type: {v}')
        return v


class EdgeUpdateSchema(BaseSchema):
    """
    Schema for updating an existing edge.
    """
    name: Optional[str] = Field(None, description="New name for the edge.")
    edge_type: Optional[EdgeTypeEnum] = Field(None, description="New type for the edge.")
    description: Optional[str] = Field(None, description="New description for the edge.")

    @field_validator('name')
    def name_no_spaces(cls, v):
        """
        Ensures the new edge name does not contain spaces.
        """
        if v and ' ' in v:
            raise ValueError('Edge name must not contain spaces')
        return v

    @field_validator('edge_type')
    def validate_edge_type(cls, v):
        """
        Validates the new edge type against the EdgeTypeEnum.
        """
        if v and not EdgeTypeEnum.has_value(v):
            raise ValueError(f'Invalid edge_type: {v}')
        return v


class EdgeResponseSchema(BaseSchema):
    """
    Schema for returning edge details.
    """
    edge_id: UUID = Field(..., description="Unique identifier for the edge.")
    name: str = Field(..., description="Name of the edge.")
    edge_type: EdgeTypeEnum = Field(..., description="Type of the edge.")
    description: Optional[str] = Field(None, description="Description of the edge.")
    current_version_id: Optional[UUID] = Field(None, description="UUID of the current version of the edge.")
    created_at: datetime = Field(..., description="Timestamp when the edge was created.")
    updated_at: datetime = Field(..., description="Timestamp when the edge was last updated.")
    created_by: Optional[UUID] = Field(None, description="UUID of the user who created the edge.")


# -------------------
# Edge Version Schemas
# -------------------

class EdgeVersionCreateSchema(BaseSchema):
    """
    Schema for creating a new edge version.
    """
    edge_id: UUID = Field(..., description="UUID of the edge to which this version belongs.")
    version_number: int = Field(..., description="Sequential version number.")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Metadata specific to this edge version.")
    created_by: UUID = Field(..., description="UUID of the user creating this version.")


class EdgeVersionResponseSchema(BaseSchema):
    """
    Schema for returning edge version details.
    """
    version_id: UUID = Field(..., description="Unique identifier for the edge version.")
    edge_id: UUID = Field(..., description="UUID of the associated edge.")
    version_number: int = Field(..., description="Sequential version number.")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Metadata specific to this edge version.")
    created_at: datetime = Field(..., description="Timestamp when the version was created.")
    created_by: UUID = Field(..., description="UUID of the user who created this version.")
    is_active: bool = Field(..., description="Indicator if this is the active version.")


# -------------------
# Edge Verification Schemas
# -------------------

class EdgeVerificationCreateSchema(BaseSchema):
    """
    Schema for creating a new edge verification.
    """
    edge_version_id: UUID = Field(..., description="UUID of the edge version being verified.")
    verification_status: VerificationStatusEnum = Field(..., description="Status of the verification ('pending', 'passed', 'failed').")
    verification_logs: Optional[str] = Field(None, description="Logs from the verification process.")
    verified_by: Optional[UUID] = Field(None, description="UUID of the user who performed the verification.")


class EdgeVerificationResponseSchema(BaseSchema):
    """
    Schema for returning edge verification details.
    """
    verification_id: UUID = Field(..., description="Unique identifier for the edge verification.")
    edge_version_id: UUID = Field(..., description="UUID of the edge version being verified.")
    verification_status: VerificationStatusEnum = Field(..., description="Status of the verification.")
    verification_logs: Optional[str] = Field(None, description="Logs from the verification process.")
    verified_at: Optional[datetime] = Field(None, description="Timestamp when the verification was completed.")
    verified_by: Optional[UUID] = Field(None, description="UUID of the user who performed the verification.")
    created_at: datetime = Field(..., description="Timestamp when the verification was created.")
    updated_at: datetime = Field(..., description="Timestamp when the verification was last updated.")


# -------------------
# Pipeline Schemas
# -------------------

class PipelineCreateSchema(BaseSchema):
    """
    Schema for creating a new pipeline.
    """
    name: str = Field(..., description="Unique name for the pipeline.")
    description: Optional[str] = Field(None, description="Description of the pipeline.")
    dagster_pipeline_config: Optional[Dict[str, Any]] = Field(None, description="Dagster-specific configuration for the pipeline.")
    created_by: UUID = Field(..., description="UUID of the user creating the pipeline.")


class PipelineUpdateSchema(BaseSchema):
    """
    Schema for updating an existing pipeline.
    """
    name: Optional[str] = Field(None, description="New name for the pipeline.")
    description: Optional[str] = Field(None, description="New description for the pipeline.")
    dagster_pipeline_config: Optional[Dict[str, Any]] = Field(None, description="New Dagster-specific configuration for the pipeline.")
    times_run: Optional[int] = Field(None, description="Total number of times the pipeline has run.")
    average_runtime: Optional[float] = Field(None, description="Average runtime of pipeline executions.")


class PipelineResponseSchema(BaseSchema):
    """
    Schema for returning pipeline details.
    """
    pipeline_id: UUID = Field(..., description="Unique identifier for the pipeline.")
    name: str = Field(..., description="Name of the pipeline.")
    description: Optional[str] = Field(None, description="Description of the pipeline.")
    created_at: datetime = Field(..., description="Timestamp when the pipeline was created.")
    updated_at: datetime = Field(..., description="Timestamp when the pipeline was last updated.")
    dagster_pipeline_config: Optional[Dict[str, Any]] = Field(None, description="Dagster-specific configuration for the pipeline.")
    created_by: UUID = Field(..., description="UUID of the user who created the pipeline.")
    times_run: int = Field(..., description="Total number of times the pipeline has run.")
    average_runtime: float = Field(..., description="Average runtime of pipeline executions.")


# -------------------
# Pipeline Block Schemas
# -------------------

class PipelineBlockCreateSchema(BaseSchema):
    """
    Schema for associating a block with a pipeline.
    """
    pipeline_id: UUID = Field(..., description="UUID of the pipeline.")
    block_id: UUID = Field(..., description="UUID of the block to include in the pipeline.")


class PipelineBlockResponseSchema(BaseSchema):
    """
    Schema for returning pipeline-block association details.
    """
    pipeline_block_id: UUID = Field(..., description="Unique identifier for the pipeline-block association.")
    pipeline_id: UUID = Field(..., description="UUID of the associated pipeline.")
    block_id: UUID = Field(..., description="UUID of the associated block.")
    created_at: datetime = Field(..., description="Timestamp when the association was created.")
    updated_at: datetime = Field(..., description="Timestamp when the association was last updated.")


# -------------------
# Pipeline Edge Schemas
# -------------------

class PipelineEdgeCreateSchema(BaseSchema):
    """
    Schema for associating an edge with a pipeline.
    """
    pipeline_id: UUID = Field(..., description="UUID of the pipeline.")
    edge_id: UUID = Field(..., description="UUID of the edge to include in the pipeline.")
    source_block_id: UUID = Field(..., description="UUID of the source block in the edge.")
    target_block_id: UUID = Field(..., description="UUID of the target block in the edge.")


class PipelineEdgeResponseSchema(BaseSchema):
    """
    Schema for returning pipeline-edge association details.
    """
    pipeline_edge_id: UUID = Field(..., description="Unique identifier for the pipeline-edge association.")
    pipeline_id: UUID = Field(..., description="UUID of the associated pipeline.")
    edge_id: UUID = Field(..., description="UUID of the associated edge.")
    source_block_id: UUID = Field(..., description="UUID of the source block in the edge.")
    target_block_id: UUID = Field(..., description="UUID of the target block in the edge.")
    created_at: datetime = Field(..., description="Timestamp when the association was created.")
    updated_at: datetime = Field(..., description="Timestamp when the association was last updated.")


# -------------------
# Vector Representation Schemas
# -------------------

class VectorRepresentationSchema(BaseSchema):
    """
    Schema representing a vector embedding associated with an entity (block or edge).
    """
    vector_id: UUID = Field(..., description="Unique identifier for the vector embedding.")
    entity_type: str = Field(..., description="Type of the entity ('block' or 'edge').")
    entity_id: UUID = Field(..., description="UUID of the associated entity.")
    vector: List[float] = Field(..., description="Vector embedding (e.g., 512-dimensional).")
    taxonomy_filter: Optional[Dict[str, Any]] = Field(None, description="Taxonomy constraints for RAG search.")
    created_at: datetime = Field(..., description="Timestamp when the vector was created.")
    updated_at: datetime = Field(..., description="Timestamp when the vector was last updated.")

class VectorRepresentationResponseSchema(VectorRepresentationSchema):
    """
    Schema for returning vector embedding details.
    """
    pass


class VectorRepresentationCreateSchema(BaseSchema):
    """
    Schema for creating a new vector embedding.
    """
    entity_type: str = Field(..., description="Type of the entity ('block' or 'edge').")
    entity_id: UUID = Field(..., description="UUID of the associated entity.")
    vector: List[float] = Field(..., description="Vector embedding (e.g., 512-dimensional).")
    taxonomy_filter: Optional[Dict[str, Any]] = Field(None, description="Taxonomy constraints for RAG search.")


# -------------------
# Audit Log Schemas
# -------------------

class AuditLogCreateSchema(BaseSchema):
    """
    Schema for creating a new audit log entry.
    """
    user_id: UUID = Field(..., description="UUID of the user performing the action.")
    action_type: ActionTypeEnum = Field(..., description="Type of action performed (e.g., 'CREATE', 'READ').")
    entity_type: AuditEntityTypeEnum = Field(..., description="Type of the entity involved (e.g., 'block', 'edge').")
    entity_id: UUID = Field(..., description="UUID of the affected entity.")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional details about the action.")


class AuditLogResponseSchema(BaseSchema):
    """
    Schema for returning audit log entry details.
    """
    log_id: UUID = Field(..., description="Unique identifier for the audit log entry.")
    user_id: UUID = Field(..., description="UUID of the user who performed the action.")
    action_type: ActionTypeEnum = Field(..., description="Type of action performed.")
    entity_type: AuditEntityTypeEnum = Field(..., description="Type of the entity involved.")
    entity_id: UUID = Field(..., description="UUID of the affected entity.")
    timestamp: datetime = Field(..., description="Timestamp when the action was performed.")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional details about the action.")
