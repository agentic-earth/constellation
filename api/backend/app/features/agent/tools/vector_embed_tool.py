import asyncio
import nest_asyncio
from langchain.tools import StructuredTool
from backend.app.features.core.services.vector_embedding_service import (
    VectorEmbeddingService,
)
from langchain.tools import BaseTool
from typing import List, Optional
import asyncio


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
    description="Embeds the user's query into a vector space.",
)

if __name__ == "__main__":
    print(VectorEmbedTool.arun({"query": "climate change mitigation strategies"}))
