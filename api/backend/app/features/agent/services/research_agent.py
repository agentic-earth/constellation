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
from crewai_tools import PDFSearchTool
from backend.app.features.core.services.pipeline_service import PipelineService
from backend.app.features.core.services.taxonomy_service import TaxonomyService
from backend.app.features.core.services.vector_embedding_service import VectorEmbeddingService
from backend.app.logger import ConstellationLogger
from backend.app.embeddings import PDFEmbeddingService
from typing import List, Dict
class ResearchAgent(Agent):
    def __init__(self, pipeline_service: PipelineService, taxonomy_service: TaxonomyService, vector_embedding_service: VectorEmbeddingService, pdf_embedding_service: PDFEmbeddingService):

        papersearchtool = PDFSearchTool(config=dict(
            llm=dict(
                provider="OpenAI",
                config=dict(
                    model="gpt-4o-mini",
                    temperature=0.5,
                    top_p=1,
                    stream=True,
                ),
            ),
            embedder=dict(
                provider="custom",
                config=dict(
                    embed_function=pdf_embedding_service.create_embeddings,
                ),
            ),
        ))
        super().__init__(
            name="Researcher",
            role="Climate Scientist",
            goal="Conduct thorough research on weather/climate topics",
            backstory="As a climate scientist, I am tasked with conducting research on weather and climate topics.",
            verbose=True,
            allow_delegation=False,
            tools=[papersearchtool]
        )
        self.pipeline_service = pipeline_service
        self.taxonomy_service = taxonomy_service
        self.pdf_embedding_service = pdf_embedding_service
        self.vector_embedding_service = vector_embedding_service
        self.logger = ConstellationLogger("ResearchAgent")

    def find_similar_papers(self, query: str, top_k: int = 5) -> List[Dict[str, str]]:
        # Embed the query
        query_embedding = self.pdf_embedding_service.embed_query(query)
        
        # Search for similar papers
        similar_blocks = self.vector_embedding_service.search_similar_blocks(query_embedding, top_k=top_k)
        
        # Format the results
        results = []
        for block in similar_blocks:
            results.append({
                "title": block.name,  # Assuming the paper title is stored in the 'name' field
                "link": block.metadata.get("link", "No link available")  # Assuming the link is stored in metadata
            })
        
        return results
