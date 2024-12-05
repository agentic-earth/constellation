# app/features/agent/dev_crew.py

"""
Dev Crew Module

This module orchestrates the creation and execution of a development crew using the CrewAI framework.
It integrates with the Core Microservice to leverage pipeline and taxonomy services, enabling
sophisticated development tasks related to analyzing GitHub repositories.

Design Philosophy:
- Utilize CrewAI for task orchestration and agent interaction.
- Integrate seamlessly with Core Microservice components for data access and processing.
- Maintain flexibility to accommodate various development tasks and agent configurations.
- Ensure modularity to allow easy expansion of development capabilities.
- Leverage GitHub integration for repository analysis and code generation tasks.
"""

import sys
import os


# Add the parent directory of 'backend' to the Python path
# Before running, be sure to run the following command: `cd api` to get to the api directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "/backend")))

from crewai import Crew, Task
from backend.app.logger import ConstellationLogger
from backend.app.features.core.services.pipeline_service import PipelineService
from backend.app.features.core.services.taxonomy_service import TaxonomyService
from backend.app.features.agent.services.dev_agent import DevAgent


def create_dev_crew(github_repo_url: str):
    logger = ConstellationLogger().get_logger("DevCrew")
    pipeline_service = PipelineService()
    taxonomy_service = TaxonomyService()

    developer = DevAgent(github_repo_url, pipeline_service, taxonomy_service)
    logger.info(f"Developer created: {developer}")
    development_task = Task(
        description=f"Search for information in the GitHub repository: {github_repo_url}. "
        f"Focus on recent code changes, open issues, and pull requests. ",
        agent=developer,
        expected_output="Provide me a python code that utilizes the BERTopic library to perform topic modeling on a given dataset",
    )
    logger.info(f"Development task created: {development_task}")
    crew = Crew(agents=[developer], tasks=[development_task])
    logger.info(
        f"Dev Crew created with {len(crew.agents)} agents and {len(crew.tasks)} tasks"
    )
    return crew


if __name__ == "__main__":
    os.environ["OPENAI_API_KEY"] = (
        "OPENAI_API_KEY"
    )

    SUPABASE_URL = ""
    SUPABASE_KEY = "SUPABASE_KEY"
    SUPABASE_SERVICE_KEY = "SUPABASE_SERVICE_KEY"
    os.environ["SUPABASE_URL"] = SUPABASE_URL
    os.environ["SUPABASE_KEY"] = SUPABASE_KEY
    os.environ["SUPABASE_SERVICE_KEY"] = SUPABASE_SERVICE_KEY

    crew = create_dev_crew("https://github.com/MaartenGr/BERTopic")
    result = crew.kickoff()
    print(result)
