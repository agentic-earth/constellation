from backend.app.features.agent.crews.crew import LLMCrew
from crewai import Crew
from prisma.models import Block as PrismaBlock
from typing import List

class CrewProcess:
    """
    CrewProcess class to manage the creation and configuration of research crews.
    """

    def __init__(self):
        """
        Initializes the CrewProcess with a default agent.
        """
        self.agent = LLMCrew().build_agent()

    def make_crews(self, query: str, blocks: List[PrismaBlock]) -> Crew:
        """
        Creates and configures a research crew with the given query and blocks.

        Args:
            query (str): The query string for the research task.
            blocks (List[PrismaBlock]): A list of PrismaBlock objects to be processed.

        Returns:
            Crew: A configured Crew object with the specified agents and tasks.
        """
        # Create and return a Crew object with the specified agent and task
        return Crew(
            agents=[self.agent],
            tasks=[LLMCrew().build_task(query, blocks, self.agent)],
            verbose=False,
        )