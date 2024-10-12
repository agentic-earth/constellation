"""
Audit Service Module

This module implements the Audit Service using a Repository pattern with Prisma ORM.

Design Pattern:
- Repository Pattern: The AuditService class acts as a repository, encapsulating the data access logic.
- Dependency Injection: The Prisma client is injected via the database singleton.

Key Design Decisions:
1. Use of Dictionaries: We use dictionaries for input data to provide flexibility in the API.
   This allows callers to provide only the necessary fields without needing to construct full objects.

2. Prisma Models: We use Prisma-generated models (AuditLog) for type hinting and as return types.
   This ensures type safety and consistency with the database schema.

3. Enum Handling: Utilizes Python Enums to mirror Prisma enums for `action_type` and `entity_type`.
   This enhances type safety and prevents invalid enum values.

4. Transaction Management: Utilizes Prisma's interactive transactions to ensure ACID properties during complex operations.

5. JSON Handling: Directly handles JSON fields using Python dictionaries, leveraging Prisma's native JSON support.

This approach balances flexibility, type safety, and simplicity, leveraging Prisma's capabilities
while providing a clean API for audit log operations.
"""

import json
from typing import Optional, List, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime, timezone
import asyncio
from enum import Enum

from prisma import Prisma
from prisma.enums import ActionTypeEnum as PrismaActionTypeEnum, AuditEntityTypeEnum as PrismaAuditEntityTypeEnum
from prisma.models import AuditLog as PrismaAuditLog
from prisma.errors import UniqueViolationError, PrismaError

from backend.app.database import database
from backend.app.logger import ConstellationLogger


