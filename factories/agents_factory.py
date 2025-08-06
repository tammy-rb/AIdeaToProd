
from crewai import Agent


class AgentFactory:
    """
    Factory for creating configured agents.
    """
    def __init__(self):
        pass
    @staticmethod
    def get_high_level_designer(tools) -> Agent:
        """
        Create a high-level design agent with Google Drive tools.
        
        Args:
            idea: The application idea to design
            app_name: Name of the application
            
        Returns:
            Configured Agent instance
        """
        
        return Agent(
            role="High-Level Design Architect and Google Drive Expert",
            goal="Create comprehensive high-level design documents from project ideas and save them to Google Drive",
            backstory=f"""
            I am an experienced system architect with expertise in:
            - Software architecture design
            - Technical documentation
            - Google Drive file management
            - Project planning and structure
            .
            """,
            tools=tools,
            verbose=True,
            allow_delegation=False
        )


