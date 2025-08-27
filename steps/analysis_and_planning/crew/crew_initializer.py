from crewai import Crew, Process, Agent, Task
from .factories.agents_factory import AgentsFactory
from .factories.tasks_factory import TasksFactory
from models import AppConfig

# Import the file saving tool and path management
from crewai_tools import FileWriterTool
from ..config.paths import ensure_directories

# Create an instance of the file writer tool
save_content_to_file = FileWriterTool()

class CrewInitializer:
    """Handles the initialization and setup of CrewAI crews"""
    
    def __init__(self):
        pass
    
    def initialize_crew(self, tools, app_config: AppConfig):
        """
        Initialize and configure the crew with a tools map and app configuration.
        
        Args:
            tools: Dictionary mapping tool categories to tool lists
            app_config: AppConfig object with workflow parameters (idea, app_name, jira_project_key)
        """
        # Ensure directories exist
        ensure_directories()
        
        # Extract values from the AppConfig object
        idea = app_config.idea
        app_name = app_config.app_name
        jira_project_key = app_config.jira_project_key

        # Get specific tool categories
        google_drive_tools = tools.get("google_drive", [])
        atlassian_tools = tools.get("atlassian", [])

        # Compose tool sets for each agent (centralized tool management)
        hld_tools = google_drive_tools + [save_content_to_file]
        dd_tools = google_drive_tools + [save_content_to_file]
        code_structure_tools = google_drive_tools + [save_content_to_file]
        planning_tools = atlassian_tools + [save_content_to_file]

        # Create agents with their specific tool sets
        HLD_agent = AgentsFactory.get_HLD_agent(hld_tools)
        HLD_task = TasksFactory.get_HLD_task(HLD_agent, idea, app_name)

        DD_agent = AgentsFactory.get_DD_agent(dd_tools)
        DD_only_task = TasksFactory.get_DD_only_task(DD_agent, app_name)

        CodeStructure_agent = AgentsFactory.get_CodeStructure_agent(code_structure_tools)
        CodeStructure_task = TasksFactory.get_CodeStructure_task(CodeStructure_agent, app_name)

        Planning_agent = AgentsFactory.get_Planning_agent(planning_tools)
        Planning_task = TasksFactory.get_Planning_Jira_task(Planning_agent, jira_project_key)

        # Create a Crew instance with the agents and tasks in strict order
        crew = Crew(
            agents=[HLD_agent, DD_agent, CodeStructure_agent, Planning_agent],
            tasks=[HLD_task, DD_only_task, CodeStructure_task, Planning_task],
            process=Process.sequential,
            verbose=True
        )
        
        return crew
