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

from crewai import Agent, Crew, Task
from backend.app.features.core.services.pipeline_service import PipelineService
from backend.app.features.core.services.taxonomy_service import TaxonomyService
from .researcher_agent import ResearcherAgent

def create_research_crew():
    pipeline_service = PipelineService()
    taxonomy_service = TaxonomyService()

    researcher = ResearcherAgent(pipeline_service, taxonomy_service)

    research_task = Task(
        description="Research recent advancements in AI for climate modeling",
        agent=researcher
    )

    crew = Crew(
        agents=[researcher],
        tasks=[research_task]
    )

    return crew

if __name__ == "__main__":
    crew = create_research_crew()
    result = crew.kickoff()
    print(result)