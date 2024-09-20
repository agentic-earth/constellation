# app/schemas.py

from pydantic import BaseModel, EmailStr, validator
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


# -------------------
# User Schemas
# -------------------

class UserCreateSchema(BaseModel):
    username: str
    email: EmailStr
    password: str

    @validator('password')
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        # Add more checks (e.g., uppercase, numbers, special characters) if needed
        return v

    @validator('username')
    def username_no_spaces(cls, v):
        if ' ' in v:
            raise ValueError('Username must not contain spaces')
        return v


class UserUpdateSchema(BaseModel):
    username: Optional[str]
    email: Optional[EmailStr]
    password_hash: Optional[str]
    role: Optional[str]


class UserResponseSchema(BaseModel):
    user_id: UUID
    username: str
    email: EmailStr
    role: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
        exclude = ['password_hash']


# -------------------
# API Key Schemas
# -------------------

class APIKeyCreateSchema(BaseModel):
    user_id: UUID
    encrypted_api_key: str
    expires_at: datetime


class APIKeyResponseSchema(BaseModel):
    api_key_id: UUID
    user_id: UUID
    encrypted_api_key: str
    created_at: datetime
    expires_at: datetime
    is_active: bool

    class Config:
        orm_mode = True


# -------------------
# Taxonomy Category Schemas
# -------------------

class TaxonomyCategoryCreateSchema(BaseModel):
    name: str
    parent_id: Optional[UUID]


class TaxonomyCategoryResponseSchema(BaseModel):
    category_id: UUID
    name: str
    parent_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


# -------------------
# Block Schemas
# -------------------

class BlockCreateSchema(BaseModel):
    name: str
    block_type: BlockTypeEnum
    description: Optional[str]


class BlockUpdateSchema(BaseModel):
    name: Optional[str]
    block_type: Optional[BlockTypeEnum]
    description: Optional[str]


class BlockResponseSchema(BaseModel):
    block_id: UUID
    name: str
    block_type: BlockTypeEnum
    description: Optional[str]
    created_at: datetime
    updated_at: datetime
    current_version_id: Optional[UUID]

    class Config:
        orm_mode = True


# -------------------
# Block Version Schemas
# -------------------

class BlockVersionCreateSchema(BaseModel):
    block_id: UUID
    version_number: int
    metadata: Optional[dict]
    created_by: UUID


class BlockVersionResponseSchema(BaseModel):
    version_id: UUID
    block_id: UUID
    version_number: int
    metadata: Optional[dict]
    created_at: datetime
    created_by: UUID
    is_active: bool

    class Config:
        orm_mode = True


# -------------------
# Block Taxonomy Schemas
# -------------------

class BlockTaxonomyCreateSchema(BaseModel):
    block_id: UUID
    category_id: UUID


class BlockTaxonomyResponseSchema(BaseModel):
    block_taxonomy_id: UUID
    block_id: UUID
    category_id: UUID
    created_at: datetime

    class Config:
        orm_mode = True


# -------------------
# Code Repo Schemas
# -------------------

class CodeRepoCreateSchema(BaseModel):
    entity_type: EntityTypeEnum
    entity_id: UUID
    repo_url: str
    branch: Optional[str] = "main"


class CodeRepoResponseSchema(BaseModel):
    repo_id: UUID
    entity_type: EntityTypeEnum
    entity_id: UUID
    repo_url: str
    branch: str
    last_updated: datetime

    class Config:
        orm_mode = True


# -------------------
# Docker Image Schemas
# -------------------

class DockerImageCreateSchema(BaseModel):
    entity_type: EntityTypeEnum
    entity_id: UUID
    image_tag: str
    registry_url: str


class DockerImageResponseSchema(BaseModel):
    image_id: UUID
    entity_type: EntityTypeEnum
    entity_id: UUID
    image_tag: str
    registry_url: str
    build_status: BuildStatusEnum
    build_logs: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


# -------------------
# Dependency Schemas
# -------------------

class DependencyCreateSchema(BaseModel):
    entity_type: EntityTypeEnum
    entity_id: UUID
    dependency_type: DependencyTypeEnum
    dependency_detail: str


class DependencyResponseSchema(BaseModel):
    dependency_id: UUID
    entity_type: EntityTypeEnum
    entity_id: UUID
    dependency_type: DependencyTypeEnum
    dependency_detail: str

    class Config:
        orm_mode = True


