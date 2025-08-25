from crewai import Crew, Process, Agent, Task
from .factories.agents_factory import AgentsFactory
from .factories.tasks_factory import TasksFactory
from steps.analysis_and_planning.models import AppConfig

class CrewInitializer:
    """Handles the initialization and setup of CrewAI crews"""
    
    def __init__(self):
        pass
    
    def initialize_crew(self, tools, app_config: AppConfig):
        """
        Initialize and configure the crew with a tools map and app configuration.
        
        Args:
            tools_map: Dictionary mapping tool categories to tool lists
            app_config: AppConfig object with workflow parameters (idea, app_name, jira_project_key)
        """
        # Extract values from the AppConfig object
        idea = app_config.idea
        app_name = app_config.app_name
        jira_project_key = app_config.jira_project_key

        # Select only the tools each agent needs
        google_drive_tools = tools.get("google_drive", [])
        atlassian_tools = tools.get("atlassian", [])

        # HLD uses only Google Drive
        HLD_agent = AgentsFactory.get_HLD_agent(google_drive_tools)
        HLD_task = TasksFactory.get_HLD_task(HLD_agent, idea, app_name)

        # DD-only uses Google Drive
        DD_agent = AgentsFactory.get_DD_agent(google_drive_tools)
        DD_only_task = TasksFactory.get_DD_only_task(DD_agent, app_name)

        # Code Structure agent (no external tools required)
        CodeStructure_agent = AgentsFactory.get_CodeStructure_agent(google_drive_tools)
        CodeStructure_task = TasksFactory.get_CodeStructure_task(CodeStructure_agent, app_name)

        # Planning/Jira agent uses Atlassian tools
        Planning_agent = AgentsFactory.get_Planning_agent(atlassian_tools)
        Planning_task = TasksFactory.get_Planning_Jira_task(Planning_agent, jira_project_key)

        # Create a Crew instance with the agents and tasks in strict order
        crew = Crew(
            agents=[HLD_agent, DD_agent, CodeStructure_agent, Planning_agent],
            tasks=[HLD_task, DD_only_task, CodeStructure_task, Planning_task],
            process=Process.sequential,
            verbose=True
        )
        
        return crew
