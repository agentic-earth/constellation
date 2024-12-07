from typing import List
from crewai import Agent, Task
from langchain_openai import ChatOpenAI
from prisma.models import Block as PrismaBlock

class LLMCrew:
    """LLM Crew"""
    def __init__(self):
        pass

    @staticmethod
    def build_agent() -> Agent:
        """
        Builds and returns an Agent configured with a large language model.

        Returns:
            Agent: An Agent object configured with a large language model.
        """
        return Agent(
            llm=ChatOpenAI(model="gpt-3.5-turbo"),
            verbose=False,
            role="Analyst",
            goal="Follow the instructions",
            backstory="There are some data that need to be processed and you are the one who can do it.",
        )
    
    @staticmethod
    def build_task(query: str, blocks: List[PrismaBlock], agent: Agent) -> Task:
        """
        Builds and returns a Task configured with the given query, blocks, and agent.

        Args:
            query (str): The user's query string.
            blocks (List[PrismaBlock]): A list of PrismaBlock objects representing models and datasets.
            agent (Agent): The agent responsible for executing the task.

        Returns:
            Task: A Task object configured with the specified query, blocks, and agent.
        """
        return Task(
            description='''
            You are given a user's query, as well as a list of objects representing models and datasets. Each object has at least the fields name, block_type, and description. Datasets also have a filepath field. Your task is to:
            1. Identify which model(s) and dataset(s) are related to the user's query. (“Related” could mean the model or dataset's name or description contains the user's query.)
            2. From the matched model with block_type = "model", extract the model's name and place it into the {xxx} placeholder.
            3. From the matched dataset with block_type = "dataset", extract the dataset's filepath and place it into the {yyy} placeholder.
            4. If multiple matches exist, use the first or most relevant matches.
            5. Output only the final JSON structure, with no additional explanation.

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
                            "operation": "export_to_s3",
                            "parameters": {
                            "inference_results": [
                                {
                                "operation": "model_inference",
                                "parameters": {
                                    "data": {
                                    "operation": "dict_to_list",
                                    "parameters": {
                                        "data": {
                                        "operation": "import_from_google_drive",
                                        "parameters": {
                                            "file_id": "{yyy}"
                                        }
                                        }
                                    }
                                    },
                                    "model": "{xxx}"
                                }
                                }
                            ]
                            }
                        },
                        {
                            "operation": "delete_model",
                            "parameters": {
                            "model": "{xxx}"
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
            expected_output="formatted JSON",
            verbose=False,
        )