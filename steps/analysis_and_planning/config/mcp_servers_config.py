"""
Configuration for MCP (Model Context Protocol) servers used in the analysis and planning step.
Separates concerns by isolating server connection parameters from business logic.
"""

import os
from mcp import StdioServerParameters
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Constants
ATLASSIAN_SSE = "https://mcp.atlassian.com/v1/sse"


class MCPServersConfig:
    """Configuration provider for MCP server parameters used in analysis and planning."""
    
    @staticmethod
    def get_google_drive_params() -> StdioServerParameters:
        """
        Get configuration parameters for Google Drive MCP server.
        
        Returns:
            StdioServerParameters for Google Drive MCP server
        """
        return StdioServerParameters(
            command=r"C:\Users\USER\Desktop\AIdeaToProd\.venv\Scripts\python.exe",
            args=[r"mcps\google_drive_mcp\server.py"],
            env={"UV_PYTHON": "3.13", **os.environ},
            cwd=r"c:\Users\USER\Desktop\AIdeaToProd"
        )
    
    @staticmethod
    def get_atlassian_params() -> StdioServerParameters:
        """
        Get configuration parameters for Atlassian MCP server.
        
        Returns:
            StdioServerParameters for Atlassian MCP server
        """
        return StdioServerParameters(
            command="npx",
            args=["-y", "mcp-remote", ATLASSIAN_SSE],
        )
    
    @staticmethod
    def get_all_server_params() -> dict:
        """
        Get all server parameters as a dictionary for analysis and planning step.
        
        Returns:
            Dictionary with server names as keys and their parameters as values
        """
        return {
            "google_drive": MCPServersConfig.get_google_drive_params(),
            "atlassian": MCPServersConfig.get_atlassian_params(),
        }
