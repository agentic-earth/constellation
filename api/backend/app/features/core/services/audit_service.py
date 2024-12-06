"""
Audit Service Module

This module implements the Audit Service using a Repository pattern with Prisma ORM.

Design Pattern:
- Repository Pattern: The AuditService class acts as a repository, encapsulating the data access logic.
- Dependency Injection: The Prisma client is injected as an argument into each method.

Key Design Decisions:
1. Pass Prisma Client: Each method receives the Prisma client as an argument, promoting better testability and decoupling.
2. Use Timezone-Aware Datetimes: Replaced `utcnow` with `datetime.now(timezone.utc)` to handle timezone-aware objects.
3. Enum Handling: Utilizes Python Enums to mirror Prisma enums for `action_type` and `entity_type`.
4. Main Function for Testing: Added a main function to demonstrate and test the AuditService functionalities.
"""

import asyncio
import traceback
import json
from typing import Optional, List, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime, timezone
from prisma import Prisma
from prisma.enums import (
    ActionTypeEnum as PrismaActionTypeEnum,
    AuditEntityTypeEnum as PrismaAuditEntityTypeEnum,
)
from prisma.models import AuditLog as PrismaAuditLog
from prisma.errors import UniqueViolationError, PrismaError

from backend.app.logger import ConstellationLogger


