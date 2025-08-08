from crewai import Agent


class AgentsFactory:
    """
    Factory for creating configured agents.
    """
    def __init__(self):
        pass
    @staticmethod
    def get_hl_design_agent(google_drive_tools):
        """
        Create a high-level design agent with Google Drive tools.
        
        Args:
            idea: The application idea to design
            app_name: Name of the application
            
        Returns:
            Configured Agent instance
        """
        
        return Agent(
            role="High-Level Design Architect",
            goal="Create comprehensive high-level design documents for software applications",
            backstory=f"""
            You are an experienced software architect who excels at translating 
            ideas into structured, high-level design documents. You understand system architecture, 
            user requirements, and technical feasibility.
            """,
            tools=google_drive_tools,
            verbose=True
        )
    
    @staticmethod
    def get_detailed_design_agent(tools):
        """
        Create a detailed design agent with Google Drive and Jira tools.
        
        Args:
            idea: The application idea to design
            app_name: Name of the application
            
        Returns:
            Configured Agent instance
        """
        
        return Agent(
            role="Detailed Design Specialist & Project Manager",
            goal="Transform high-level designs into detailed specifications and create actionable development tasks",
            backstory=f"""
            You are a senior technical lead who specializes in breaking down 
            high-level designs into detailed technical specifications and creating well-structured 
            development tasks. You have extensive experience with project management and understand 
            how to create clear, actionable work items for development teams.
            """,
            tools=tools,
            verbose=True
        )

