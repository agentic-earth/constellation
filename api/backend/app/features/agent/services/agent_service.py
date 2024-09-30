import asyncio
import aioredis
from uuid import UUID
from some_module import PipelineAPIRequest  # Replace 'some_module' with the actual module name
from pydantic import ValidationError
from logger import ConstellationLogger

class AgentService:

    def __init__(self):
        self.logger = ConstellationLogger().get_logger("AgentService")
        self.redis = aioredis.from_url("redis://localhost")

    async def get_session(self, session_id: UUID) -> dict:
        return await self.redis.get(str(session_id))

    async def update_session(self, session_id: UUID, data: dict) -> None:
        await self.redis.set(str(session_id), data)


if __name__ == "__main__":
    # Example usage
    llm_output = '{"data": {"image_url": "https://example.com/image.jpg"}, "metadata": {"source": "llm"}}'
    pipeline_request = asyncio.run(process_llm_output(llm_output))
    print(pipeline_request)