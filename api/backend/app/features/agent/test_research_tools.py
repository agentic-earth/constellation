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
        async with prisma.tx(timeout=10000) as tx:

            # Test VectorEmbedTool
            query = "climate change mitigation strategies"
            vector = await VectorEmbedTool.arun({"query": query})
            print(f"Vector embedding for '{query}':")
            print(vector)  

            sample_papers = [
                {
                    "title":"Machine learning for Earth System Science (ESS): A survey, status and\n  future directions for South Asia",
                    "abstract":"  This survey focuses on the current problems in Earth systems science where\nmachine learning algorithms can be applied. It provides an overview of previous\nwork, ongoing work at the Ministry of Earth Sciences, Gov. of India, and future\napplications of ML algorithms to some significant earth science problems. We\nprovide a comparison of previous work with this survey, a mind map of\nmultidimensional areas related to machine learning and a Gartner's hype cycle\nfor machine learning in Earth system science (ESS). We mainly focus on the\ncritical components in Earth Sciences, including atmospheric, Ocean,\nSeismology, and biosphere, and cover AI/ML applications to statistical\ndownscaling and forecasting problems.\n",
                    "pdf_url":"http://arxiv.org/pdf/2112.12966v1",
                    "block_type":"paper"
                },
                {
                    "title":"Will Artificial Intelligence supersede Earth System and Climate Models?",
                    "abstract":"  We outline a perspective of an entirely new research branch in Earth and\nclimate sciences, where deep neural networks and Earth system models are\ndismantled as individual methodological approaches and reassembled as learning,\nself-validating, and interpretable Earth system model-network hybrids.\nFollowing this path, we coin the term \"Neural Earth System Modelling\" (NESYM)\nand highlight the necessity of a transdisciplinary discussion platform,\nbringing together Earth and climate scientists, big data analysts, and AI\nexperts. We examine the concurrent potential and pitfalls of Neural Earth\nSystem Modelling and discuss the open question whether artificial intelligence\nwill not only infuse Earth system modelling, but ultimately render them\nobsolete.\n",
                    "pdf_url":"http://arxiv.org/pdf/2101.09126v1",
                    "block_type":"paper"
                }
            ]

            # Test creating blocks for sample papers
            print("\nCreating blocks for sample papers:")
            for paper in sample_papers:
                created_block = await block_service.create_block(tx, paper)
                if created_block:
                    print(f"Created block: {created_block}")
                    # Retrieve and print the vector for each created block
                    block_vector = await block_service.get_block_vector(tx, created_block.block_id)
                    if block_vector:
                        print(f"Vector for {created_block}: {block_vector[:5]}")
                    else:
                        print(f"No vector found for {created_block}")
                else:
                    print(f"Failed to create block for {paper['title']}")

            # Test SimilaritySearchTool
            print("\nTesting SimilaritySearchTool:")
            similar_blocks = await SimilaritySearchTool.arun({"vector": vector})
            if similar_blocks:
                print("Similar blocks found:")
                for block in similar_blocks:
                    # Dictionary keys: 'id', 'content', 'dataframe', 'blob', 'score', 'embedding', 'sparse_embedding', 'blockBlock_id'
                    print(f"id: {block['id']} \nContent: {block['content']} \nSimilarity: {block['score']}\n")
            else:
                print("No similar blocks found.")

            print("\nTesting Research Crew:")
            # Get the crew instance
            crew = crew_process.make_crews("climate change")
            print("Crew created")
            # Run the crew
            crew.kickoff()

    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback

        print(traceback.format_exc())

    finally:
        await prisma.disconnect()
        print("Disconnected from the database")


if __name__ == "__main__":
    asyncio.run(test_tools())
