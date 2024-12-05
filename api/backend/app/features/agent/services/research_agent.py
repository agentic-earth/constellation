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
from backend.app.features.core.services.block_service import BlockService
import json
from typing import List, Dict, Any, ClassVar


class ResearchAgent(Agent):
    def __init__(self, **kwargs):
        super().__init__(
            name="Researcher",
            role="Climate Scientist",
            goal="Find and analyze the most relevant papers for climate-related queries",
            backstory="As a climate scientist, I specialize in finding and analyzing research papers to provide insights on climate topics.",
            verbose=True,
            allow_delegation=False,
            tools=[self.find_similar_papers],
            **kwargs,
        )

    @tool
    async def find_similar_papers(self, query: str, top_k: int = 5) -> str:
        """Find papers similar to the given query."""
        try:
            query_embedding = await self.block_service.generate_embedding(query)
            similar_blocks = (
                await self.block_service.search_blocks_by_vector_similarity(
                    query_embedding, top_k=top_k
                )
            )
            return json.dumps(similar_blocks)
        except Exception as e:
            self.logger.error(f"Error in find_similar_papers: {str(e)}")
            return json.dumps({"error": "Failed to find similar papers"})

    # @tool("Analyze Papers")
    # async def analyze_papers(self, papers_json: str, query: str) -> str:
    #     """Analyze the relevance of given papers to the query."""
    #     try:
    #         papers = json.loads(papers_json)
    #         analysis = f"Analysis of top {len(papers)} papers related to '{query}':\n\n"
    #         for paper in papers:
    #             paper_name = paper['name']
    #             paper_description = paper.get('description', 'No description available')
    #             similarity_score = paper['similarity']

    #             analysis += f"Paper: {paper_name}\n"
    #             analysis += f"Relevance Score: {similarity_score:.2f}\n"
    #             analysis += f"Description: {paper_description}\n"
    #             analysis += f"Relevance: This paper is relevant because it discusses aspects of {query}.\n\n"

    #         return json.dumps({"analysis": analysis})
    #     except Exception as e:
    #         self.logger.error(f"Error in analyze_papers: {str(e)}")
    #         return json.dumps({"error": "Failed to analyze papers"})
