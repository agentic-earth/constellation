from backend.app.features.agent.crews.research_crew import ResearchCrew
from crewai import Crew
from prisma.models import Block as PrismaBlock
from typing import List

class CrewProcess:
    def __init__(self):
        self.research_agent = ResearchCrew().research_agent()
        # self.developer = DevCrew()

    def make_crews(self, query: str, blocks: List[PrismaBlock]) -> Crew:
        return Crew(
            agents=[self.research_agent],
            tasks=[ResearchCrew().research_task(query, blocks, self.research_agent)],
            verbose=False,
            # memory=True,
            # planning=True  # Enable planning feature for the crew
        )