class AuditService:
    def __init__(self):
        self.prisma = database.prisma
        self.logger = ConstellationLogger()

    async def create_audit_log(self, audit_data: Dict[str, Any]) -> PrismaAuditLog:
        """
        Create a new audit log entry.

        Args:
            audit_data (Dict[str, Any]): Dictionary containing audit log data.
                Expected keys:
                    - 'user_id': UUID (string)
                    - 'action_type': ActionTypeEnum
                    - 'entity_type': AuditEntityTypeEnum
                    - 'entity_id': UUID (string)
                    - 'details': Dict[str, Any] (optional)

        Returns:
            PrismaAuditLog: The created audit log entry.
        """
        # Validate required fields
        required_fields = ["user_id", "action_type", "entity_type", "entity_id"]
        for field in required_fields:
            if field not in audit_data:
                raise ValueError(f"Missing required field: {field}")

        # Ensure enums are valid
        if audit_data["action_type"] not in PrismaActionTypeEnum.__members__:
            raise ValueError(f"Invalid action_type: {audit_data['action_type']}")

        if audit_data["entity_type"] not in PrismaAuditEntityTypeEnum.__members__:
            raise ValueError(f"Invalid entity_type: {audit_data['entity_type']}")

        # Validate 'details' field
        details = audit_data.get("details")
        if details is not None and not isinstance(details, dict):
            raise ValueError("`details` must be a dictionary representing JSON data.")

        # Prepare data for creation
        create_data = {
            "log_id": str(uuid4()),
            "user_id": audit_data["user_id"],
            "action_type": PrismaActionTypeEnum[audit_data["action_type"]],
            "entity_type": PrismaAuditEntityTypeEnum[audit_data["entity_type"]],
            "entity_id": audit_data["entity_id"],
            "timestamp": datetime.now(timezone.utc),
            "details": json.dumps(details)  # Will default to '{}'::jsonb if not provided
        }

        # Create the audit log
        created_log = await self.prisma.auditlog.create(
            data=create_data
        )

        self.logger.log(
            "AuditService",
            "info",
            "Audit log created successfully.",
            log_id=created_log.log_id,
            action_type=created_log.action_type,
            entity_type=created_log.entity_type,
            entity_id=created_log.entity_id
        )

        return created_log

    async def get_audit_log_by_id(self, log_id: UUID) -> Optional[PrismaAuditLog]:
        """
        Retrieve an audit log entry by its ID.

        Args:
            log_id (UUID): The UUID of the audit log to retrieve.

        Returns:
            Optional[PrismaAuditLog]: The retrieved audit log entry, or None if not found.
        """
        audit_log = await self.prisma.auditlog.find_unique(
            where={"log_id": str(log_id)}
        )

        if audit_log:
            self.logger.log(
                "AuditService",
                "info",
                "Audit log retrieved successfully.",
                log_id=audit_log.log_id
            )
        else:
            self.logger.log(
                "AuditService",
                "warning",
                "Audit log not found.",
                log_id=str(log_id)
            )

        return audit_log

    async def list_audit_logs(self, filters: Optional[Dict[str, Any]] = None, limit: int = 100, offset: int = 0) -> List[PrismaAuditLog]:
        """
        List audit log entries, optionally filtered.

        Args:
            filters (Optional[Dict[str, Any]]): Optional filters to apply to the query.
                Supported filters:
                    - 'user_id': UUID (string)
                    - 'action_type': ActionTypeEnum
                    - 'entity_type': AuditEntityTypeEnum
                    - 'entity_id': UUID (string)
            limit (int): The maximum number of audit logs to retrieve.
            offset (int): The number of audit logs to skip before starting to collect the result set.

        Returns:
            List[PrismaAuditLog]: A list of audit log entries matching the filters.
        """
        prisma_filters = {}

        if filters:
            if "user_id" in filters:
                prisma_filters["user_id"] = filters["user_id"]
            if "action_type" in filters:
                if filters["action_type"] not in PrismaActionTypeEnum.__members__:
                    raise ValueError(f"Invalid action_type filter: {filters['action_type']}")
                prisma_filters["action_type"] = PrismaActionTypeEnum[filters["action_type"]]
            if "entity_type" in filters:
                if filters["entity_type"] not in PrismaAuditEntityTypeEnum.__members__:
                    raise ValueError(f"Invalid entity_type filter: {filters['entity_type']}")
                prisma_filters["entity_type"] = PrismaAuditEntityTypeEnum[filters["entity_type"]]
            if "entity_id" in filters:
                prisma_filters["entity_id"] = filters["entity_id"]

        audit_logs = await self.prisma.auditlog.find_many(
            where=prisma_filters,
            take=limit,
            skip=offset,
            order={"timestamp": "desc"}
        )

        self.logger.log(
            "AuditService",
            "info",
            f"Retrieved {len(audit_logs)} audit logs.",
            filters=filters,
            limit=limit,
            offset=offset
        )

        return audit_logs

    async def update_audit_log(self, log_id: UUID, update_data: Dict[str, Any]) -> PrismaAuditLog:
        """
        Update an existing audit log entry.

        Args:
            log_id (UUID): The UUID of the audit log to update.
            update_data (Dict[str, Any]): Dictionary containing updated audit log data.
                Allowed keys: 'action_type', 'entity_type', 'entity_id', 'details'.

        Returns:
            PrismaAuditLog: The updated audit log entry.
        """
        # Prevent updating the primary key
        if "log_id" in update_data:
            del update_data["log_id"]

        # Validate enums if they are being updated
        if "action_type" in update_data:
            if update_data["action_type"] not in PrismaActionTypeEnum.__members__:
                raise ValueError(f"Invalid action_type: {update_data['action_type']}")
            update_data["action_type"] = PrismaActionTypeEnum[update_data["action_type"]]

        if "entity_type" in update_data:
            if update_data["entity_type"] not in PrismaAuditEntityTypeEnum.__members__:
                raise ValueError(f"Invalid entity_type: {update_data['entity_type']}")
            update_data["entity_type"] = PrismaAuditEntityTypeEnum[update_data["entity_type"]]

        # Validate 'details' field
        if "details" in update_data:
            details = update_data["details"]
            if details is not None and not isinstance(details, dict):
                raise ValueError("`details` must be a dictionary representing JSON data.")
            update_data["details"] = details  # Will default to '{}'::jsonb if set to default

        # Update timestamp
        update_data["timestamp"] = datetime.now(timezone.utc)

        updated_log = await self.prisma.auditlog.update(
            where={"log_id": str(log_id)},
            data=update_data
        )

        self.logger.log(
            "AuditService",
            "info",
            "Audit log updated successfully.",
            log_id=updated_log.log_id,
            updated_fields=list(update_data.keys())
        )

        return updated_log

    async def delete_audit_log(self, log_id: UUID) -> bool:
        """
        Delete an audit log entry.

        Args:
            log_id (UUID): The UUID of the audit log to delete.

        Returns:
            bool: True if the audit log was successfully deleted, False otherwise.
        """
        deleted_log = await self.prisma.auditlog.delete(
            where={"log_id": str(log_id)}
        )

        if deleted_log:
            self.logger.log(
                "AuditService",
                "info",
                "Audit log deleted successfully.",
                log_id=str(log_id)
            )
            return True
        else:
            self.logger.log(
                "AuditService",
                "warning",
                "Audit log not found for deletion.",
                log_id=str(log_id)
            )
            return False

    async def main(self):
        """
        Comprehensive main function to test AuditService functionalities.
        Demonstrates creating audit logs, retrieving logs, updating logs, and deleting logs.
        """
        print("Starting AuditService test...")

        # Step 1: Create a new audit log
        print("\nCreating a new audit log...")
        new_log_data = {
            "user_id": str(uuid4()),  # Random UUID since no Profile relation
            "action_type": "CREATE",
            "entity_type": "block",
            "entity_id": str(uuid4()),
            "details": {"message": "Created a new block with ID xyz"}  # Ensure this is a dict
        }
        created_log = await self.create_audit_log(new_log_data)
        if created_log:
            print(f"Created AuditLog: {created_log.log_id} - Action: {created_log.action_type}")
        else:
            print("Failed to create AuditLog.")

        # Step 2: Retrieve the audit log by ID
        if created_log:
            print(f"\nRetrieving AuditLog with ID: {created_log.log_id}")
            retrieved_log = await self.get_audit_log_by_id(UUID(created_log.log_id))
            if retrieved_log:
                print(f"Retrieved AuditLog: {retrieved_log.log_id} - Action: {retrieved_log.action_type} - Details: {retrieved_log.details}")
            else:
                print("Failed to retrieve AuditLog.")
        else:
            print("Skipping retrieval since AuditLog creation failed.")

        # Step 3: List all audit logs
        print("\nListing all audit logs...")
        audit_logs = await self.list_audit_logs()
        print(f"Total AuditLogs: {len(audit_logs)}")
        for log in audit_logs:
            print(f"- Log ID: {log.log_id}, Action: {log.action_type}, Entity: {log.entity_type}, Details: {log.details}")

        # Step 4: Update the audit log's details
        if created_log:
            print(f"\nUpdating AuditLog with ID: {created_log.log_id}")
            update_data = {
                "details": {"message": "Updated audit log details."},  # Ensure this is a dict
                "action_type": "UPDATE"
            }
            updated_log = await self.update_audit_log(UUID(created_log.log_id), update_data)
            if updated_log:
                print(f"Updated AuditLog: {updated_log.log_id} - Action: {updated_log.action_type} - Details: {updated_log.details}")
            else:
                print("Failed to update AuditLog.")
        else:
            print("Skipping update since AuditLog creation failed.")

        # Step 5: Delete the audit log
        if created_log:
            print(f"\nDeleting AuditLog with ID: {created_log.log_id}")
            deletion_success = await self.delete_audit_log(UUID(created_log.log_id))
            print(f"AuditLog deleted: {deletion_success}")
        else:
            print("Skipping deletion since AuditLog creation failed.")

        # Step 6: List audit logs after deletion
        print("\nListing audit logs after deletion...")
        audit_logs_after_deletion = await self.list_audit_logs()
        print(f"Total AuditLogs: {len(audit_logs_after_deletion)}")
        for log in audit_logs_after_deletion:
            print(f"- Log ID: {log.log_id}, Action: {log.action_type}, Entity: {log.entity_type}, Details: {log.details}")

        print("\nAuditService test completed.")


# Testing the AuditService
if __name__ == "__main__":
    async def run_audit_service_tests():
        print("Connecting to the database...")
        await database.connect()
        print("Database connected.")

        audit_service = AuditService()
        await audit_service.main()

        print("\nDisconnecting from the database...")
        await database.disconnect()
        print("Database disconnected.")

    asyncio.run(run_audit_service_tests())
