# app/schemas.py

from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, List
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
)

# Base configuration for all schemas
class BaseSchema(BaseModel):
    class Config:
        from_attributes = True

# -------------------
# User Schemas
# -------------------

class UserCreateSchema(BaseSchema):
    username: str
    email: EmailStr
    password: str

    @field_validator('password')
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        # Add more checks (e.g., uppercase, numbers, special characters) if needed
        return v

    @field_validator('username')
    def username_no_spaces(cls, v):
        if ' ' in v:
            raise ValueError('Username must not contain spaces')
        return v

class UserUpdateSchema(BaseSchema):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password_hash: Optional[str] = None
    role: Optional[str] = None

class UserResponseSchema(BaseSchema):
    user_id: UUID
    username: str
    email: EmailStr
    role: str
    created_at: datetime
    updated_at: datetime

    class Config:
        exclude = ['password_hash']

# -------------------
# API Key Schemas
# -------------------

class APIKeyCreateSchema(BaseSchema):
    user_id: UUID
    encrypted_api_key: str
    expires_at: datetime

class APIKeyResponseSchema(BaseSchema):
    api_key_id: UUID
    user_id: UUID
    encrypted_api_key: str
    created_at: datetime
    expires_at: datetime
    is_active: bool

# -------------------
# Taxonomy Category Schemas
# -------------------

class TaxonomyCategoryCreateSchema(BaseSchema):
    name: str
    parent_id: Optional[UUID] = None

class TaxonomyCategoryResponseSchema(BaseSchema):
    category_id: UUID
    name: str
    parent_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime

# -------------------
# Block Schemas
# -------------------

class BlockCreateSchema(BaseSchema):
    name: str
    block_type: BlockTypeEnum
    description: Optional[str] = None
    created_by: Optional[UUID] = None

class BlockUpdateSchema(BaseSchema):
    name: Optional[str] = None
    block_type: Optional[BlockTypeEnum] = None
    description: Optional[str] = None

class BlockResponseSchema(BaseSchema):
    block_id: UUID
    name: str
    block_type: BlockTypeEnum
    description: Optional[str]
    created_at: datetime
    updated_at: datetime
    created_by: Optional[UUID] = None

# -------------------
# Block Version Schemas
# -------------------

class BlockVersionCreateSchema(BaseSchema):
    block_id: UUID
    version_number: int
    metadata: Optional[dict] = None
    created_by: UUID

class BlockVersionResponseSchema(BaseSchema):
    version_id: UUID
    block_id: UUID
    version_number: int
    metadata: Optional[dict]
    created_at: datetime
    created_by: UUID
    is_active: bool

# -------------------
# Block Taxonomy Schemas
# -------------------

class BlockTaxonomyCreateSchema(BaseSchema):
    block_id: UUID
    category_id: UUID

class BlockTaxonomyResponseSchema(BaseSchema):
    block_taxonomy_id: UUID
    block_id: UUID
    category_id: UUID
    created_at: datetime

# -------------------
# Code Repo Schemas
# -------------------

class CodeRepoCreateSchema(BaseSchema):
    entity_type: EntityTypeEnum
    entity_id: UUID
    repo_url: str
    branch: Optional[str] = "main"

class CodeRepoResponseSchema(BaseSchema):
    repo_id: UUID
    entity_type: EntityTypeEnum
    entity_id: UUID
    repo_url: str
    branch: str
    last_updated: datetime

# -------------------
# Docker Image Schemas
# -------------------

class DockerImageCreateSchema(BaseSchema):
    entity_type: EntityTypeEnum
    entity_id: UUID
    image_tag: str
    registry_url: str

class DockerImageResponseSchema(BaseSchema):
    image_id: UUID
    entity_type: EntityTypeEnum
    entity_id: UUID
    image_tag: str
    registry_url: str
    build_status: BuildStatusEnum
    build_logs: Optional[str]
    created_at: datetime
    updated_at: datetime

# -------------------
# Dependency Schemas
# -------------------

class DependencyCreateSchema(BaseSchema):
    entity_type: EntityTypeEnum
    entity_id: UUID
    dependency_type: DependencyTypeEnum
    dependency_detail: str

class DependencyResponseSchema(BaseSchema):
    dependency_id: UUID
    entity_type: EntityTypeEnum
    entity_id: UUID
    dependency_type: DependencyTypeEnum
    dependency_detail: str

# -------------------
# Edge Schemas
# -------------------

