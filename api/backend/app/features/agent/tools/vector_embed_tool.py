from langchain.tools import StructuredTool
from backend.app.features.core.services.block_service import BlockService
from typing import List

async def vector_embed(query: str) -> List[float]:
    """
    Embeds the user's query into a vector space.
    """
    block_service = BlockService()
    vector = await block_service.generate_embedding(query)
    return vector

VectorEmbedTool = StructuredTool.from_function(
    func=vector_embed,
    name="VectorEmbedTool",
    description="Embeds the user's query into a vector space."
)
