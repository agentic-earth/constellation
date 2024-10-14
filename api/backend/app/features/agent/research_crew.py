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
from typing import List, Dict, Any
from crewai import Crew, Task
from backend.app.logger import ConstellationLogger
from backend.app.features.agent.services.research_agent import ResearchAgent, PaperAnalysis
from backend.app.features.core.services.block_service import BlockService
import json

class ResearchCrew:
    def __init__(self):
        self.logger = ConstellationLogger().get_logger("ResearchCrew")
        self.researcher = ResearchAgent()

    def create_research_tasks(self, query: str) -> List[Task]:
        find_papers_task = Task(
            description=f"Find papers related to: {query}",
            agent=self.researcher,
            tools=[self.researcher.find_similar_papers],
            expected_output="JSON string of paper analysis"  # Provide a string description
        )
        
        # analyze_papers_task = Task(
        #     description=f"Analyze the papers found in relation to: {query}",
        #     agent=self.researcher,
        #     tools=[self.researcher.analyze_papers],
        #     expected_output="JSON string of paper analysis"  # Provide a string description
        # )
        
        # return [find_papers_task, analyze_papers_task]
        return [find_papers_task]

    async def research(self, query: str) -> str:
        tasks = self.create_research_tasks(query)
        
        crew = Crew(
            agents=[self.researcher],
            tasks=tasks,
            verbose=True
        )

        result = crew.kickoff()
        
        # Check if result is a CrewOutput object
        if hasattr(result, 'tasks'):
            # Return the last task's output
            return result.tasks[-1].output
        elif isinstance(result, list) and len(result) > 0:
            # If it's a list, return the last item
            return result[-1]
        else:
            # If the structure is unexpected, return an error message
            return json.dumps({"status": "error", "message": "Unexpected result structure from research task."})
