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
from prisma import Prisma
from prisma.client import get_prisma
from fastapi import HTTPException, status
from prisma.models import audit_logs as PrismaAuditLog
import json

class AuditController:
    """
    AuditController handles all audit-related operations, including creating audit logs for various actions.
    """

    def __init__(self, prisma: Prisma):
        """
        Initializes the AuditController with the Prisma client and logger.
        """
        self.prisma = prisma
        self.logger = ConstellationLogger()
        self.audit_service = AuditService()

    async def create_audit_log(self, audit_data: AuditLogCreateSchema) -> Optional[PrismaAuditLog]:
        """
        Creates an audit log entry in the `audit_logs` table.

        Args:
            audit_data (Dict[str, Any]): Dictionary containing audit details.

        Returns:
            Optional[PrismaAuditLog]: The created audit log if successful, None otherwise.
        """
        try:
            async with self.prisma.tx() as tx:
                create_data = { 
                    "user_id": audit_data.user_id,
                    "action_type": audit_data.action_type,
                    "entity_type": audit_data.entity_type,
                    "entity_id": audit_data.entity_id,
                    "details": json.dumps(audit_data.details),
                }

                audit_log = await self.audit_service.create_audit_log(tx, create_data)

                if not audit_log:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Audit log creation failed.",
                    )
                else:
                    self.logger.log(
                        "AuditController",
                        "info",
                        "Audit log created successfully.",
                    )
                return audit_log

        except Exception as e:
            self.logger.log(
                "AuditController",
                "critical",
                f"Exception during audit log creation: {str(e)}",
                extra={"traceback": traceback.format_exc(), "audit_data": audit_data},
            )
            return None

    async def get_audit_log_by_id(self, log_id: UUID) -> Optional[PrismaAuditLog]:
        """
        Retrieves an audit log by its unique identifier.

        Args:
            log_id (UUID): The UUID of the audit log to retrieve.

        Returns:
            Optional[PrismaAuditLog]: The audit log data if found, None otherwise.
        """
        try:
            async with self.prisma.tx() as tx:
                audit_log = await self.audit_service.get_audit_log_by_id(tx, log_id)
                
                if not audit_log:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Audit log not found.",
                    )
                else:
                    self.logger.log(
                        "AuditController",
                        "info",
                        "Audit log retrieved successfully.",
                    )

                return audit_log
            
        except Exception as e:
            self.logger.log(
                "AuditController",
                "critical",
                f"Exception during audit log retrieval: {e}",
            )
            return None

    async def update_audit_log(
        self, log_id: UUID, update_data: AuditLogUpdateSchema
    ) -> Optional[PrismaAuditLog]:
        """
        Updates an existing audit log's information.

        Args:
            log_id (UUID): The UUID of the audit log to update.
            update_data (AuditLogUpdateSchema): The data to update for the audit log.

        Returns:
            Optional[PrismaAuditLog]: The updated audit log data if successful, None otherwise.
        """
        try:
            async with self.prisma.tx() as tx:
                update_audit_data = {
                    "action_type": update_data.action_type,
                    "details": json.dumps(update_data.details),
                }
                updated_audit = await self.audit_service.update_audit_log(tx, log_id, update_audit_data)

                if not updated_audit:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Audit log update failed.",
                    )
                else:
                    self.logger.log(
                        "AuditController",
                        "info",
                        "Audit log updated successfully.",
                    )
                
                return updated_audit
        except Exception as e:
            self.logger.log(
                "AuditController",
                "critical",
                f"Exception during audit log update: {e}",
            )
            return None

    async def delete_audit_log(self, log_id: UUID) -> bool:
        """
        Deletes an audit log.

        Args:
            log_id (UUID): The UUID of the audit log to delete.

        Returns:
            bool: True if deletion was successful, False otherwise.
        """
        try:
            async with self.prisma.tx() as tx:
                success = await self.audit_service.delete_audit_log(tx, log_id)

                if not success:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Audit log deletion failed.",
                    )
                else:
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

    async def list_audit_logs(
        self, filters: Optional[Dict[str, Any]] = None
    ) -> List[PrismaAuditLog]:
        """
        Lists audit logs with optional filtering.

        Args:
            filters (Optional[Dict[str, Any]]): Key-value pairs to filter the audit logs.

        Returns:
            Optional[List[PrismaAuditLog]]: A list of audit logs if successful, None otherwise.
        """
        try:
            async with self.prisma.tx() as tx:
                audit_logs = await self.audit_service.list_audit_logs(tx, filters)

                if not audit_logs:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Audit logs not found.",
                    )
                else:
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
            return []