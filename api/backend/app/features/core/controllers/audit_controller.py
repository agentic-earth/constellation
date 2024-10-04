# app/services/audit_service.py

"""
Audit Controller Module

This module encapsulates all audit-related operations, including logging actions performed on blocks and taxonomy.
It ensures that all critical operations are captured in `audit_logs` for traceability and compliance.

Design Philosophy:
- Maintain independence from other services to uphold clear separation of concerns.
- Utilize Supabase's REST API for standard CRUD operations for performance and reliability.
- Handle complex audit logging within Python.
- Ensure flexibility to adapt to auditing requirements with minimal modifications.
"""

import traceback
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime

from backend.app.logger import ConstellationLogger
from backend.app.database import get_supabase_client
from backend.app.schemas import AuditLogResponseSchema, AuditLogUpdateSchema
from backend.app.utils.serialization_utils import serialize_dict
from backend.app.features.core.services.audit_service import AuditService


class AuditController:
    """
    AuditController handles all audit-related operations, including creating audit logs for various actions.
    """

    def __init__(self):
        """
        Initializes the AuditController with the Supabase client and logger.
        """
        self.client = get_supabase_client()
        self.logger = ConstellationLogger()
        self.audit_service = AuditService()

    def create_audit_log(self, audit_data: Dict[str, Any]) -> bool:
        """
        Creates an audit log entry in the `audit_logs` table.

        Args:
            audit_data (Dict[str, Any]): Dictionary containing audit details.

        Returns:
            bool: True if audit log creation was successful, False otherwise.
        """
        try:
            # Ensure mandatory fields are present
            required_fields = {"action_type", "entity_type", "entity_id", "details"}
            if not required_fields.issubset(audit_data.keys()):
                self.logger.log(
                    "AuditController",
                    "error",
                    "Missing required fields in audit_data.",
                    extra={"audit_data": audit_data},
                )
                return False

            # Generate UUID for the audit log
            audit_log_id = uuid4()
            audit_data["log_id"] = str(audit_log_id)

            # Add timestamp
            audit_data["timestamp"] = datetime.utcnow().isoformat()

            # Serialize the data
            serialized_data = serialize_dict(audit_data)

            # Insert the audit log into the database
            response = self.client.table("audit_logs").insert(serialized_data).execute()

            if response.error:
                self.logger.log(
                    "AuditController",
                    "error",
                    "Failed to create audit log.",
                    extra={"error": response.error.message, "audit_data": audit_data},
                )
                return False

            self.logger.log(
                "AuditController",
                "info",
                "Audit log created successfully.",
                extra={
                    "log_id": str(audit_log_id),
                    "entity_id": audit_data["entity_id"],
                    "action_type": audit_data["action_type"],
                },
            )
            return True

        except Exception as e:
            self.logger.log(
                "AuditController",
                "critical",
                f"Exception during audit log creation: {str(e)}",
                extra={"traceback": traceback.format_exc(), "audit_data": audit_data},
            )
            return False

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
                    log_id=audit_log.log_id,
                )
            return audit_log
        except Exception as e:
            self.logger.log(
                "AuditController",
                "critical",
                f"Exception during audit log retrieval: {e}",
            )
            return None

    def update_audit_log(
        self, log_id: UUID, update_data: AuditLogUpdateSchema
    ) -> Optional[AuditLogResponseSchema]:
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
                    log_id=audit_log.log_id,
                )
            return audit_log
        except Exception as e:
            self.logger.log(
                "AuditController", "critical", f"Exception during audit log update: {e}"
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
                    log_id=log_id,
                )
            return success
        except Exception as e:
            self.logger.log(
                "AuditController",
                "critical",
                f"Exception during audit log deletion: {e}",
            )
            return False

    def list_audit_logs(
        self, filters: Optional[Dict[str, Any]] = None
    ) -> Optional[List[AuditLogResponseSchema]]:
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
                    filters=filters,
                )
            return audit_logs
        except Exception as e:
            self.logger.log(
                "AuditController",
                "critical",
                f"Exception during listing audit logs: {e}",
            )
            return None
