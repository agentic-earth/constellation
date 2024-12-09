import sys

from backend.app.features.agent.crews.crew_process import CrewProcess

sys.path.append("/Users/justinxiao/Downloads/coursecode/CSCI2340/constellation-backend/api")
sys.path.append("/Users/justinxiao/Downloads/coursecode/CSCI2340/constellation-backend/api/backend")

import asyncio
from prisma import Prisma
from backend.app.config import Settings
from backend.app.features.agent.tools.vector_embed_tool import VectorEmbedTool
from backend.app.features.agent.tools.similarity_search_tool import SimilaritySearchTool
from backend.app.features.core.services.block_service import BlockService


async def test_tools():
    block_service = BlockService()
    settings = Settings()
    prisma = Prisma(datasource={"url": str(settings.DATABASE_URL)})
    crew_process = CrewProcess()
    # dev_crew = DevCrew()
    await prisma.connect()
    print("Connected to db")

    try:
        # Test VectorEmbedTool
        query = "climate change mitigation strategies"
        vector = await VectorEmbedTool.func(query)
        print(f"Vector embedding for '{query}':")
        print(vector[:5])

        sample_papers = [
            {
                "name": "Climate Change Mitigation Strategies",
                "text": "This paper discusses various strategies for mitigating climate change, including renewable energy adoption, carbon capture technologies, and policy interventions.",
                "block_type": "paper",
                "description": "An overview of climate change mitigation approaches",
            },
            {
                "name": "Impact of Rising Sea Levels",
                "text": "This study examines the potential consequences of rising sea levels on coastal communities and ecosystems, proposing adaptation measures.",
                "block_type": "paper",
                "description": "Analysis of sea level rise impacts and adaptation strategies",
            },
            {
                "name": "Renewable Energy Technologies",
                "text": "An in-depth look at current and emerging renewable energy technologies, their efficiencies, and potential for large-scale implementation.",
                "block_type": "paper",
                "description": "Overview of renewable energy technologies and their potential",
            },
        ]

        # Test creating blocks for sample papers
        print("\nCreating blocks for sample papers:")
        for paper in sample_papers:
            created_block = await block_service.create_block(paper)
            if created_block:
                print(f"Created block: {created_block.name}")
                # Retrieve and print the vector for each created block
                block_vector = await block_service.get_block_vector(
                    created_block.block_id
                )
                if block_vector:
                    print(f"Vector for {created_block.name}: {block_vector[:5]}")
                else:
                    print(f"Failed to create block for {paper['title']}")

        # Test SimilaritySearchTool
        print("\nTesting SimilaritySearchTool:")
        similar_blocks = await SimilaritySearchTool.func(vector)
        if similar_blocks:
            print("Similar blocks found:")
            for block in similar_blocks:
                print(
                    f"- {block['name']}: {block['description']} (Similarity: {block['similarity']})"
                )
        else:
            print("No similar blocks found.")

    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback

        print(traceback.format_exc())

    finally:
        await prisma.disconnect()
        print("Disconnected from the database")


if __name__ == "__main__":
    asyncio.run(test_tools())
