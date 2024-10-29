from langchain.tools import StructuredTool
from backend.app.features.core.services.block_service import BlockService
from typing import List, Dict, Any

from prisma import Prisma

async def similarity_search(tx: Prisma, vector: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Searches for the most similar paper to the user's query and provides a summary.
    """
    block_service = BlockService()
    vectors = await block_service.search_blocks_by_vector_similarity(tx, vector, top_k)
    return vectors

SimilaritySearchTool = StructuredTool.from_function(
    func=similarity_search,
    name="SimilaritySearchTool",
    description="Searches for the most similar paper to the user's query and provides a summary."
)
