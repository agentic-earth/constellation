from backend.app.features.agent.tools.vector_embed_tool import VectorEmbedTool
from backend.app.features.agent.tools.similarity_search_tool import SimilaritySearchTool

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from langchain_openai import ChatOpenAI

@CrewBase
class ResearchCrew:
    """Research Crew"""

    agents_config = "agents_config.yaml"
    tasks_config = "tasks_config.yaml"
    llm = ChatOpenAI(model="gpt-4o")
    
    @agent
    def research_agent() -> Agent:
        return Agent(
            # config=self.agents_config["Researcher_agent"],
            tools=[
                VectorEmbedTool,
                SimilaritySearchTool
            ],
            # llm=ChatOpenAI(model="gpt-4o"),
            goal="Find the most similar paper to the background of human inputs and provide a summary of the paper, and also you should find the link to the GitHub repository of the paper.",
            role="Researcher",
            backstory="You are a researcher that help users look for papers realted to their query.",
            verbose=False,
        )

    @task
    def research_task(self) -> Task:
        return Task(
            config=self.tasks_config["find_similar_papers_task"],
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
