"""
Configuration for MCP (Model Context Protocol) servers used in the repository creation step.
Handles GitHub-related server connections for repository management.
"""

import os
from mcp import StdioServerParameters
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Constants
GITHUB_PERSONAL_ACCESS_TOKEN = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")


class GitHubMCPConfig:
    """Configuration provider for GitHub MCP server parameters."""
    
    @staticmethod
    def get_github_params() -> StdioServerParameters:
        """
        Get configuration parameters for GitHub MCP server.
        
        Returns:
            StdioServerParameters for GitHub MCP server
        """
        return StdioServerParameters(
            command="docker",
            args=[
                "run",
                "-i",
                "--rm",
                "-e", "GITHUB_PERSONAL_ACCESS_TOKEN",
                "ghcr.io/github/github-mcp-server",
            ],
            env={**os.environ, "GITHUB_PERSONAL_ACCESS_TOKEN": GITHUB_PERSONAL_ACCESS_TOKEN or ""},
        )
    
    @staticmethod
    def get_all_server_params() -> dict:
        """
        Get all server parameters as a dictionary for repository creation step.
        
        Returns:
            Dictionary with server names as keys and their parameters as values
        """
        return {
            "github": GitHubMCPConfig.get_github_params(),
        }
