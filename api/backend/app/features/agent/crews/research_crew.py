from crewai import Crew, Agent, Process, Task
from crewai.project import CrewBase, agent, crew, task
from langchain_openai import ChatOpenAI
from backend.app.features.agent.tools.vector_embed_tool import VectorEmbedTool
from backend.app.features.agent.tools.similarity_search_tool import SimilaritySearchTool

@CrewBase
class ResearchCrew:
    '''Research Crew'''

    agents_config = "agents_config.yaml"
    tasks_config = "tasks_config.yaml"
    llm = ChatOpenAI(model="gpt-4o")

    @agent
    def research_agent(self) -> Agent:

        return Agent(
            config=self.agents_config["research_agent"],
            tools=[
                VectorEmbedTool(),
                SimilaritySearchTool(),
            ],
            llm=self.llm,
            verbose=True,
        )
    
    @task
    def research_task(self) -> Task:
        return Task(
            config=self.tasks_config["research_task"],
            agent=self.research_agent,
            process=Process.sequential,
        )
    
    @crew
    def research_crew(self) -> Crew:
        return Crew(
            agents=[self.research_agent],
            tasks=[self.research_task],
            verbose=2,
        )
    