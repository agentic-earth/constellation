# app/models.py

from pydantic import BaseModel, EmailStr
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from enum import Enum


# -------------------
# Enum Definitions
# -------------------

class BlockTypeEnum(str, Enum):
    dataset = 'dataset'
    model = 'model'


class EntityTypeEnum(str, Enum):
    block = 'block'
    edge = 'edge'


class BuildStatusEnum(str, Enum):
    pending = 'pending'
    success = 'success'
    failed = 'failed'


class DependencyTypeEnum(str, Enum):
    internal = 'internal'
    external = 'external'


class VerificationStatusEnum(str, Enum):
    pending = 'pending'
    passed = 'passed'
    failed = 'failed'


class ActionTypeEnum(str, Enum):
    CREATE = 'CREATE'
    READ = 'READ'
    UPDATE = 'UPDATE'
    DELETE = 'DELETE'


class AuditEntityTypeEnum(str, Enum):
    block = 'block'
    edge = 'edge'
    pipeline = 'pipeline'
    taxonomy = 'taxonomy'
    metadata = 'metadata'
    user = 'user'
    api_key = 'api_key'
    code_repo = 'code_repo'
    docker_image = 'docker_image'
    verification = 'verification'


# -------------------
# Model Definitions
# -------------------

class User(BaseModel):
    user_id: UUID
    username: str
    email: EmailStr
    password_hash: str
    role: str  # Consider using Enum for roles
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class APIKey(BaseModel):
    api_key_id: UUID
    user_id: UUID
    encrypted_api_key: str
    created_at: datetime
    expires_at: datetime
    is_active: bool

    class Config:
        orm_mode = True


class TaxonomyCategory(BaseModel):
    category_id: UUID
    name: str
    parent_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class Block(BaseModel):
    block_id: UUID
    name: str
    block_type: BlockTypeEnum
    description: Optional[str]
    created_at: datetime
    updated_at: datetime
    current_version_id: Optional[UUID]

    class Config:
        orm_mode = True


class BlockVersion(BaseModel):
    version_id: UUID
    block_id: UUID
    version_number: int
    metadata: Optional[dict]
    created_at: datetime
    created_by: UUID
    is_active: bool

    class Config:
        orm_mode = True


class BlockTaxonomy(BaseModel):
    block_taxonomy_id: UUID
    block_id: UUID
    category_id: UUID
    created_at: datetime

    class Config:
        orm_mode = True


class CodeRepo(BaseModel):
    repo_id: UUID
    entity_type: EntityTypeEnum
    entity_id: UUID
    repo_url: str
    branch: str
    last_updated: datetime

    class Config:
        orm_mode = True


class DockerImage(BaseModel):
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


class Dependency(BaseModel):
    dependency_id: UUID
    entity_type: EntityTypeEnum
    entity_id: UUID
    dependency_type: DependencyTypeEnum
    dependency_detail: str

    class Config:
        orm_mode = True


class Edge(BaseModel):
    edge_id: UUID
    name: str
    description: Optional[str]
    current_version_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class EdgeVersion(BaseModel):
    version_id: UUID
    edge_id: UUID
    version_number: int
    metadata: Optional[dict]
    created_at: datetime
    created_by: UUID
    is_active: bool

    class Config:
        orm_mode = True


class EdgeVerification(BaseModel):
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


class Pipeline(BaseModel):
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


class PipelineBlock(BaseModel):
    pipeline_block_id: UUID
    pipeline_id: UUID
    block_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class PipelineEdge(BaseModel):
    pipeline_edge_id: UUID
    pipeline_id: UUID
    edge_id: UUID
    source_block_id: UUID
    target_block_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class BlockVectorRepresentation(BaseModel):
    vector_id: UUID
    block_id: UUID
    vector_db: str
    vector_key: str
    taxonomy_filter: Optional[dict]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class EdgeVectorRepresentation(BaseModel):
    vector_id: UUID
    edge_id: UUID
    vector_db: str
    vector_key: str
    taxonomy_filter: Optional[dict]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class AuditLog(BaseModel):
    log_id: UUID
    user_id: UUID
    action_type: ActionTypeEnum
    entity_type: AuditEntityTypeEnum
    entity_id: UUID
    timestamp: datetime
    details: Optional[dict]

    class Config:
        orm_mode = True
