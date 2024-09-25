from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Integer, Text, Float
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID, ENUM
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from enum import Enum as PyEnum


# -------------------
# Enum Definitions
# -------------------

class BlockTypeEnum(PyEnum):
    dataset = 'dataset'
    model = 'model'

class EdgeTypeEnum(PyEnum):
    primary = 'primary'
    secondary = 'secondary'
    tertiary = 'tertiary'

class EntityTypeEnum(PyEnum):
    block = 'block'
    edge = 'edge'

class BuildStatusEnum(PyEnum):
    pending = 'pending'
    success = 'success'
    failed = 'failed'

class DependencyTypeEnum(PyEnum):
    internal = 'internal'
    external = 'external'

class VerificationStatusEnum(PyEnum):
    pending = 'pending'
    passed = 'passed'
    failed = 'failed'

class ActionTypeEnum(PyEnum):
    CREATE = 'CREATE'
    READ = 'READ'
    UPDATE = 'UPDATE'
    DELETE = 'DELETE'

class AuditEntityTypeEnum(PyEnum):
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

class User(Base):
    __tablename__ = 'users'
    
    user_id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String, nullable=False)
    email = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False)  # This can be converted to an ENUM if necessary
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    api_keys = relationship('APIKey', back_populates='user')

class APIKey(Base):
    __tablename__ = 'api_keys'
    
    api_key_id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(PostgresUUID(as_uuid=True), ForeignKey('users.user_id'), nullable=False)
    encrypted_api_key = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    user = relationship('User', back_populates='api_keys')

