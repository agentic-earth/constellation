# app/routes/audit_logs.py

"""
Audit Log Routes Module

This module defines all API endpoints related to audit log operations, including creating, retrieving,
updating, deleting audit logs. It leverages the AuditController to perform business logic and interact
with the services layer. All operations are logged using the Constellation Logger.

Responsibilities:
- Define HTTP endpoints for audit log-related operations.
- Validate and parse incoming request data using Pydantic schemas.
- Delegate request handling to the AuditController.
- Handle and respond to errors appropriately.

Design Philosophy:
- Maintain thin Routes by delegating complex logic to Controllers.
- Ensure clear separation between HTTP handling and business logic.
"""

from fastapi import APIRouter, HTTPException
from typing import List, Optional
from uuid import UUID
from app.controllers.audit_controller import AuditController
from app.schemas import (
    AuditLogCreateSchema,
    AuditLogUpdateSchema,
    AuditLogResponseSchema
)

router = APIRouter(
    prefix="/audit-logs",
    tags=["Audit Logs"],
    responses={404: {"description": "Not found"}},
)

# Initialize the AuditController instance
audit_controller = AuditController()

# -------------------
# Basic Audit Log Endpoints
# -------------------

@router.post("/", response_model=AuditLogResponseSchema, status_code=201)
def create_audit_log(audit_log: AuditLogCreateSchema):
    """
    Create a new audit log entry.

    Args:
        audit_log (AuditLogCreateSchema): The data required to create a new audit log.

    Returns:
        AuditLogResponseSchema: The created audit log's data.
    """
    created_audit_log = audit_controller.create_audit_log(audit_log)
    if not created_audit_log:
        raise HTTPException(status_code=400, detail="Audit log creation failed.")
    return created_audit_log

@router.get("/{log_id}", response_model=AuditLogResponseSchema)
def get_audit_log(log_id: UUID):
    """
    Retrieve an audit log by its UUID.

    Args:
        log_id (UUID): The UUID of the audit log to retrieve.

    Returns:
        AuditLogResponseSchema: The audit log's data if found.
    """
    audit_log = audit_controller.get_audit_log_by_id(log_id)
    if not audit_log:
        raise HTTPException(status_code=404, detail="Audit log not found.")
    return audit_log

@router.put("/{log_id}", response_model=AuditLogResponseSchema)
def update_audit_log(log_id: UUID, audit_log_update: AuditLogUpdateSchema):
    """
    Update an existing audit log's information.

    Args:
        log_id (UUID): The UUID of the audit log to update.
        audit_log_update (AuditLogUpdateSchema): The data to update for the audit log.

    Returns:
        AuditLogResponseSchema: The updated audit log's data if successful.
    """
    updated_audit_log = audit_controller.update_audit_log(log_id, audit_log_update)
    if not updated_audit_log:
        raise HTTPException(status_code=400, detail="Audit log update failed.")
    return updated_audit_log

@router.delete("/{log_id}", status_code=204)
def delete_audit_log(log_id: UUID):
    """
    Delete an audit log by its UUID.

    Args:
        log_id (UUID): The UUID of the audit log to delete.

    Returns:
        HTTP 204 No Content: If deletion was successful.
    """
    success = audit_controller.delete_audit_log(log_id)
    if not success:
        raise HTTPException(status_code=404, detail="Audit log not found or already deleted.")
    return

@router.get("/", response_model=List[AuditLogResponseSchema])
def list_audit_logs(action_type: Optional[str] = None, user_id: Optional[UUID] = None, entity_type: Optional[str] = None):
    """
    List audit logs with optional filtering by action type, user ID, and entity type.

    Args:
        action_type (Optional[str]): Filter audit logs by action type.
        user_id (Optional[UUID]): Filter audit logs by user ID.
        entity_type (Optional[str]): Filter audit logs by entity type.

    Returns:
        List[AuditLogResponseSchema]: A list of audit logs matching the filters.
    """
    filters = {}
    if action_type:
        filters["action_type"] = action_type
    if user_id:
        filters["user_id"] = str(user_id)
    if entity_type:
        filters["entity_type"] = entity_type
    audit_logs = audit_controller.list_audit_logs(filters)
    if audit_logs is None:
        raise HTTPException(status_code=500, detail="Failed to retrieve audit logs.")
    return audit_logs
