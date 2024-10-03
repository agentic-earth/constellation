"""
Audit Service Module

This module implements the Audit Service using a Repository pattern with Prisma ORM.

Design Pattern:
- Repository Pattern: The AuditService class acts as a repository, encapsulating the data access logic.
- Dependency Injection: The Prisma client is injected via the database singleton.

Key Design Decisions:
1. Use of Dictionaries: We use dictionaries for input data to provide flexibility in the API.
   This allows callers to provide only the necessary fields without needing to construct full objects.

2. Prisma Models: We use Prisma-generated models (PrismaAuditLog) for type hinting and as return types.
   This ensures type safety and consistency with the database schema.

3. No Request/Response Models: We directly use dictionaries for input and Prisma models for output.
   This simplifies the API and reduces redundancy, as Prisma models already provide necessary structure.

4. JSON Handling: We manually convert the 'details' field to and from JSON strings.
   This ensures compatibility with Prisma's JSON field type.

5. Error Handling: Exceptions are allowed to propagate, to be handled by the caller.

This approach balances flexibility, type safety, and simplicity, leveraging Prisma's capabilities
while providing a clean API for audit log operations.
"""

import json
from typing import Optional, List, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime
import asyncio

from prisma.models import audit_logs as PrismaAuditLog
from prisma.enums import action_type_enum, audit_entity_type_enum
from backend.app.database import database

class AuditService:
    def __init__(self):
        self.prisma = database.prisma

    async def create_audit_log(self, audit_data: Dict[str, Any]) -> Optional[PrismaAuditLog]:
        """
        Create a new audit log entry.

        Args:
            audit_data (Dict[str, Any]): Dictionary containing audit log data.

        Returns:
            Optional[PrismaAuditLog]: The created audit log entry, or None if creation failed.
        """
        create_data = {
            "log_id": str(uuid4()),
            "action_type": audit_data["action_type"],
            "entity_type": audit_data["entity_type"],
            "entity_id": audit_data["entity_id"],
            "timestamp": datetime.utcnow(),
            "users": {"connect": {"user_id": audit_data["user_id"]}},
        }

        if "details" in audit_data:
            create_data["details"] = json.dumps(audit_data["details"])

        return await self.prisma.audit_logs.create(data=create_data)

    async def get_audit_log_by_id(self, log_id: UUID) -> Optional[PrismaAuditLog]:
        """
        Retrieve an audit log entry by its ID.

        Args:
            log_id (UUID): The ID of the audit log to retrieve.

        Returns:
            Optional[PrismaAuditLog]: The retrieved audit log entry, or None if not found.
        """
        return await self.prisma.audit_logs.find_unique(where={"log_id": str(log_id)})

    async def list_audit_logs(self, filters: Optional[Dict[str, Any]] = None) -> List[PrismaAuditLog]:
        """
        List audit log entries, optionally filtered.

        Args:
            filters (Optional[Dict[str, Any]]): Optional filters to apply to the query.

        Returns:
            List[PrismaAuditLog]: A list of audit log entries matching the filters.
        """
        return await self.prisma.audit_logs.find_many(where=filters or {})

    async def update_audit_log(self, log_id: UUID, audit_data: Dict[str, Any]) -> Optional[PrismaAuditLog]:
        """
        Update an existing audit log entry.

        Args:
            log_id (UUID): The ID of the audit log to update.
            audit_data (Dict[str, Any]): Dictionary containing updated audit log data.

        Returns:
            Optional[PrismaAuditLog]: The updated audit log entry, or None if update failed.
        """
        update_data = {k: v for k, v in audit_data.items() if k != "user_id"}
        if "details" in update_data:
            update_data["details"] = json.dumps(update_data["details"])
        return await self.prisma.audit_logs.update(
            where={"log_id": str(log_id)},
            data=update_data
        )

    async def delete_audit_log(self, log_id: UUID) -> bool:
        """
        Delete an audit log entry.

        Args:
            log_id (UUID): The ID of the audit log to delete.

        Returns:
            bool: True if the audit log was successfully deleted, False otherwise.
        """
        deleted_log = await self.prisma.audit_logs.delete(where={"log_id": str(log_id)})
        return deleted_log is not None

async def main():
    """
    Main function to demonstrate and test the AuditService functionality.
    """
    print("Starting AuditService test...")

    print("Connecting to the database...")
    await database.connect()
    print("Database connected successfully.")

    audit_service = AuditService()

    # Use this user ID in your tests
    test_user_id = "11111111-1111-1111-1111-111111111111"

    try:
        # Create a new audit log
        print("\nCreating a new audit log...")
        new_log_data = {
            "user_id": test_user_id,  # Use the test user ID here
            "action_type": action_type_enum.CREATE,
            "entity_type": audit_entity_type_enum.block,
            "entity_id": str(uuid4()),
            "details": {"message": "Created a new block"}
        }
        created_log = await audit_service.create_audit_log(new_log_data)
        print(f"Created audit log: {created_log}")

        # ... (rest of the main function remains the same)

    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        print(traceback.format_exc())

    finally:
        print("\nDisconnecting from the database...")
        await database.disconnect()
        print("Database disconnected.")

if __name__ == "__main__":
    asyncio.run(main())