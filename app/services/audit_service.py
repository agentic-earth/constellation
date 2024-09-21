# app/services/audit_service.py

"""
Audit Service Module

This module encapsulates all audit log-related business logic and interactions with the Supabase backend.
It provides functions to create, retrieve, list, and delete audit logs, ensuring that all operations are
logged appropriately using the Constellation Logger.

Design Philosophy:
- Utilize Supabase's REST API for standard CRUD operations for performance and reliability.
- Use Python only for advanced logic that cannot be handled directly by Supabase.
- Ensure flexibility to adapt to schema changes with minimal modifications.
"""

from typing import Optional, List, Dict, Any
from uuid import UUID
from app.models import AuditLog
from app.schemas import AuditLogCreateSchema, AuditLogResponseSchema
from app.logger import ConstellationLogger
from app.database import get_supabase_client
from app.schemas import AuditLogResponseSchema
from datetime import datetime


class AuditService:
    """
    AuditService class encapsulates all audit log-related operations.
    """

    def __init__(self):
        """
        Initializes the AuditService with the Supabase client and logger.
        """
        self.client = get_supabase_client()
        self.logger = ConstellationLogger()

    def create_audit_log(self, audit_data: AuditLogCreateSchema) -> Optional[AuditLogResponseSchema]:
        """
        Creates a new audit log entry in the Supabase database.

        Args:
            audit_data (AuditLogCreateSchema): The data required to create a new audit log.

        Returns:
            Optional[AuditLogResponseSchema]: The created audit log data if successful, None otherwise.
        """
        try:
            # Convert Pydantic schema to dictionary
            data = audit_data.dict()
            response = self.client.table("audit_logs").insert(data).execute()

            if response.status_code in [200, 201] and response.data:
                created_audit = AuditLogResponseSchema(**response.data[0])
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
                    "Failed to create audit log",
                    status_code=response.status_code,
                    error=response.error
                )
                return None
        except Exception as e:
            self.logger.log(
                "AuditService",
                "critical",
                f"Exception during audit log creation: {e}"
            )
            return None

    def get_audit_log_by_id(self, log_id: UUID) -> Optional[AuditLogResponseSchema]:
        """
        Retrieves an audit log by its unique identifier.

        Args:
            log_id (UUID): The UUID of the audit log to retrieve.

        Returns:
            Optional[AuditLogResponseSchema]: The audit log data if found, None otherwise.
        """
        try:
            response = self.client.table("audit_logs").select("*").eq("log_id", str(log_id)).single().execute()

            if response.status_code == 200 and response.data:
                audit_log = AuditLogResponseSchema(**response.data)
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
                    log_id=log_id,
                    status_code=response.status_code
                )
                return None
        except Exception as e:
            self.logger.log(
                "AuditService",
                "critical",
                f"Exception during audit log retrieval: {e}"
            )
            return None

    def list_audit_logs(self, filters: Optional[Dict[str, Any]] = None) -> Optional[List[AuditLogResponseSchema]]:
        """
        Retrieves a list of audit logs with optional filtering.

        Args:
            filters (Optional[Dict[str, Any]]): Key-value pairs to filter the audit logs.

        Returns:
            Optional[List[AuditLogResponseSchema]]: A list of audit logs if successful, None otherwise.
        """
        try:
            query = self.client.table("audit_logs").select("*")
            if filters:
                for key, value in filters.items():
                    query = query.eq(key, value)
            response = query.execute()

            if response.status_code == 200 and response.data:
                audit_logs = [AuditLogResponseSchema(**audit) for audit in response.data]
                self.logger.log(
                    "AuditService",
                    "info",
                    f"{len(audit_logs)} audit logs retrieved successfully",
                    filters=filters
                )
                return audit_logs
            else:
                self.logger.log(
                    "AuditService",
                    "warning",
                    "No audit logs found",
                    filters=filters,
                    status_code=response.status_code
                )
                return []
        except Exception as e:
            self.logger.log(
                "AuditService",
                "critical",
                f"Exception during listing audit logs: {e}"
            )
            return None

    def delete_audit_log(self, log_id: UUID) -> bool:
        """
        Deletes an audit log from the Supabase database.

        Args:
            log_id (UUID): The UUID of the audit log to delete.

        Returns:
            bool: True if deletion was successful, False otherwise.
        """
        try:
            response = self.client.table("audit_logs").delete().eq("log_id", str(log_id)).execute()

            if response.status_code == 200 and response.count > 0:
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
                    log_id=log_id,
                    status_code=response.status_code
                )
                return False
        except Exception as e:
            self.logger.log(
                "AuditService",
                "critical",
                f"Exception during audit log deletion: {e}"
            )
            return False
