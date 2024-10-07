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

# from github import Github    
# import crewai  # Assuming crewai is a library you have access to
# from crewai_tools import GithubSearchTool

# class DevAgent:
#     def __init__(self, github_token):
#         # Initialize the DevAgent with a GitHub token for authentication
#         self.github = Github(github_token)

#     def get_repo_info(self, repo_url):
#         """
#         Fetch basic information about a GitHub repository.

#         Parameters:
#         - repo_url (str): The URL of the GitHub repository.

#         Returns:
#         - dict: A dictionary containing the repository's name, description,
#                 star count, fork count, and primary language.
#         """
#         # Extract the repository name and owner from the URL
#         repo_name = self._extract_repo_name(repo_url)
#         # Get the repository object using the GitHub API
#         repo = self.github.get_repo(repo_name)
        
#         # Collect basic information about the repository
#         repo_info = {
#             "name": repo.name,
#             "description": repo.description,
#             "stars": repo.stargazers_count,
#             "forks": repo.forks_count,
#             "language": repo.language,
#         }
        
#         return repo_info

#     def analyze_repo_with_crewai(self, repo_info):
#         """
#         Analyze the repository information using CrewAI's GithubSearchTool.

#         Parameters:
#         - repo_info (dict): A dictionary containing repository information.

#         Returns:
#         - Analysis result from CrewAI's GithubSearchTool.
#         """
#         # Initialize the GithubSearchTool with the repository URL
#         tool = GithubSearchTool(
#             github_repo=f"https://github.com/{repo_info['name']}",
#             content_types=['code', 'issue']  # Specify the content types to search
#         )

#         # Perform the search and analysis
#         analysis = tool.search()  # Assuming 'search' is the method to perform the analysis

#         return analysis

#     def _extract_repo_name(self, repo_url):
#         """
#         Extract the repository name from a given URL.

#         Parameters:
#         - repo_url (str): The URL of the GitHub repository.

#         Returns:
#         - str: The repository name in the format 'owner/repo'.
#         """
#         # Split the URL by '/' and extract the last two elements
#         parts = repo_url.rstrip('/').split('/')
#         if len(parts) < 2:
#             raise ValueError("Invalid GitHub repository URL")
        
#         # Return the owner and repo name
#         return f"{parts[-2]}/{parts[-1]}"

# def main():
#     # Replace 'your_github_token' with your actual GitHub token
#     github_token = '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'
#     # Replace 'your_repo_url' with the actual GitHub repository URL you want to test
#     repo_url = 'https://github.com/JustinXre2020/COVID-Data-Extractor'

#     # Initialize the DevAgent with the GitHub token
#     agent = DevAgent(github_token)

#     # Fetch repository information
#     try:
#         repo_info = agent.get_repo_info(repo_url)
#         print("Repository Information:")
#         print(repo_info)
#     except Exception as e:
#         print(f"Error fetching repository information: {e}")
#         return

#     # Analyze the repository using CrewAI
#     try:
#         analysis_result = agent.analyze_repo_with_crewai(repo_info)
#         print("Analysis Result:")
#         print(analysis_result)
#     except Exception as e:
#         print(f"Error analyzing repository: {e}")

# if __name__ == "__main__":
#     main()
import os
from crewai_tools import GithubSearchTool

class DevAgent:
    def __init__(self, github_repo=None, content_types=None, custom_config=None, gh_token=None):
        """
        Initialize the DevAgent with GitHub repository search capabilities.

        Parameters:
        - github_repo (str, optional): The URL of the GitHub repository to search.
        - content_types (list, optional): Types of content to search (e.g., ['code', 'issue']).
        - custom_config (dict, optional): Custom configuration for the GithubSearchTool.
        - gh_token (str, optional): GitHub token for authentication.
        """
        self.github_repo = github_repo
        self.content_types = content_types or ['code', 'issue', 'pr', 'repo']
        self.custom_config = custom_config
        self.gh_token = gh_token
        self.search_tool = self._initialize_search_tool()

    def _initialize_search_tool(self):
        """Initialize the GithubSearchTool with the provided parameters."""
        openai_api_key = os.environ.get("OPENAI_API_KEY")
        
        if not openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        
        tool_params = {
            "github_repo": self.github_repo,
            "content_types": self.content_types,
            "gh_token": self.gh_token,
            "openai_api_key": openai_api_key
        }
        if self.custom_config:
            tool_params['config'] = self.custom_config

        return GithubSearchTool(**tool_params)

    def search_repository(self, query):
        """
        Perform a semantic search within the GitHub repository.

        Parameters:
        - query (str): The search query to execute.

        Returns:
        - The search results from the GithubSearchTool.
        """
        return self.search_tool.search(query)

    def set_repository(self, github_repo):
        """
        Set or change the GitHub repository to search.

        Parameters:
        - github_repo (str): The URL of the GitHub repository.
        """
        self.github_repo = github_repo
        self.search_tool = self._initialize_search_tool()

    def update_content_types(self, content_types):
        """
        Update the content types to search.

        Parameters:
        - content_types (list): New list of content types to search.
        """
        self.content_types = content_types
        self.search_tool = self._initialize_search_tool()

    def set_custom_config(self, custom_config):
        """
        Set a custom configuration for the GithubSearchTool.

        Parameters:
        - custom_config (dict): Custom configuration dictionary.
        """
        self.custom_config = custom_config
        self.search_tool = self._initialize_search_tool()

if __name__ == "__main__":
    # Initialize DevAgent with a specific repository
    os.environ['OPENAI_API_KEY'] = 'sk-WCt96z3T6pan0cwlSVtv_X7hXqEdVP04VfbVNzGiJpT3BlbkFJ8vYD3dakbsZYU3w9hYOfZS_n35PEdDJDuYCQ92Q4gA'
    agent = DevAgent(
        github_repo='https://github.com/JustinXre2020/COVID-Data-Extractor',
        content_types=['code', 'issue'],
        gh_token='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'
    )

    # Perform a search
    results = agent.search_repository("Find all TODO comments in the code")

    # Perform another search with the new configuration
    results = agent.search_repository("Find performance optimization opportunities")
