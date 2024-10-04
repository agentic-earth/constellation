# app/services/audit_service.py

"""
Audit Service Module

This module encapsulates all audit log-related business logic and interactions with the Prisma ORM.
It provides functions to create, retrieve, list, and delete audit logs, ensuring that all operations are
logged appropriately using the Constellation Logger.

Design Philosophy:
- Utilize Prisma ORM for database operations, ensuring type safety and efficient queries.
- Use Python for advanced logic that cannot be handled directly by the database.
- Ensure flexibility to adapt to schema changes with minimal modifications.
"""

from typing import Optional, List, Dict, Any
from uuid import UUID
from prisma.models import AuditLog
from backend.app.schemas import AuditLogCreateSchema, AuditLogResponseSchema
from backend.app.logger import ConstellationLogger
from datetime import datetime
from prisma import Prisma


class AuditService:
    """
    AuditService class encapsulates all audit log-related operations.
    """

    def __init__(self):
        """
        Initializes the AuditService with the logger.
        """
        self.logger = ConstellationLogger()

    async def create_audit_log(self, tx: Prisma, audit_data: AuditLogCreateSchema) -> Optional[AuditLogResponseSchema]:
        """
        Creates a new audit log entry in the database.

        Args:
            tx (Prisma): The Prisma transaction object.
            audit_data (AuditLogCreateSchema): The data required to create a new audit log.

        Returns:
            Optional[AuditLogResponseSchema]: The created audit log data if successful, None otherwise.
        """
        try:
            data = audit_data.dict()
            created_audit = await tx.auditlog.create(data=data)

            if created_audit:
                audit_response = AuditLogResponseSchema(**created_audit.dict())
                self.logger.log(
                    "AuditService",
                    "info",
                    "Audit log created successfully",
                    log_id=audit_response.log_id,
                    user_id=audit_response.user_id,
                    action_type=audit_response.action_type,
                    entity_type=audit_response.entity_type,
                    entity_id=audit_response.entity_id
                )
                return audit_response
            else:
                self.logger.log(
                    "AuditService",
                    "error",
                    "Failed to create audit log"
                )
                return None
        except Exception as e:
            self.logger.log(
                "AuditService",
                "critical",
                f"Exception during audit log creation: {e}"
            )
            return None

    async def get_audit_log_by_id(self, tx: Prisma, log_id: UUID) -> Optional[AuditLogResponseSchema]:
        """
        Retrieves an audit log by its unique identifier.

        Args:
            tx (Prisma): The Prisma transaction object.
            log_id (UUID): The UUID of the audit log to retrieve.

        Returns:
            Optional[AuditLogResponseSchema]: The audit log data if found, None otherwise.
        """
        try:
            audit_log = await tx.auditlog.find_unique(where={"log_id": str(log_id)})

            if audit_log:
                audit_response = AuditLogResponseSchema(**audit_log.dict())
                self.logger.log(
                    "AuditService",
                    "info",
                    "Audit log retrieved successfully",
                    log_id=audit_response.log_id,
                    user_id=audit_response.user_id,
                    action_type=audit_response.action_type,
                    entity_type=audit_response.entity_type,
                    entity_id=audit_response.entity_id
                )
                return audit_response
            else:
                self.logger.log(
                    "AuditService",
                    "warning",
                    "Audit log not found",
                    log_id=log_id
                )
                return None
        except Exception as e:
            self.logger.log(
                "AuditService",
                "critical",
                f"Exception during audit log retrieval: {e}"
            )
            return None

    async def list_audit_logs(self, tx: Prisma, filters: Optional[Dict[str, Any]] = None) -> Optional[List[AuditLogResponseSchema]]:
        """
        Retrieves a list of audit logs with optional filtering.

        Args:
            tx (Prisma): The Prisma transaction object.
            filters (Optional[Dict[str, Any]]): Key-value pairs to filter the audit logs.

        Returns:
            Optional[List[AuditLogResponseSchema]]: A list of audit logs if successful, None otherwise.
        """
        try:
            where_clause = filters or {}
            audit_logs = await tx.auditlog.find_many(where=where_clause)

            if audit_logs:
                audit_responses = [AuditLogResponseSchema(**audit.dict()) for audit in audit_logs]
                self.logger.log(
                    "AuditService",
                    "info",
                    f"{len(audit_responses)} audit logs retrieved successfully",
                    filters=filters
                )
                return audit_responses
            else:
                self.logger.log(
                    "AuditService",
                    "warning",
                    "No audit logs found",
                    filters=filters
                )
                return []
        except Exception as e:
            self.logger.log(
                "AuditService",
                "critical",
                f"Exception during listing audit logs: {e}"
            )
            return None

    async def delete_audit_log(self, tx: Prisma, log_id: UUID) -> bool:
        """
        Deletes an audit log from the database.

        Args:
            tx (Prisma): The Prisma transaction object.
            log_id (UUID): The UUID of the audit log to delete.

        Returns:
            bool: True if deletion was successful, False otherwise.
        """
        try:
            deleted_log = await tx.auditlog.delete(where={"log_id": str(log_id)})

            if deleted_log:
                self.logger.log(
                    "AuditService",
                    "info",
                    "Audit log deleted successfully",
                    log_id=log_id
                )
                return True
            else:
                self.logger.log(
                    "AuditService",
                    "warning",
                    "Audit log not found or already deleted",
                    log_id=log_id
                )
                return False
        except Exception as e:
            self.logger.log(
                "AuditService",
                "critical",
                f"Exception during audit log deletion: {e}"
            )
            return False