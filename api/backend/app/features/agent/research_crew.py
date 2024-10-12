# app/features/agent/research_crew.py

"""
Research Crew Module

This module orchestrates the creation and execution of a research crew using the CrewAI framework.
It integrates with the Core Microservice to leverage pipeline and taxonomy services, enabling
sophisticated research tasks related to AI and climate modeling.

Design Philosophy:
- Utilize CrewAI for task orchestration and agent interaction.
- Integrate seamlessly with Core Microservice components for data access and processing.
- Maintain flexibility to accommodate various research tasks and agent configurations.
- Ensure modularity to allow easy expansion of research capabilities.
"""

import sys
import os

# Add the parent directory of 'backend' to the Python path
# Before running, be sure to run the following command: `cd api` to get to the api directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),  '..', '..', '..', '..', '..')))

from crewai import Crew, Task
from backend.app.logger import ConstellationLogger
from backend.app.features.core.services.pipeline_service import PipelineService
from backend.app.features.core.services.taxonomy_service import TaxonomyService
from backend.app.features.agent.services.research_agent import ResearchAgent

def create_research_crew(research_topic: str, pdf_directory: str = 'api/backend/app/features/agent/services/assets'):
    logger = ConstellationLogger().get_logger("ResearchCrew")
    pipeline_service = PipelineService()
    taxonomy_service = TaxonomyService()

    researcher = ResearchAgent(pipeline_service, taxonomy_service)
    logger.info(f'Researcher created: {researcher}')

    research_task = Task(
        description=f'Research recent advancements in {research_topic} using the papers in {pdf_directory}. '
                    f'Focus on latest publications, key findings, and potential applications.',
        agent=researcher,
        expected_output='Provide a list of recent papers on {research_topic} with their titles and links.'
    )
    logger.info(f'Research task created: {research_task}')

    crew = Crew(
        agents=[researcher],
        tasks=[research_task]
    )
    logger.info(f'Research Crew created with {len(crew.agents)} agents and {len(crew.tasks)} tasks')
    return crew


if __name__ == "__main__":
    os.environ['OPENAI_API_KEY'] = 'OPENAI_API_KEY'

    SUPABASE_URL=''
    SUPABASE_KEY='SUPABASE_KEY'
    SUPABASE_SERVICE_KEY='SUPABASE_SERVICE_KEY'
    os.environ['SUPABASE_URL'] = SUPABASE_URL
    os.environ['SUPABASE_KEY'] = SUPABASE_KEY
    os.environ['SUPABASE_SERVICE_KEY'] = SUPABASE_SERVICE_KEY

    crew = create_research_crew('predicting weather 6 hours in advance')
    result = crew.kickoff()
    print(result)