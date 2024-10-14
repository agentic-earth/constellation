import asyncio
from backend.app.features.agent.tools.vector_embed_tool import VectorEmbedTool
from backend.app.features.agent.tools.similarity_search_tool import SimilaritySearchTool
from backend.app.features.core.services.block_service import BlockService


async def test_tools():
    block_service = BlockService()
    await block_service.connect()

    try:
        # Test VectorEmbedTool
        query = "climate change mitigation strategies"
        vector = await VectorEmbedTool.func(query)
        print(f"Vector embedding for '{query}':")
        print(vector[:5])  # Print first 5 elements of the vector

        sample_papers = [
            {
                "name": "Climate Change Mitigation Strategies",
                "text": "This paper discusses various strategies for mitigating climate change, including renewable energy adoption, carbon capture technologies, and policy interventions.",
                "block_type": "paper",
                "description": "An overview of climate change mitigation approaches"
            },
            {
                "name": "Impact of Rising Sea Levels",
                "text": "This study examines the potential consequences of rising sea levels on coastal communities and ecosystems, proposing adaptation measures.",
                "block_type": "paper",
                "description": "Analysis of sea level rise impacts and adaptation strategies"
            },
            {
                "name": "Renewable Energy Technologies",
                "text": "An in-depth look at current and emerging renewable energy technologies, their efficiencies, and potential for large-scale implementation.",
                "block_type": "paper",
                "description": "Overview of renewable energy technologies and their potential"
            }
        ]

        for paper in sample_papers:
            created_block = await block_service.create_block(paper)
            if created_block:
                print(f"Created block: {created_block.name}")
                # Retrieve and print the vector for each created block
                block_vector = await block_service.get_block_vector(created_block.block_id)
                print(f"Vector for {created_block.name}: {block_vector[:5] if block_vector else 'None'}")

        print("Sample papers populated successfully")

        # Retrieve all vectors to make sure they're stored
        all_vectors = await block_service.get_all_vectors()
        print(f"Total vectors retrieved: {len(all_vectors)}")

        # Test SimilaritySearchTool
        results = await SimilaritySearchTool.func(vector)
        print("\nSimilar papers found:")
        if results:
            for result in results:
                print(f"- {result['name']}: {result['description']} (Similarity: {result['similarity']})")
        else:
            print("No similar papers found.")

        # If no results, try direct similarity search
        if not results:
            print("\nTrying direct similarity search:")
            direct_results = await block_service.search_blocks_by_vector_similarity(vector)
            if direct_results:
                for result in direct_results:
                    print(f"- {result['name']}: {result['description']} (Similarity: {result['similarity']})")
            else:
                print("No results from direct similarity search.")
    finally:
        await block_service.disconnect()

if __name__ == "__main__":
    asyncio.run(test_tools())