class TaxonomyCategory(Base):
    __tablename__ = 'taxonomy_categories'
    
    category_id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    parent_id = Column(PostgresUUID(as_uuid=True), ForeignKey('taxonomy_categories.category_id'), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

class Block(Base):
    __tablename__ = 'blocks'
    
    block_id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    block_type = Column(ENUM(BlockTypeEnum, name='block_type_enum'), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = Column(PostgresUUID(as_uuid=True), nullable=True)
    
    versions = relationship('BlockVersion', back_populates='block')

class BlockVersion(Base):
    __tablename__ = 'block_versions'
    
    version_id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    block_id = Column(PostgresUUID(as_uuid=True), ForeignKey('blocks.block_id'), nullable=False)
    version_number = Column(Integer, nullable=False)
    metadata = Column(Text, nullable=True)  # Optional dict can be stored as JSON
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_by = Column(PostgresUUID(as_uuid=True), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    block = relationship('Block', back_populates='versions')

class BlockTaxonomy(Base):
    __tablename__ = 'block_taxonomies'
    
    block_taxonomy_id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    block_id = Column(PostgresUUID(as_uuid=True), ForeignKey('blocks.block_id'), nullable=False)
    category_id = Column(PostgresUUID(as_uuid=True), ForeignKey('taxonomy_categories.category_id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

class CodeRepo(Base):
    __tablename__ = 'code_repos'
    
    repo_id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_type = Column(ENUM(EntityTypeEnum, name='entity_type_enum'), nullable=False)
    entity_id = Column(PostgresUUID(as_uuid=True), nullable=False)
    repo_url = Column(String, nullable=False)
    branch = Column(String, nullable=False)
    last_updated = Column(DateTime, default=datetime.utcnow, nullable=False)

class DockerImage(Base):
    __tablename__ = 'docker_images'
    
    image_id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_type = Column(ENUM(EntityTypeEnum, name='entity_type_enum'), nullable=False)
    entity_id = Column(PostgresUUID(as_uuid=True), nullable=False)
    image_tag = Column(String, nullable=False)
    registry_url = Column(String, nullable=False)
    build_status = Column(ENUM(BuildStatusEnum, name='build_status_enum'), nullable=False)
    build_logs = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

class Dependency(Base):
    __tablename__ = 'dependencies'
    
    dependency_id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_type = Column(ENUM(EntityTypeEnum, name='entity_type_enum'), nullable=False)
    entity_id = Column(PostgresUUID(as_uuid=True), nullable=False)
    dependency_type = Column(ENUM(DependencyTypeEnum, name='dependency_type_enum'), nullable=False)
    dependency_detail = Column(Text, nullable=False)

class Edge(Base):
    __tablename__ = 'edges'
    
    edge_id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    edge_type = Column(ENUM(EdgeTypeEnum, name='edge_type_enum'), nullable=False)
    description = Column(Text, nullable=True)
    current_version_id = Column(PostgresUUID(as_uuid=True), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    versions = relationship('EdgeVersion', back_populates='edge')

class EdgeVersion(Base):
    __tablename__ = 'edge_versions'
    
    version_id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    edge_id = Column(PostgresUUID(as_uuid=True), ForeignKey('edges.edge_id'), nullable=False)
    version_number = Column(Integer, nullable=False)
    metadata = Column(Text, nullable=True)  # Optional dict can be stored as JSON
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_by = Column(PostgresUUID(as_uuid=True), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    edge = relationship('Edge', back_populates='versions')

class EdgeVerification(Base):
    __tablename__ = 'edge_verifications'
    
    verification_id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    edge_version_id = Column(PostgresUUID(as_uuid=True), ForeignKey('edge_versions.version_id'), nullable=False)
    verification_status = Column(ENUM(VerificationStatusEnum, name='verification_status_enum'), nullable=False)
    verification_logs = Column(Text, nullable=True)
    verified_at = Column(DateTime, nullable=True)
    verified_by = Column(PostgresUUID(as_uuid=True), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

class Pipeline(Base):
    __tablename__ = 'pipelines'
    
    pipeline_id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    dagster_pipeline_config = Column(Text, nullable=True)  # Optional dict as JSON
    created_by = Column(PostgresUUID(as_uuid=True), nullable=False)
    times_run = Column(Integer, default=0, nullable=False)
    average_runtime = Column(Float, default=0.0, nullable=False)

class PipelineBlock(Base):
    __tablename__ = 'pipeline_blocks'
    
    pipeline_block_id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pipeline_id = Column(PostgresUUID(as_uuid=True), ForeignKey('pipelines.pipeline_id'), nullable=False)
    block_id = Column(PostgresUUID(as_uuid=True), ForeignKey('blocks.block_id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

class PipelineEdge(Base):
    __tablename__ = 'pipeline_edges'
    
    pipeline_edge_id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pipeline_id = Column(PostgresUUID(as_uuid=True), ForeignKey('pipelines.pipeline_id'), nullable=False)
    edge_id = Column(PostgresUUID(as_uuid=True), ForeignKey('edges.edge_id'), nullable=False)
    source_block_id = Column(PostgresUUID(as_uuid=True), nullable=False)
    target_block_id = Column(PostgresUUID(as_uuid=True), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

class BlockVectorRepresentation(Base):
    __tablename__ = 'block_vector_representations'
    
    vector_id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    block_id = Column(PostgresUUID(as_uuid=True), ForeignKey('blocks.block_id'), nullable=False)
    vector_db = Column(String, nullable=False)
    vector_key = Column(String, nullable=False)
    taxonomy_filter = Column(Text, nullable=True)  # Optional dict as JSON
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

class EdgeVectorRepresentation(Base):
    __tablename__ = 'edge_vector_representations'
    
    vector_id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    edge_id = Column(PostgresUUID(as_uuid=True), ForeignKey('edges.edge_id'), nullable=False)
    vector_db = Column(String, nullable=False)
    vector_key = Column(String, nullable=False)
    taxonomy_filter = Column(Text, nullable=True)  # Optional dict as JSON
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

class AuditLog(Base):
    __tablename__ = 'audit_logs'
    
    log_id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(PostgresUUID(as_uuid=True), ForeignKey('users.user_id'), nullable=False)
    action_type = Column(ENUM(ActionTypeEnum, name='action_type_enum'), nullable=False)
    entity_type = Column(ENUM(AuditEntityTypeEnum, name='audit_entity_type_enum'), nullable=False)
    entity_id = Column(PostgresUUID(as_uuid=True), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    details = Column(Text, nullable=True)  # Optional dict as JSON
