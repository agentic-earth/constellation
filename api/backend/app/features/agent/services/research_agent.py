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
- Utilize ConstellationLogger for consistent and centralized logging.

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
from backend.app.logger import ConstellationLogger

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
        self.logger = ConstellationLogger("ResearchAgent")

    def search_papers(self, query: str):
        """
        Search for relevant papers based on the given query.

        Args:
            query (str): The search query string.

        Returns:
            list: A list of dictionaries containing paper information.
        """
        self.logger.debug(f"Initiating paper search with query: {query}")
        try:
            # Use the pipeline service to search for papers
            search_results = self.pipeline_service.search_papers(query)

            # Process and format the search results
            formatted_results = []
            for paper in search_results:
                formatted_results.append({
                    'id': paper.id,
                    'title': paper.title,
                    'authors': paper.authors,
                    'abstract': paper.abstract,
                    'publication_date': paper.publication_date,
                    'relevance_score': paper.relevance_score
                })

            self.logger.info(f"Successfully found {len(formatted_results)} papers matching the query: {query}")
            return formatted_results
        except Exception as e:
            self.logger.error(f"Error occurred while searching papers: {str(e)}", exc_info=True)
            raise

    def analyze_taxonomy(self, paper_id: str):
        """
        Analyze the taxonomy of a specific paper.

        Args:
            paper_id (str): The unique identifier of the paper to analyze.

        Returns:
            dict: A dictionary containing the taxonomy analysis results.
        """
        self.logger.debug(f"Starting taxonomy analysis for paper ID: {paper_id}")
        try:
            # Retrieve the paper details using the pipeline service
            paper = self.pipeline_service.get_paper(paper_id)

            if not paper:
                self.logger.warning(f"Paper not found for ID: {paper_id}")
                return {"error": "Paper not found"}

            # Use the taxonomy service to analyze the paper's content
            taxonomy_analysis = self.taxonomy_service.analyze_paper(paper.content)

            # Process and format the taxonomy analysis results
            formatted_analysis = {
                'paper_id': paper_id,
                'title': paper.title,
                'main_topics': taxonomy_analysis.main_topics,
                'subtopics': taxonomy_analysis.subtopics,
                'key_concepts': taxonomy_analysis.key_concepts,
                'related_fields': taxonomy_analysis.related_fields
            }

            self.logger.info(f"Successfully completed taxonomy analysis for paper ID: {paper_id}")
            return formatted_analysis
        except Exception as e:
            self.logger.error(f"Error occurred during taxonomy analysis for paper ID {paper_id}: {str(e)}", exc_info=True)
            raise
