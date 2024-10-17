# dependencies.py

from typing import Generator
from fastapi import Depends
from prisma import Prisma
from backend.app.database import prisma_client
from backend.app.features.core.controllers.block_controller import BlockController

def get_prisma() -> Prisma:
    return prisma_client


def get_block_controller(prisma: Prisma = Depends(get_prisma)) -> BlockController:
    return BlockController(prisma)