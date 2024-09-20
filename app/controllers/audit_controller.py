# app/controllers/audit_controller.py

"""
Audit Controller Module

This module defines the AuditController class responsible for managing audit log-related operations.
It handles both basic CRUD operations for audit logs and any complex workflows that may involve
additional business logic or multiple services.

Responsibilities:
- Coordinating between AuditService to perform audit log-related operations.
- Managing transactions to ensure data consistency across multiple service operations.
- Handling higher-level business logic specific to audit logs.

Design Philosophy:
- Maintain high cohesion by focusing solely on audit log-related orchestration.
- Promote loose coupling by interacting with services through well-defined interfaces.
- Ensure robustness through comprehensive error handling and logging.

Usage Example:
    from app.controllers import AuditController

    audit_controller = AuditController()
    new_audit_log = audit_controller.create_audit_log(audit_data)
"""
from typing import List, Optional, Dict, Any
from uuid import UUID
from app.services import (
    AuditService
)
from app.schemas import (
    AuditLogCreateSchema,
    AuditLogUpdateSchema,
    AuditLogResponseSchema
)
from app.logger import ConstellationLogger

class AuditController:
    """
    AuditController manages all audit log-related operations, coordinating with AuditService
    to perform CRUD operations and handle complex business logic.
    """

    def __init__(self):
        """
        Initializes the AuditController with an instance of AuditService,
        along with the ConstellationLogger for logging purposes.
        """
        self.audit_service = AuditService()
        self.logger = ConstellationLogger()

    # -------------------
    # Basic Audit Log Operations
    # -------------------

    def create_audit_log(self, audit_data: AuditLogCreateSchema) -> Optional[AuditLogResponseSchema]:
        """
        Creates a new audit log entry.

        Args:
            audit_data (AuditLogCreateSchema): The data required to create a new audit log.

        Returns:
            Optional[AuditLogResponseSchema]: The created audit log data if successful, None otherwise.
        """
        try:
            audit_log = self.audit_service.create_audit_log(audit_data)
            if audit_log:
                self.logger.log(
                    "AuditController",
                    "info",
                    "Audit log created successfully.",
                    log_id=audit_log.log_id
                )
            return audit_log
        except Exception as e:
            self.logger.log(
                "AuditController",
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
            audit_log = self.audit_service.get_audit_log_by_id(log_id)
            if audit_log:
                self.logger.log(
                    "AuditController",
                    "info",
                    "Audit log retrieved successfully.",
                    log_id=audit_log.log_id
                )
            return audit_log
        except Exception as e:
            self.logger.log(
                "AuditController",
                "critical",
                f"Exception during audit log retrieval: {e}"
            )
            return None

    def update_audit_log(self, log_id: UUID, update_data: AuditLogUpdateSchema) -> Optional[AuditLogResponseSchema]:
        """
        Updates an existing audit log's information.

        Args:
            log_id (UUID): The UUID of the audit log to update.
            update_data (AuditLogUpdateSchema): The data to update for the audit log.

        Returns:
            Optional[AuditLogResponseSchema]: The updated audit log data if successful, None otherwise.
        """
        try:
            audit_log = self.audit_service.update_audit_log(log_id, update_data)
            if audit_log:
                self.logger.log(
                    "AuditController",
                    "info",
                    "Audit log updated successfully.",
                    log_id=audit_log.log_id
                )
            return audit_log
        except Exception as e:
            self.logger.log(
                "AuditController",
                "critical",
                f"Exception during audit log update: {e}"
            )
            return None

    def delete_audit_log(self, log_id: UUID) -> bool:
        """
        Deletes an audit log.

        Args:
            log_id (UUID): The UUID of the audit log to delete.

        Returns:
            bool: True if deletion was successful, False otherwise.
        """
        try:
            success = self.audit_service.delete_audit_log(log_id)
            if success:
                self.logger.log(
                    "AuditController",
                    "info",
                    "Audit log deleted successfully.",
                    log_id=log_id
                )
            return success
        except Exception as e:
            self.logger.log(
                "AuditController",
                "critical",
                f"Exception during audit log deletion: {e}"
            )
            return False

    def list_audit_logs(self, filters: Optional[Dict[str, Any]] = None) -> Optional[List[AuditLogResponseSchema]]:
        """
        Lists audit logs with optional filtering.

        Args:
            filters (Optional[Dict[str, Any]]): Key-value pairs to filter the audit logs.

        Returns:
            Optional[List[AuditLogResponseSchema]]: A list of audit logs if successful, None otherwise.
        """
        try:
            audit_logs = self.audit_service.list_audit_logs(filters)
            if audit_logs is not None:
                self.logger.log(
                    "AuditController",
                    "info",
                    f"{len(audit_logs)} audit logs retrieved successfully.",
                    filters=filters
                )
            return audit_logs
        except Exception as e:
            self.logger.log(
                "AuditController",
                "critical",
                f"Exception during listing audit logs: {e}"
            )
            return None
