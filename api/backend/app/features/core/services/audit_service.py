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
from uuid import UUID, uuid4
from datetime import datetime

from prisma import Prisma
from backend.app.schemas import AuditLogCreateSchema, AuditLogResponseSchema

class AuditService:
    """
    AuditService encapsulates all audit log-related operations, including creating and retrieving audit logs.
    It interacts directly with the Prisma client to manage audit log data.
    """

    def __init__(self, prisma: Prisma):
        self.prisma = prisma

    async def create_audit_log(self, audit_data: AuditLogCreateSchema) -> Optional[AuditLogResponseSchema]:
        audit_log = await self.prisma.audit_logs.create(
            data={
                "log_id": uuid4(),
                "user_id": str(audit_data.user_id),
                "action_type": audit_data.action_type.value,
                "entity_type": audit_data.entity_type.value,
                "entity_id": str(audit_data.entity_id),
                "details": audit_data.details,
                "timestamp": datetime.utcnow(),
            }
        )
        return AuditLogResponseSchema(**audit_log.__dict__)

    async def get_audit_log_by_id(self, log_id: UUID) -> Optional[AuditLogResponseSchema]:
        audit_log = await self.prisma.audit_logs.find_unique(where={"log_id": str(log_id)})
        if audit_log:
            return AuditLogResponseSchema(**audit_log.__dict__)
        return None

    async def list_audit_logs(self, filters: Optional[Dict[str, Any]] = None) -> Optional[List[AuditLogResponseSchema]]:
        if filters:
            audit_logs = await self.prisma.audit_logs.find_many(where=filters)
        else:
            audit_logs = await self.prisma.audit_logs.find_many()
        return [AuditLogResponseSchema(**log.__dict__) for log in audit_logs] if audit_logs else []
    
    async def delete_audit_log(self, log_id: UUID) -> bool:
        await self.prisma.audit_logs.delete(where={"log_id": str(log_id)})
        return True