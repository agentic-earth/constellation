# dependencies.py

from typing import Generator
from backend.app.features.agent.crews.crew_process import CrewProcess
from fastapi import Depends
from prisma import Prisma
from backend.app.database import prisma_client
from backend.app.features.core.controllers.block_controller import BlockController
from backend.app.features.core.controllers.edge_controller import EdgeController
from backend.app.features.core.controllers.pipeline_controller import PipelineController


def get_prisma() -> Prisma:
    return prisma_client


def get_block_controller(prisma: Prisma = Depends(get_prisma)) -> BlockController:
    return BlockController(prisma)


def get_edge_controller(prisma: Prisma = Depends(get_prisma)) -> EdgeController:
    return EdgeController(prisma)


def get_pipeline_controller(prisma: Prisma = Depends(get_prisma)) -> PipelineController:
    return PipelineController(prisma)
