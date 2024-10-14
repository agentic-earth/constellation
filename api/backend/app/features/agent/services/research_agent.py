# app/features/agent/services/research_agent.py

"""
Research Agent Module

This module defines the ResearchAgent class, which is responsible for conducting
research tasks within the Constellation ecosystem. It leverages the CrewAI framework
to perform paper analysis and synthesis.

Design Philosophy:
- Utilize CrewAI's Agent class for consistent agent behavior and integration.
- Focus on the agent's core role and goal.
- Implement tools as methods that can be used by the agent during task execution.
"""

from crewai import Agent
from crewai_tools import tool
from langchain_community.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from backend.app.features.core.services.block_service import BlockService
from backend.app.logger import ConstellationLogger
import json
from typing import List, Dict, Any, ClassVar

class PaperAnalysis:
    def __init__(self, papers: List[Dict[str, Any]], analysis: str):
        self.papers = papers
        self.analysis = analysis

class ResearchAgent(Agent):
    find_similar_papers: ClassVar
    analyze_papers: ClassVar

    def __init__(self, **kwargs):
        super().__init__(
            name="Researcher",
            role="Climate Scientist",
            goal="Conduct thorough research on weather/climate topics",
            backstory="As a climate scientist, I am tasked with analyzing research papers and synthesizing information on weather and climate topics.",
            verbose=True,
            allow_delegation=False,
            tools=[self.find_similar_papers],
            # tools=[self.find_similar_papers, self.analyze_papers],
            output_pydantic=PaperAnalysis,
            **kwargs
        )

    @tool("Find Similar Papers")
    def find_similar_papers(self, query: str, top_k: int = 5) -> str:
        """Find papers similar to the given query."""
        block_service = BlockService()
        query_embedding = block_service.generate_embedding(query)
        similar_blocks = block_service.search_blocks_by_vector_similarity(query_embedding, top_k=top_k)
        return json.dumps(similar_blocks)

    # @tool("Analyze Papers")
    # async def analyze_papers(self, papers_json: str, query: str) -> str:
    #     """Analyze the given papers in relation to the query and provide insights."""
    #     papers = json.loads(papers_json)
        
    #     analysis = f"Analysis of top {len(papers)} papers related to '{query}':\n\n"
        
    #     for paper in papers:
    #         paper_name = paper['name']
    #         paper_description = paper.get('description', 'No description available')
    #         similarity_score = paper['similarity']
            
    #         # Generate analysis using the LLM
    #         paper_analysis = await self._generate_paper_analysis(paper_name, paper_description, query, similarity_score)
            
    #         analysis += f"Paper: {paper_name}\n"
    #         analysis += f"Relevance Score: {similarity_score:.2f}\n"
    #         analysis += f"Analysis: {paper_analysis}\n\n"
        
        # return json.dumps(PaperAnalysis(papers=papers, analysis=analysis).__dict())

    # async def _generate_paper_analysis(self, paper_name: str, paper_description: str, query: str, similarity_score: float) -> str:
    #     """Generate a brief analysis of why a paper relates to the query using an LLM."""
    #     try:
    #         analysis = await self.analysis_chain.arun(
    #             paper_name=paper_name,
    #             paper_description=paper_description,
    #             query=query,
    #             similarity_score=f"{similarity_score:.2f}"
    #         )
    #         return analysis.strip()
    #     except Exception as e:
    #         self.logger.error(f"Error generating paper analysis: {str(e)}")
    #         return "Unable to generate analysis due to an error."