class AuditService:
    def __init__(self):
        self.logger = ConstellationLogger()

    async def create_audit_log(
        self, tx: Prisma, audit_data: Dict[str, Any]
    ) -> Optional[PrismaAuditLog]:
        """
        Create a new audit log entry.

        Args:
            tx (Prisma): The Prisma client instance.
            audit_data (Dict[str, Any]): Dictionary containing audit log data.
                Expected keys:
                    - 'user_id': UUID (string)
                    - 'action_type': ActionTypeEnum
                    - 'entity_type': AuditEntityTypeEnum
                    - 'entity_id': UUID (string)
                    - 'details': Dict[str, Any] (optional)

        Returns:
            Optional[PrismaAuditLog]: The created audit log entry if successful, None otherwise.
        """
        try:
            # Validate required fields
            required_fields = {"user_id", "action_type", "entity_type", "entity_id"}
            for field in required_fields:
                if field not in audit_data:
                    self.logger.log(
                        "AuditService",
                        "error",
                        "Missing required field in audit_data.",
                        extra={"audit_data": audit_data},
                    )
                    return None

            # Ensure enums are valid
            if audit_data["action_type"] not in PrismaActionTypeEnum.__members__:
                self.logger.log(
                    "AuditService",
                    "error",
                    f"Invalid action_type: {audit_data['action_type']}",
                )
                return None

            if audit_data["entity_type"] not in PrismaAuditEntityTypeEnum.__members__:
                self.logger.log(
                    "AuditService",
                    "error",
                    f"Invalid entity_type: {audit_data['entity_type']}",
                )
                return None

            # Validate and sanitize 'details' field
            details = audit_data.get("details")
            if details is not None and not isinstance(details, dict):
                self.logger.log(
                    "AuditService",
                    "error",
                    "`details` must be a dictionary representing JSON data.",
                    extra={"details": details},
                )
                return None

            # Prepare data for creation
            create_data = {
                "log_id": str(uuid4()),
                "user_id": str(audit_data["user_id"]),
                "action_type": str(PrismaActionTypeEnum[audit_data["action_type"]]),
                "entity_type": str(PrismaAuditEntityTypeEnum[audit_data["entity_type"]]),
                "entity_id": str(audit_data["entity_id"]),
                "timestamp": datetime.now(timezone.utc),
                "details": json.dumps(details),  # Ensure this is a dict
            }

            self.logger.log(
                "AuditService",
                "info",
                "Audit log data is valid.",
                extra={"audit_create_data": create_data},
            )

            # Create the audit log
            created_log = await tx.auditlog.create(data=create_data)

            self.logger.log(
                "AuditService",
                "info",
                "Audit log created successfully.",
                log_id=created_log.log_id,
                action_type=created_log.action_type,
                entity_type=created_log.entity_type,
                entity_id=created_log.entity_id,
            )
            print(f"Audit log created successfully: {created_log.log_id}")
            return created_log

        except Exception as e:
            self.logger.log(
                "AuditService",
                "error",
                f"Exception during audit log creation: {str(e)}",
                extra={"traceback": traceback.format_exc(), "audit_data": audit_data},
            )
            return None

    async def get_audit_log_by_id(
        self, tx: Prisma, log_id: UUID
    ) -> Optional[PrismaAuditLog]:
        """
        Retrieve an audit log entry by its ID.

        Args:
            tx (Prisma): The Prisma client instance.
            log_id (UUID): The UUID of the audit log to retrieve.

        Returns:
            Optional[PrismaAuditLog]: The audit log data if found, None otherwise.
        """
        try:
            audit_log = await tx.auditlog.find_unique(where={"log_id": str(log_id)})

            if audit_log:
                self.logger.log(
                    "AuditService",
                    "info",
                    "Audit log retrieved successfully.",
                    log_id=audit_log.log_id,
                )
            else:
                self.logger.log(
                    "AuditService",
                    "warning",
                    "Audit log not found.",
                    log_id=str(log_id),
                )

            return audit_log
        except Exception as e:
            self.logger.log(
                "AuditService",
                "error",
                "Failed to retrieve audit log by ID.",
                error=str(e),
            )
            return None

    async def list_audit_logs(
        self,
        tx: Prisma,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[PrismaAuditLog]:
        """
        List audit log entries, optionally filtered.

        Args:
            tx (Prisma): The Prisma client instance.
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
        try:
            prisma_filters = {}

            if filters:
                if "user_id" in filters:
                    prisma_filters["user_id"] = filters["user_id"]
                if "action_type" in filters:
                    if filters["action_type"] not in PrismaActionTypeEnum.__members__:
                        self.logger.log(
                            "AuditService",
                            "error",
                            f"Invalid action_type filter: {filters['action_type']}",
                        )
                        return []
                    prisma_filters["action_type"] = PrismaActionTypeEnum[
                        filters["action_type"]
                    ]
                if "entity_type" in filters:
                    if (
                        filters["entity_type"]
                        not in PrismaAuditEntityTypeEnum.__members__
                    ):
                        self.logger.log(
                            "AuditService",
                            "error",
                            f"Invalid entity_type filter: {filters['entity_type']}",
                        )
                        return []
                    prisma_filters["entity_type"] = PrismaAuditEntityTypeEnum[
                        filters["entity_type"]
                    ]
                if "entity_id" in filters:
                    prisma_filters["entity_id"] = filters["entity_id"]

            audit_logs = await tx.auditlog.find_many(
                where=prisma_filters,
                take=limit,
                skip=offset,
                order={"timestamp": "desc"},
            )

            self.logger.log(
                "AuditService",
                "info",
                f"Retrieved {len(audit_logs)} audit logs.",
                filters=filters,
                limit=limit,
                offset=offset,
            )

            return audit_logs
        except Exception as e:
            self.logger.log(
                "AuditService", "error", "Failed to list audit logs.", error=str(e)
            )
            return []

    async def update_audit_log(
        self, tx: Prisma, log_id: UUID, update_data: Dict[str, Any]
    ) -> Optional[PrismaAuditLog]:
        """
        Update an existing audit log entry.

        Args:
            tx (Prisma): The Prisma client instance.
            log_id (UUID): The UUID of the audit log to update.
            update_data (Dict[str, Any]): Dictionary containing updated audit log data.
                Allowed keys: 'action_type', 'entity_type', 'entity_id', 'details'.

        Returns:
            Optional[PrismaAuditLog]: The updated audit log entry if successful, None otherwise.
        """
        try:
            # Prevent updating the primary key
            if "log_id" in update_data:
                del update_data["log_id"]

            # Validate enums if they are being updated
            if "action_type" in update_data:
                if update_data["action_type"] not in PrismaActionTypeEnum.__members__:
                    self.logger.log(
                        "AuditService",
                        "error",
                        f"Invalid action_type: {update_data['action_type']}",
                    )
                    return None
                update_data["action_type"] = PrismaActionTypeEnum[
                    update_data["action_type"]
                ]

            if "entity_type" in update_data:
                if (
                    update_data["entity_type"]
                    not in PrismaAuditEntityTypeEnum.__members__
                ):
                    self.logger.log(
                        "AuditService",
                        "error",
                        f"Invalid entity_type: {update_data['entity_type']}",
                    )
                    return None
                update_data["entity_type"] = PrismaAuditEntityTypeEnum[
                    update_data["entity_type"]
                ]

            # Validate 'details' field
            if "details" in update_data:
                details = update_data["details"]
                if details is not None and not isinstance(details, dict):
                    self.logger.log(
                        "AuditService",
                        "error",
                        "`details` must be a dictionary representing JSON data.",
                        extra={"details": details},
                    )
                    return None
                update_data["details"] = (
                    details  # Will default to '{}'::jsonb if set to default
                )

            # Update timestamp
            update_data["timestamp"] = datetime.now(timezone.utc)
            update_data["details"] = json.dumps(update_data["details"])
            updated_log = await tx.auditlog.update(
                where={"log_id": str(log_id)}, data=update_data
            )

            self.logger.log(
                "AuditService",
                "info",
                "Audit log updated successfully.",
                log_id=updated_log.log_id,
                updated_fields=list(update_data.keys()),
            )

            return updated_log

        except Exception as e:
            self.logger.log(
                "AuditService", "error", f"Failed to update audit log: {str(e)}"
            )
            return None

    async def delete_audit_log(self, tx: Prisma, log_id: UUID) -> bool:
        """
        Delete an audit log entry.

        Args:
            tx (Prisma): The Prisma client instance.
            log_id (UUID): The UUID of the audit log to delete.

        Returns:
            bool: True if the audit log was successfully deleted, False otherwise.
        """
        try:
            deleted_log = await tx.auditlog.delete(where={"log_id": str(log_id)})

            if deleted_log:
                self.logger.log(
                    "AuditService",
                    "info",
                    "Audit log deleted successfully.",
                    log_id=str(log_id),
                )
                return True
            else:
                self.logger.log(
                    "AuditService",
                    "warning",
                    "Audit log not found for deletion.",
                    log_id=str(log_id),
                )
                return False
        except Exception as e:
            self.logger.log(
                "AuditService", "error", f"Failed to delete audit log: {str(e)}"
            )
            return False

    async def main(self):
        """
        Comprehensive main function to test AuditService functionalities.
        Demonstrates creating audit logs, retrieving logs, updating logs, and deleting logs.
        """
        try:
            # Initialize Prisma client
            prisma = Prisma()
            await prisma.connect()
            print("Connected to the database.")

            # Initialize AuditService
            audit_service = AuditService()

            # Step 1: Create a new audit log
            print("\nCreating a new audit log...")
            new_log_data = {
                "user_id": str(uuid4()),  # Random UUID since no Profile relation
                "action_type": "CREATE",
                "entity_type": "block",
                "entity_id": str(uuid4()),
                "details": {
                    "message": "Created a new block with ID xyz"
                },  # Ensure this is a dict
            }
            created_log = await audit_service.create_audit_log(prisma, new_log_data)
            if created_log:
                print(
                    f"Created AuditLog: {created_log.log_id} - Action: {created_log.action_type}"
                )
            else:
                print("Failed to create AuditLog.")

            # Step 2: Retrieve the audit log by ID
            if created_log:
                print(f"\nRetrieving AuditLog with ID: {created_log.log_id}")
                retrieved_log = await audit_service.get_audit_log_by_id(
                    prisma, UUID(created_log.log_id)
                )
                if retrieved_log:
                    print(
                        f"Retrieved AuditLog: {retrieved_log.log_id} - Action: {retrieved_log.action_type} - Details: {retrieved_log.details}"
                    )
                else:
                    print("Failed to retrieve AuditLog.")
            else:
                print("Skipping retrieval since AuditLog creation failed.")

            # Step 3: List all audit logs
            print("\nListing all audit logs...")
            audit_logs = await audit_service.list_audit_logs(prisma)
            print(f"Total AuditLogs: {len(audit_logs)}")
            for log in audit_logs:
                print(
                    f"- Log ID: {log.log_id}, Action: {log.action_type}, Entity: {log.entity_type}, Details: {log.details}"
                )

            # Step 4: Update the audit log's details
            if created_log:
                print(f"\nUpdating AuditLog with ID: {created_log.log_id}")
                update_data = {
                    "details": {
                        "message": "Updated audit log details."
                    },  # Ensure this is a dict
                    "action_type": "UPDATE",
                }
                updated_log = await audit_service.update_audit_log(
                    prisma, UUID(created_log.log_id), update_data
                )
                if updated_log:
                    print(
                        f"Updated AuditLog: {updated_log.log_id} - Action: {updated_log.action_type} - Details: {updated_log.details}"
                    )
                else:
                    print("Failed to update AuditLog.")
            else:
                print("Skipping update since AuditLog creation failed.")

            # Step 5: Delete the audit log
            if created_log:
                print(f"\nDeleting AuditLog with ID: {created_log.log_id}")
                deletion_success = await audit_service.delete_audit_log(
                    prisma, UUID(created_log.log_id)
                )
                print(f"AuditLog deleted: {deletion_success}")
            else:
                print("Skipping deletion since AuditLog creation failed.")

            # Step 6: List audit logs after deletion
            print("\nListing audit logs after deletion...")
            audit_logs_after_deletion = await audit_service.list_audit_logs(prisma)
            print(f"Total AuditLogs: {len(audit_logs_after_deletion)}")
            for log in audit_logs_after_deletion:
                print(
                    f"- Log ID: {log.log_id}, Action: {log.action_type}, Entity: {log.entity_type}, Details: {log.details}"
                )

        except Exception as e:
            self.logger.log(
                "AuditService", "error", "An error occurred in main.", error=str(e)
            )
            print(f"An error occurred: {e}")
        finally:
            print("\nDisconnecting from the database...")
            await prisma.disconnect()
            print("Database disconnected.")


# -------------------
# Testing Utility
# -------------------


async def run_audit_service_tests():
    """
    Function to run AuditService tests.
    """
    audit_service = AuditService()
    await audit_service.main()


if __name__ == "__main__":
    asyncio.run(run_audit_service_tests())
