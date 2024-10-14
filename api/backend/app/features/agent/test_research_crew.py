#test_research_crew.py

"""
Simple test script for the ResearchCrew class.
"""

import asyncio
from dotenv import load_dotenv
from backend.app.features.agent.research_crew import ResearchCrew
from backend.app.features.core.services.block_service import BlockService

async def populate_test_data():
    block_service = BlockService()
    paper = {
        "name": "Short-term Weather Prediction Models",
        "text": "Short term weather prediction models using Graphcast are the future",
        "block_type": "paper",
        "description": "Analysis of short-term weather prediction techniques"
    }
    await block_service.create_block(paper)
    print("Test data populated")

async def main():
    # Load environment variables
    load_dotenv()

    # Populate test data
    await populate_test_data()

    # Create a ResearchCrew instance
    research_crew = ResearchCrew()

    # Run a simple research query
    query = "predicting weather 6 hours in advance"
    result = await research_crew.research(query)

    # Print the result
    print("\nResearch Result:")
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
