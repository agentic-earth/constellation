from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from langchain_openai import ChatOpenAI

@CrewBase
class DevCrew:
    '''Developer Crew'''
    agents_config = "agents_config.yaml"
    tasks_config = "tasks_config.yaml"
    llm = ChatOpenAI(model="gpt-4o")

    @agent
    def develop_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["developer_agent"],
            llm=self.llm,
            verbose=True,
        )
    
    @task
    def develop_task(self) -> Task:
        return Task(
            config=self.tasks_config["generate_pseudocode"],
            agent=self.develop_agent,
            process=Process.sequential,
        )
    
    @crew
    def develop_crew(self) -> Crew:
        return Crew(
            agents=[self.develop_agent],
            tasks=[self.develop_task],
            verbose=2,
        )