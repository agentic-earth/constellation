# app/features/agent/services/research_agent.py

"""
Research Agent Module

This module defines the ResearchAgent class, which is responsible for conducting
research tasks within the Constellation ecosystem. It leverages the CrewAI framework
and integrates with core services to perform paper searches and taxonomy analysis.

Design Philosophy:
- Utilize CrewAI's Agent class for consistent agent behavior and integration.
- Leverage Core Microservice components (PipelineService and TaxonomyService) for data access and processing.
- Maintain modularity to allow easy expansion of research capabilities.
- Implement specific research methods that can be called by the research crew or other parts of the system.

Key Components:
- ResearchAgent: A specialized agent class for research tasks.
- search_papers: Method to search for relevant papers based on a query.
- analyze_taxonomy: Method to analyze the taxonomy of a specific paper.

This module is part of the Agent Microservice and plays a crucial role in enabling
intelligent research capabilities within the Constellation Backend.
"""

from crewai import Agent
from backend.app.features.core.services.pipeline_service import PipelineService
from backend.app.features.core.services.taxonomy_service import TaxonomyService

class ResearchAgent(Agent):
    def __init__(self, pipeline_service: PipelineService, taxonomy_service: TaxonomyService):
        super().__init__(
            name="Researcher",
            role="Research Specialist",
            goal="Conduct thorough research and analysis on given topics",
            backstory="As an AI research specialist, I have access to vast amounts of information and can quickly analyze and synthesize data to provide insights.",
            verbose=True,
            allow_delegation=False
        )
        self.pipeline_service = pipeline_service
        self.taxonomy_service = taxonomy_service

    def search_papers(self, query: str):
        # Implement paper search logic here
        # This method should use the pipeline_service and taxonomy_service as needed
        pass

    def analyze_taxonomy(self, paper_id: str):
        # Implement taxonomy analysis logic here
        # This method should use the taxonomy_service
        pass

