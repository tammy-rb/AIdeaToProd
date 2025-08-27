"""
Type definitions for the analysis and planning step.
"""

from pydantic import BaseModel, Field


class AppConfig(BaseModel):
    """Application configuration data model for workflow steps."""
    
    idea: str = Field(..., description="The application idea description")
    app_name: str = Field(..., description="The name of the application")
    jira_project_key: str = Field(..., description="The Jira project key for task creation")