class EdgeCreateSchema(BaseSchema):
    name: str
    description: Optional[str] = None

class EdgeUpdateSchema(BaseSchema):
    name: Optional[str] = None
    description: Optional[str] = None

class EdgeResponseSchema(BaseSchema):
    edge_id: UUID
    name: str
    description: Optional[str]
    current_version_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime

# -------------------
# Edge Version Schemas
# -------------------

class EdgeVersionCreateSchema(BaseSchema):
    edge_id: UUID
    version_number: int
    metadata: Optional[dict] = None
    created_by: UUID

class EdgeVersionResponseSchema(BaseSchema):
    version_id: UUID
    edge_id: UUID
    version_number: int
    metadata: Optional[dict]
    created_at: datetime
    created_by: UUID
    is_active: bool

# -------------------
# Edge Verification Schemas
# -------------------

class EdgeVerificationCreateSchema(BaseSchema):
    edge_version_id: UUID
    verification_status: VerificationStatusEnum
    verification_logs: Optional[str] = None
    verified_by: Optional[UUID] = None

class EdgeVerificationResponseSchema(BaseSchema):
    verification_id: UUID
    edge_version_id: UUID
    verification_status: VerificationStatusEnum
    verification_logs: Optional[str]
    verified_at: Optional[datetime]
    verified_by: Optional[UUID]
    created_at: datetime
    updated_at: datetime

# -------------------
# Pipeline Schemas
# -------------------

class PipelineCreateSchema(BaseSchema):
    name: str
    description: Optional[str] = None
    dagster_pipeline_config: Optional[dict] = None
    created_by: UUID

class PipelineUpdateSchema(BaseSchema):
    name: Optional[str] = None
    description: Optional[str] = None
    dagster_pipeline_config: Optional[dict] = None
    times_run: Optional[int] = None
    average_runtime: Optional[float] = None

class PipelineResponseSchema(BaseSchema):
    pipeline_id: UUID
    name: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime
    dagster_pipeline_config: Optional[dict]
    created_by: UUID
    times_run: int
    average_runtime: float

# -------------------
# Pipeline Block Schemas
# -------------------

class PipelineBlockCreateSchema(BaseSchema):
    pipeline_id: UUID
    block_id: UUID

class PipelineBlockResponseSchema(BaseSchema):
    pipeline_block_id: UUID
    pipeline_id: UUID
    block_id: UUID
    created_at: datetime
    updated_at: datetime

# -------------------
# Pipeline Edge Schemas
# -------------------

class PipelineEdgeCreateSchema(BaseSchema):
    pipeline_id: UUID
    edge_id: UUID
    source_block_id: UUID
    target_block_id: UUID

class PipelineEdgeResponseSchema(BaseSchema):
    pipeline_edge_id: UUID
    pipeline_id: UUID
    edge_id: UUID
    source_block_id: UUID
    target_block_id: UUID
    created_at: datetime
    updated_at: datetime

# -------------------
# Block Vector Representation Schemas
# -------------------

class BlockVectorRepresentationCreateSchema(BaseSchema):
    block_id: UUID
    vector_db: str
    vector_key: str
    taxonomy_filter: Optional[dict] = None

class BlockVectorRepresentationResponseSchema(BaseSchema):
    vector_id: UUID
    block_id: UUID
    vector_db: str
    vector_key: str
    taxonomy_filter: Optional[dict]
    created_at: datetime
    updated_at: datetime

# -------------------
# Edge Vector Representation Schemas
# -------------------

class EdgeVectorRepresentationCreateSchema(BaseSchema):
    edge_id: UUID
    vector_db: str
    vector_key: str
    taxonomy_filter: Optional[dict] = None

class EdgeVectorRepresentationResponseSchema(BaseSchema):
    vector_id: UUID
    edge_id: UUID
    vector_db: str
    vector_key: str
    taxonomy_filter: Optional[dict]
    created_at: datetime
    updated_at: datetime

# -------------------
# Audit Log Schemas
# -------------------

class AuditLogCreateSchema(BaseSchema):
    user_id: UUID
    action_type: ActionTypeEnum
    entity_type: AuditEntityTypeEnum
    entity_id: UUID
    details: Optional[dict] = None

class AuditLogResponseSchema(BaseSchema):
    log_id: UUID
    user_id: UUID
    action_type: ActionTypeEnum
    entity_type: AuditEntityTypeEnum
    entity_id: UUID
    timestamp: datetime
    details: Optional[dict] = None
