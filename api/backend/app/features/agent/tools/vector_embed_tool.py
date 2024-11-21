import asyncio
import nest_asyncio
from langchain.tools import StructuredTool
from backend.app.features.core.services.vector_embedding_service import VectorEmbeddingService
from langchain.tools import BaseTool
from typing import List, Optional
import asyncio

def _run(query: str) -> List[float]:
    """Synchronous run method"""
    try:
        # Use nest_asyncio to handle nested event loops
        nest_asyncio.apply()
        
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(_arun(query))
    except Exception as e:
        raise RuntimeError(f"Error in vector embedding: {str(e)}")



async def _arun(query: str) -> List[float]:
    """Asynchronous run method"""
    try:
        embedding_service = VectorEmbeddingService()
        vector = await embedding_service.generate_text_embedding(query)
        return vector
    except Exception as e:
        raise RuntimeError(f"Error generating embedding: {str(e)}")

# Wrap the tool in LangChain's Tool object
VectorEmbedTool = StructuredTool.from_function(
    name="vector_embed",
    description="Embeds text into vector space",
    func=_run,  # Use the synchronous version as the primary entry point
    coroutine=_arun  # Optionally include the asynchronous version
)
     
if __name__ == "__main__":
   print(VectorEmbedTool.arun({"query": "climate change mitigation strategies"}))