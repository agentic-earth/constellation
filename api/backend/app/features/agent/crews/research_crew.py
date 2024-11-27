import logging
from typing import Any, Dict, List
from backend.app.features.agent.tools.vector_embed_tool import VectorEmbedTool
from backend.app.features.agent.tools.similarity_search_tool import SimilaritySearchTool
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
import yaml

class ResearchCrew:
    '''Research Crew'''

    def __init__(self):
        with open("C:/Users/JXPARATROOPER/Desktop/CourseCode/CSCI 2340/constellation-backend/api/backend/app/features/agent/config/agents.yaml", "r") as file:
            self.agents_config = yaml.safe_load(file)
        with open("C:/Users/JXPARATROOPER/Desktop/CourseCode/CSCI 2340/constellation-backend/api/backend/app/features/agent/config/tasks.yaml", "r") as file:
            self.tasks_config = yaml.safe_load(file)
        self.llm = ChatOpenAI(model="gpt-4o")

    @staticmethod
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
    
    @staticmethod
    def research_task(query: str, agent: Agent) -> Task:
        return Task(
            # config=self.tasks_config["find_similar_paper"],
            description=f"Find the most similar paper to user's query: '{query}', provide a summary of the paper, and also you should find the link to the GitHub repository of the paper. if the paper is not found, provide a message to the user that no papers have been found.",
            # prompt_context='You are a researcher looking for similar papers to a given query.',
            # description="Process the user query through vector embedding and similarity search, then analyze the results",
            prompt_context='Process user query and analyze the results',
            agent=agent,
            # process=Process.sequential,
            expected_output="JSON string of similar papers",
            verbose=True,
            # human_input=True,
        )
