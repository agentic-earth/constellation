import json
import asyncio
from backend.app.features.agent.crews.crew_process import CrewProcess

async def test_tools():
    """
    Tests the functionality of the Research Crew by creating a crew instance,
    running it with a sample query and blocks, and printing the results.

    This function:
    1. Initializes a CrewProcess instance.
    2. Defines a sample query and blocks.
    3. Creates a research crew with the given query and blocks.
    4. Runs the crew and prints the results.
    5. Handles and prints any exceptions that occur during the process.
    """
    crew_process = CrewProcess()

    try:
        print("\nTesting Research Crew:")
        # Define the query and blocks
        query = 'wildfire'
        blocks = [
            {
                "name": "vit-fire-detection",
                "block_type": "model",
                "description": "This is vit fire detection model"
            },
            {
                "name": "vit-fire-dataset",
                "block_type": "dataset",
                "description": "This is the dataset for vit fire model",
                "filepath": "1aniasD6RcD3Zr7K8DSWiiqtXCRbFx7gU"
            }
        ]
        # Create the research crew
        crew = crew_process.make_crews(query, blocks)
        print("Crew created")
        
        # Run the crew
        result = crew.kickoff()
        print("Crew result:", result)
        
        # Parse and print the JSON result
        parsed_result = json.loads(result)
        print("Parsed result:", parsed_result)

    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    # Run the test_tools function asynchronously
    asyncio.run(test_tools())