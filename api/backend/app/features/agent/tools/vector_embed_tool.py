from langchain.tools import StructuredTool
from backend.app.features.core.services.vector_embedding_service import VectorEmbeddingService
from typing import List

async def vector_embed(query: str) -> List[float]:
    """
    Embeds the user's query into a vector space.
    """
    test_embedding_service = VectorEmbeddingService()
    vector = await test_embedding_service.generate_text_embedding(query)
    return vector

VectorEmbedTool = StructuredTool.from_function(
    func=vector_embed,
    name="VectorEmbedTool",
    description="Embeds the user's query into a vector space."
)
