import os
from crewai import Agent, Task, Crew
from crewai_tools import GithubSearchTool

class DevAgent:
    def __init__(self, github_repo_url):
        self.github_repo_url = github_repo_url
        self.github_tool = self._create_github_tool()
        self.agent = self._create_agent()
        self.task = self._create_task()
        self.crew = self._create_crew()

    def _create_github_tool(self):
        return GithubSearchTool(
            github_repo=self.github_repo_url,
            content_types=['code'],
            gh_token='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'
        )

    def _create_agent(self):
        return Agent(
            role='GitHub Researcher',
            goal='Search and analyze the specified GitHub repository for relevant information',
            backstory='An expert in navigating and extracting insights from GitHub repositories',
            verbose=True,
            tools=[self.github_tool]
        )

    def _create_task(self):
        return Task(
            description=f'Search for information in the GitHub repository: {self.github_repo_url}. '
                        f'Focus on recent code changes, open issues, and pull requests. '
                        f'Provide a summary of the main features and any ongoing development work.',
            agent=self.agent,
            expected_output='A summary of the top 3 trending developments in the AI industry with a unique perspective on their significance.'
        )

    def _create_crew(self):
        return Crew(
            agents=[self.agent],
            tasks=[self.task]
        )

    def search(self):
        result = self.crew.kickoff()
        return result

# Usage example
if __name__ == "__main__":
    os.environ['OPENAI_API_KEY'] = 'sk-WCt96z3T6pan0cwlSVtv_X7hXqEdVP04VfbVNzGiJpT3BlbkFJ8vYD3dakbsZYU3w9hYOfZS_n35PEdDJDuYCQ92Q4gA'
    repo_url = 'https://github.com/crewAIInc/crewAI-tools'
    
    # Initialize DevAgent with a specific repository
    dev_agent = DevAgent(repo_url)
    result = dev_agent.search()
    print(result)