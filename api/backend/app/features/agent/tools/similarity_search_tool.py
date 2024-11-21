import asyncio
import nest_asyncio
from langchain.tools import StructuredTool
from backend.app.features.core.services.block_service import BlockService
from langchain.tools import BaseTool
from typing import List, Dict, Any

def _run(vector: List[float]) -> List[Dict[str, Any]]:
    """Synchronous run method"""
    try:
        # Use nest_asyncio to handle nested event loops
        nest_asyncio.apply()
        
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(_arun(vector))
    except Exception as e:
        raise RuntimeError(f"Error in vector embedding: {str(e)}")



async def _arun(vector: List[float]) -> List[Dict[str, Any]]:
    """Asynchronous run method"""
    try:
        block_service = BlockService()
        results = await block_service.search_blocks_by_vector_similarity(vector)
        return results
    except Exception as e:
        raise RuntimeError(f"Error in similarity search: {str(e)}")
        
# Wrap the tool in LangChain's Tool object
SimilaritySearchTool = StructuredTool.from_function(
    name="similarity_search",
    description="Search for similar blocks using vector similarity",
    func=_run,  # Use the synchronous method
    coroutine=_arun  # Provide the asynchronous method
)
