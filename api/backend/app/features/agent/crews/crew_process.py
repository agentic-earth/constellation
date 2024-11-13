from backend.app.features.agent.crews.research_crew import ResearchCrew
from crewai import Crew

class CrewProcess:
    def __init__(self):
        self.researcher = ResearchCrew()
        # self.developer = DevCrew()

    def make_crews(self) -> Crew:
        return Crew(
            agents=[self.researcher.research_agent_],
            tasks=[self.researcher.research_task_],
            verbose=True,
            memory=True,
            planning=True  # Enable planning feature for the crew
        )

# if __name__ == "__main__":
#     crew_process = CrewProcess()
#     crews = crew_process.make_crews()
#     crews.kickoff()