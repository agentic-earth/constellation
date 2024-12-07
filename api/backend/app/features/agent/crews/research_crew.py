import logging
from typing import Any, Dict, List
# from backend.app.features.agent.tools.vector_embed_tool import VectorEmbedTool
# from backend.app.features.agent.tools.similarity_search_tool import SimilaritySearchTool
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from prisma.models import Block as PrismaBlock
import yaml

class ResearchCrew:
    """Research Crew"""

    def __init__(self):
        # with open("C:/Users/JXPARATROOPER/Desktop/CourseCode/CSCI 2340/constellation-backend/api/backend/app/features/agent/config/agents.yaml", "r") as file:
        #     self.agents_config = yaml.safe_load(file)
        # with open("C:/Users/JXPARATROOPER/Desktop/CourseCode/CSCI 2340/constellation-backend/api/backend/app/features/agent/config/tasks.yaml", "r") as file:
        #     self.tasks_config = yaml.safe_load(file)
        pass

    @staticmethod
    def research_agent() -> Agent:
        return Agent(
            # config=self.agents_config["Researcher_agent"],
            # tools=[
            #     VectorEmbedTool,
            #     SimilaritySearchTool
            # ],
            llm=ChatOpenAI(model="gpt-3.5-turbo"),
            # goal="Find the most similar paper to the background of human inputs and provide a summary of the paper, and also you should find the link to the GitHub repository of the paper.",
            # role="Researcher",
            # backstory="You are a researcher that help users look for papers realted to their query.",
            verbose=False,
            role="Analyst",
            goal="Follow the instructions",
            backstory="There are some data that need to be processed and you are the one who can do it.",
        )
    
    @staticmethod
    def research_task(query: str, blocks: List[PrismaBlock], agent: Agent) -> Task:
        return Task(
            # config=self.tasks_config["find_similar_paper"],
            # description=f"",
            # prompt_context='You are a researcher looking for similar papers to a given query.',
            # description="Process the user query through vector embedding and similarity search, then analyze the results",
            description='''
        You are given a user's query, as well as a list of objects representing models and datasets. Each object has at least the fields name, block_type, and description. Datasets also have a filepath field. Your task is to:
            1.	Identify which model(s) and dataset(s) are related to the user's query. (“Related” could mean the model or dataset's name or description contains the user's query.)
            2.	From the matched model with block_type = "model", extract the model's name and place it into the {xxx} placeholder.
            3.	From the matched dataset with block_type = "dataset", extract the dataset's filepath and place it into the {yyy} placeholder.
            4.	If multiple matches exist, use the first or most relevant matches.
            5.	Output only the final JSON structure, with no additional explanation.

            Here is the user query:
            '''
            + query +
            '''

            Here is the input list of objects:

            ''' 
            + str(blocks) +
            '''
            From this input, produce the following JSON output:
            {
                "ops": {
                    "generate_dynamic_job_configs": {
                        "config": {
                            "raw_input": [
                                {
                                    "operation": "deploy_model",
                                    "parameters": {
                                        "model": "{xxx}"
                                    }
                                },
                                {
                                    "operation": "import_from_google_drive",
                                    "parameters": {
                                        "file_id": "{yyy}"
                                    }
                                },
                                {
                                    "operation": "delete_model",
                                    "parameters": {
                                        "service_name": "{xxx}-service"
                                    }
                                }
                            ]
                        }
                    }
                }
            }

            Output only the final JSON without additional explanation or formatting.
            ''',
            agent=agent,
            # process=Process.sequential,
            expected_output="formatted JSON",
            verbose=True,
            # human_input=True,

        )

