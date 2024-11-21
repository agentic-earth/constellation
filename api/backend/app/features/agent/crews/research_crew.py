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
        self.research_agent_ = self.research_agent()
        self.research_task_ = self.research_task()

    # def get_user_query(self) -> str:
    #     """
    #     Get research query from user
    #     """
    #     print("\n=== Research Paper Search ===")
    #     print("Please enter your research topic or keywords.")
    #     print("Example: 'machine learning in healthcare' or 'quantum computing algorithms'")
    #     return input("\nYour query: ").strip()

    # async def process_query(self, query: str) -> List[Dict[str, Any]]:
    #     """Process user query through vector embedding and similarity search"""
    #     try:
    #         # Generate vector embedding
    #         vector = await self.vector_tool.invoke({"text": query})
    #         print(f"Vector!!!: {vector}")
    #         if not vector:
    #             raise ValueError("Failed to generate vector embedding")

    #         # Perform similarity search
    #         results = await self.similarity_tool.invoke({"vector": vector})
    #         print(f"Results: {results}")
    #         return results
    #     except Exception as e:
    #         logging.error(f"Error processing query: {e}")
    #         return []

    def research_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["Researcher_agent"],
            tools=[
                VectorEmbedTool,
                SimilaritySearchTool
            ],
            llm=self.llm,
            goal="Find the most similar paper to the background of human inputs and provide a summary of the paper, and also you should find the link to the GitHub repository of the paper.",
            role="Researcher",
            backstory="You are a researcher looking for similar papers to a given query.",
            verbose=True,
        )
    
    def research_task(self) -> Task:
        return Task(
            # config=self.tasks_config["find_similar_paper"],
            description="Find the most similar paper to the background of user input query and provide a summary of the paper, and also you should find the link to the GitHub repository of the paper.",
            prompt_context='You are a researcher looking for similar papers to a given query.',
            # description="Process the user query through vector embedding and similarity search, then analyze the results",
            # prompt_context='Process query and analyze results',
            agent=self.research_agent_,
            # process=Process.sequential,
            # expected_output="JSON string of similar papers",
            verbose=True,
            human_input=True,
            # input_function=self.get_user_query,
            # output_function=self.process_query
        )
    
    # def create_research_crew(self) -> Crew:
    #     return Crew(
    #         agents=[self.research_agent_],
    #         tasks=[self.research_task_],
    #         verbose=True,
    #     )
    
# if __name__ == "__main__":
#     crew = ResearchCrew()
#     crew.create_research_crew().kickoff()
