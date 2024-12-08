# constellation-backend/api/backend/app/schemas.py

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime

from prisma.enums import (
    BlockTypeEnum,
    ActionTypeEnum,
    AuditEntityTypeEnum,
    VerificationStatusEnum,
)


# -------------------
# User Schemas
# -------------------


class UserCreateInput(BaseModel):
    username: str = Field(..., description="Unique username for the user.")
    email: EmailStr = Field(..., description="Valid email address for the user.")
    password: str = Field(..., description="Password for the user account.")

    @validator("password")
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        # Add more checks as needed
        return v


# -------------------
# Block Schemas
# -------------------


class BlockCreateSchema(BaseModel):
    name: str = Field(..., description="Unique name of the block.")
    block_type: BlockTypeEnum = Field(
        ..., description="Type of the block (dataset or model)."
    )
    description: Optional[str] = Field(None, description="Description of the block.")
    vector: Optional[List[float]] = Field(
        None, description="Optional vector representation of the block."
    )

    class Config:
        orm_mode = True


class BlockUpdateSchema(BaseModel):
    name: Optional[str] = Field(None, description="Unique name of the block.")
    block_type: Optional[BlockTypeEnum] = Field(
        None, description="Type of the block (dataset or model)."
    )
    description: Optional[str] = Field(None, description="Description of the block.")
    vector: Optional[List[float]] = Field(
        None, description="Optional vector representation of the block."
    )

    class Config:
        orm_mode = True


class BlockResponseSchema(BaseModel):
    block_id: UUID
    name: str
    block_type: BlockTypeEnum
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    vector: Optional[List[float]] = None

    class Config:
        orm_mode = True


# -------------------
# Edge Schemas
# -------------------


class EdgeCreateSchema(BaseModel):
    source_block_id: UUID = Field(..., description="UUID of the source block.")
    target_block_id: UUID = Field(..., description="UUID of the target block.")
    created_by: UUID = Field(..., description="UUID of the user creating the edge.")

    class Config:
        orm_mode = True


class EdgeUpdateSchema(BaseModel):
    source_block_id: Optional[UUID] = Field(
        None, description="UUID of the source block."
    )
    target_block_id: Optional[UUID] = Field(
        None, description="UUID of the target block."
    )
    updated_by: UUID = Field(..., description="UUID of the user updating the edge.")

    class Config:
        orm_mode = True


class EdgeResponseSchema(BaseModel):
    edge_id: UUID
    source_block_id: UUID
    target_block_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


# -------------------
# Edge Verification Schemas
# -------------------


class EdgeVerificationRequestSchema(BaseModel):
    source_block_id: UUID = Field(..., description="UUID of the source block.")
    target_block_id: UUID = Field(..., description="UUID of the target block.")

    class Config:
        orm_mode = True


class EdgeVerificationResponseSchema(BaseModel):
    can_connect: bool
    message: Optional[str] = Field(
        None, description="Additional information about the verification result."
    )

    class Config:
        orm_mode = True


# -------------------
# Assign Version Schemas
# -------------------


class AssignVersionSchema(BaseModel):
    version_id: UUID = Field(..., description="UUID of the version to assign.")

    class Config:
        orm_mode = True


# -------------------
# Audit Log Schemas
# -------------------


class AuditLogSchema(BaseModel):
    log_id: UUID
    user_id: UUID
    action_type: ActionTypeEnum
    entity_type: AuditEntityTypeEnum
    entity_id: UUID
    timestamp: datetime
    details: Dict[str, Any]

    class Config:
        orm_mode = True


# -------------------
# Audit Log Schemas
# -------------------


class AuditLogCreateSchema(BaseModel):
    user_id: UUID = Field(..., description="UUID of the user performing the action.")
    action_type: ActionTypeEnum = Field(..., description="Type of action performed.")
    entity_type: AuditEntityTypeEnum = Field(
        ..., description="Type of entity being acted upon."
    )
    entity_id: UUID = Field(..., description="UUID of the entity.")
    details: Dict[str, Any] = Field(
        ..., description="Additional details about the action."
    )

    class Config:
        orm_mode = True


class AuditLogResponseSchema(AuditLogSchema):
    pass


class AuditLogUpdateSchema(BaseModel):
    user_id: Optional[UUID] = Field(
        None, description="UUID of the user performing the action."
    )
    action_type: Optional[ActionTypeEnum] = Field(
        None, description="Type of action performed."
    )
    entity_type: Optional[AuditEntityTypeEnum] = Field(
        None, description="Type of entity being acted upon."
    )
    entity_id: Optional[UUID] = Field(None, description="UUID of the entity.")
    details: Optional[Dict[str, Any]] = Field(
        None, description="Additional details about the action."
    )

    class Config:
        orm_mode = True
