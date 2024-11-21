from backend.app.features.agent.crews.research_crew import ResearchCrew
from crewai import Crew

class CrewProcess:
    def __init__(self):
        self.research_agent = ResearchCrew().research_agent()
        # self.developer = DevCrew()

    def make_crews(self, query: str) -> Crew:
        return Crew(
            agents=[self.research_agent],
            tasks=[ResearchCrew().research_task(query, self.research_agent)],
            verbose=False,
            memory=True,
            planning=True  # Enable planning feature for the crew
        )
