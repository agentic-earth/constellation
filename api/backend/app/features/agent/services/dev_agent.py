"""
DevAgent Class

The DevAgent class is designed to interact with GitHub repositories and
provide insights using the CrewAI framework. It allows users to fetch
basic information about a repository and perform analysis on it.

Key Responsibilities:
- Authenticate and interact with GitHub using a provided token.
- Extract and retrieve repository information from a given GitHub URL.
- Utilize CrewAI to analyze the retrieved repository data.

Methods:
- get_repo_info: Fetches basic information about a GitHub repository.
- analyze_repo_with_crewai: Analyzes repository information using CrewAI's GithubSearchTool.
- _extract_repo_name: Helper method to extract the repository name from a URL.

This class serves as a bridge between GitHub data and CrewAI's analytical
capabilities, enabling users to gain insights into GitHub repositories.
"""

from crewai import Agent
from crewai_tools import GithubSearchTool

from backend.app.features.core.services.pipeline_service import PipelineService
from backend.app.features.core.services.taxonomy_service import TaxonomyService

class DevAgent(Agent):
    def __init__(self, github_repo_url: str, pipeline_service: PipelineService = None, taxonomy_service: TaxonomyService = None):
        super().__init__(
            name="Developer",
            role='Code Developer',
            goal='Search and analyze the specified GitHub repository for relevant information',
            backstory='An expert in navigating and extracting insights from GitHub repositories',
            verbose=True,
            allow_delegation=False,

            github_repo_url=github_repo_url,
            github_tool = GithubSearchTool(
                github_repo=github_repo_url,
                content_types=['code'],
                gh_token='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'
            ),
            pipeline_service = pipeline_service,
            taxonomy_service = taxonomy_service
        )
