# app/features/agent/research_crew.py

"""
Research Crew Module

This module orchestrates the creation and execution of a research crew using the CrewAI framework.
It integrates with the Core Microservice to leverage pipeline and taxonomy services, enabling
sophisticated research tasks related to AI and climate modeling.

Design Philosophy:
- Utilize CrewAI for task orchestration and agent interaction.
# - Integrate seamlessly with Core Microservice components for data access and processing.
# - Maintain flexibility to accommodate various research tasks and agent configurations.
# - Ensure modularity to allow easy expansion of research capabilities.
# """

# import sys
# import os
# from typing import List, Dict, Any
# from crewai import Crew, Task
# from backend.app.logger import ConstellationLogger
# from backend.app.features.agent.services.research_agent import ResearchAgent
# from backend.app.features.core.services.block_service import BlockService
# import json

# class ResearchCrew:
#     def __init__(self):
#         self.logger = ConstellationLogger().get_logger("ResearchCrew")
#         self.researcher = ResearchAgent()
#         self.block_service = BlockService()

#     def create_research_tasks(self, query: str) -> List[Task]:
#         find_papers_task = Task(
#             description=f"Find papers related to: {query}",
#             agent=self.researcher,
#             expected_output="JSON string of similar papers"
#         )
        
#         # analyze_papers_task = Task(
#         #     description=f"Analyze the papers found in relation to: {query}",
#         #     agent=self.researcher,
#         #     expected_output="JSON string of paper analysis"
#         # )
        
#         # return [find_papers_task, analyze_papers_task]
#         return [find_papers_task]

#     async def research(self, query: str) -> str:
#         tasks = self.create_research_tasks(query)
        
#         crew = Crew(
#             agents=[self.researcher],
#             tasks=tasks,
#             verbose=True
#         )

#         result = crew.kickoff()
        
#         # Process and format the result
#         try:
#             papers = json.loads(result[0])
#             analysis = json.loads(result[1])
            
#             formatted_result = {
#                 "query": query,
#                 "papers": papers,
#                 "analysis": analysis["analysis"]
#             }
            
#             return json.dumps(formatted_result)
#         except Exception as e:
#             self.logger.error(f"Error processing research result: {str(e)}")
#             return json.dumps({"error": "Failed to process research result"})