# -------------------
# Edge Schemas
# -------------------

class EdgeCreateSchema(BaseModel):
    name: str
    description: Optional[str]


class EdgeUpdateSchema(BaseModel):
    name: Optional[str]
    description: Optional[str]


class EdgeResponseSchema(BaseModel):
    edge_id: UUID
    name: str
    description: Optional[str]
    current_version_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


# -------------------
# Edge Version Schemas
# -------------------

class EdgeVersionCreateSchema(BaseModel):
    edge_id: UUID
    version_number: int
    metadata: Optional[dict]
    created_by: UUID


class EdgeVersionResponseSchema(BaseModel):
    version_id: UUID
    edge_id: UUID
    version_number: int
    metadata: Optional[dict]
    created_at: datetime
    created_by: UUID
    is_active: bool

    class Config:
        orm_mode = True


# -------------------
# Edge Verification Schemas
# -------------------

class EdgeVerificationCreateSchema(BaseModel):
    edge_version_id: UUID
    verification_status: VerificationStatusEnum
    verification_logs: Optional[str]
    verified_by: Optional[UUID]


class EdgeVerificationResponseSchema(BaseModel):
    verification_id: UUID
    edge_version_id: UUID
    verification_status: VerificationStatusEnum
    verification_logs: Optional[str]
    verified_at: Optional[datetime]
    verified_by: Optional[UUID]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


# -------------------
# Pipeline Schemas
# -------------------

class PipelineCreateSchema(BaseModel):
    name: str
    description: Optional[str]
    dagster_pipeline_config: Optional[dict]
    created_by: UUID


class PipelineUpdateSchema(BaseModel):
    name: Optional[str]
    description: Optional[str]
    dagster_pipeline_config: Optional[dict]
    times_run: Optional[int]
    average_runtime: Optional[float]


class PipelineResponseSchema(BaseModel):
    pipeline_id: UUID
    name: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime
    dagster_pipeline_config: Optional[dict]
    created_by: UUID
    times_run: int
    average_runtime: float

    class Config:
        orm_mode = True


# -------------------
# Pipeline Block Schemas
# -------------------

class PipelineBlockCreateSchema(BaseModel):
    pipeline_id: UUID
    block_id: UUID


class PipelineBlockResponseSchema(BaseModel):
    pipeline_block_id: UUID
    pipeline_id: UUID
    block_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


# -------------------
# Pipeline Edge Schemas
# -------------------

class PipelineEdgeCreateSchema(BaseModel):
    pipeline_id: UUID
    edge_id: UUID
    source_block_id: UUID
    target_block_id: UUID


class PipelineEdgeResponseSchema(BaseModel):
    pipeline_edge_id: UUID
    pipeline_id: UUID
    edge_id: UUID
    source_block_id: UUID
    target_block_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


# -------------------
# Block Vector Representation Schemas
# -------------------

class BlockVectorRepresentationCreateSchema(BaseModel):
    block_id: UUID
    vector_db: str
    vector_key: str
    taxonomy_filter: Optional[dict]


class BlockVectorRepresentationResponseSchema(BaseModel):
    vector_id: UUID
    block_id: UUID
    vector_db: str
    vector_key: str
    taxonomy_filter: Optional[dict]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


# -------------------
# Edge Vector Representation Schemas
# -------------------

class EdgeVectorRepresentationCreateSchema(BaseModel):
    edge_id: UUID
    vector_db: str
    vector_key: str
    taxonomy_filter: Optional[dict]


class EdgeVectorRepresentationResponseSchema(BaseModel):
    vector_id: UUID
    edge_id: UUID
    vector_db: str
    vector_key: str
    taxonomy_filter: Optional[dict]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


# -------------------
# Audit Log Schemas
# -------------------

class AuditLogCreateSchema(BaseModel):
    user_id: UUID
    action_type: ActionTypeEnum
    entity_type: AuditEntityTypeEnum
    entity_id: UUID
    details: Optional[dict]


class AuditLogResponseSchema(BaseModel):
    log_id: UUID
    user_id: UUID
    action_type: ActionTypeEnum
    entity_type: AuditEntityTypeEnum
    entity_id: UUID
    timestamp: datetime
    details: Optional[dict]

    class Config:
        orm_mode = True
