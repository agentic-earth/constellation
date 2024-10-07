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
from uuid import UUID, uuid4
from backend.app.logger import ConstellationLogger
from datetime import datetime
from prisma import Prisma
from prisma.models import audit_logs as PrismaAuditLog


class AuditService:
    """
    AuditService class encapsulates all audit log-related operations.
    """

    def __init__(self):
        """
        Initializes the AuditService with the logger.
        """
        self.logger = ConstellationLogger()

    async def create_audit_log(self, tx: Prisma, audit_data: Dict[str, Any]) -> Optional[PrismaAuditLog]:
        """
        Creates a new audit log entry in the database.
        """
        try:
            create_data = {
                "log_id": audit_data.get("log_id", str(uuid4())),
                "user_id": audit_data["user_id"],
                "action_type": audit_data["action_type"],
                "entity_type": audit_data["entity_type"],
                "entity_id": audit_data["entity_id"],
                "timestamp": audit_data.get("timestamp", datetime.utcnow()),
                "details": audit_data.get("details")
            }
            created_audit = await tx.audit_logs.create(data=create_data)

            if created_audit:
                self.logger.log(
                    "AuditService",
                    "info",
                    "Audit log created successfully",
                    log_id=created_audit.log_id,
                    user_id=created_audit.user_id,
                    action_type=created_audit.action_type,
                    entity_type=created_audit.entity_type,
                    entity_id=created_audit.entity_id
                )
                return created_audit
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

    async def get_audit_log_by_id(self, tx: Prisma, log_id: UUID) -> Optional[PrismaAuditLog]:
        """
        Retrieves an audit log by its unique identifier.
        """
        try:
            audit_log = await tx.auditlog.find_unique(where={"log_id": str(log_id)})

            if audit_log:
                self.logger.log(
                    "AuditService",
                    "info",
                    "Audit log retrieved successfully",
                    log_id=audit_log.log_id,
                    user_id=audit_log.user_id,
                    action_type=audit_log.action_type,
                    entity_type=audit_log.entity_type,
                    entity_id=audit_log.entity_id
                )
                return audit_log
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

    async def update_audit_log(self, tx: Prisma, log_id: UUID, update_data: Dict[str, Any]) -> Optional[PrismaAuditLog]:
        """
        Updates an existing audit log entry.
        """
        try:
            new_update_data = {
                "user_id": update_data.get("updated_by"),
                "action_type": audit_data.get("action_type"),
                "timestamp": update_data.get("updated_at", datetime.utcnow()),
                "details": audit_data.get("details")
            }
            updated_audit = await tx.auditlog.update(
                where={"log_id": str(log_id)},
                data=new_update_data
            )

            if updated_audit:
                self.logger.log(
                    "AuditService",
                    "info",
                    "Audit log updated successfully",
                    log_id=updated_audit.log_id
                )
                return updated_audit
            else:
                self.logger.log(
                    "AuditService",
                    "warning",
                    "Audit log not found or update failed",
                    log_id=log_id
                )
                return None
        except Exception as e:
            self.logger.log(
                "AuditService",
                "critical",
                f"Exception during audit log update: {e}"
            )
            return None

    async def list_audit_logs(self, tx: Prisma, filters: Optional[Dict[str, Any]] = None) -> List[PrismaAuditLog]:
        """
        Retrieves a list of audit logs with optional filtering.
        """
        try:
            audit_logs = await tx.auditlog.find_many(where=filters or {})
            self.logger.log(
                "AuditService",
                "info",
                f"{len(audit_logs)} audit logs retrieved successfully",
                filters=filters
            )
            return audit_logs
        except Exception as e:
            self.logger.log(
                "AuditService",
                "critical",
                f"Exception during listing audit logs: {e}"
            )
            return []

    async def delete_audit_log(self, tx: Prisma, log_id: UUID) -> bool:
        """
        Deletes an audit log from the database.
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