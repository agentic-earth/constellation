# app/services/__init__.py

"""
Services Package

This package contains all service modules responsible for handling business logic and interactions
with the Supabase backend. Each service encapsulates operations for a specific entity, ensuring
modularity and separation of concerns.

Available Services:
- UserService: Manages user-related operations.
- BlockService: Handles operations related to blocks.
- EdgeService: Manages edge-related functionalities.
- AuditService: Handles audit log operations.
- PipelineService: Manages pipeline-related operations.

Usage Example:
    from backend.app.services import UserService, BlockService, EdgeService, AuditService, PipelineService

    user_service = UserService()
    block_service = BlockService()
    # and so on...
"""

from backend.app.features.core.services.user_service import UserService
from backend.app.features.core.services.block_service import BlockService
from backend.app.features.core.services.edge_service import EdgeService
from backend.app.features.core.services.audit_service import AuditService
from backend.app.features.core.services.pipeline_service import PipelineService

__all__ = [
    "UserService",
    "BlockService",
    "EdgeService",
    "AuditService",
    "PipelineService",
]
