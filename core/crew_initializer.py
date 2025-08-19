from crewai import Crew, Process, Agent, Task
from factories.agents_factory import AgentsFactory
from factories.tasks_factory import TasksFactory

class CrewInitializer:
    """Handles the initialization and setup of CrewAI crews"""
    
    def __init__(self):
        pass
    
    def initialize_crew(self, tools_map):
        """Initialize and configure the crew with a tools map (not a flat array)."""

        idea = "an application that the user enter a city, and it provides 10 jokes about that city"
        app_name = "CityJokes"
        jira_project_key = "CIT"

        # Select only the tools each agent needs
        gdrive_tools = tools_map.get("gdrive", [])
        atlassian_tools = tools_map.get("atlassian", [])
        github_tools = tools_map.get("github", [])

        # HLD uses only Google Drive
        HLD_agent = AgentsFactory.get_HLD_agent(gdrive_tools)
        HLD_task = TasksFactory.get_HLD_task(HLD_agent, idea, app_name)

        # DD-only uses Google Drive
        DD_agent = AgentsFactory.get_DD_agent(gdrive_tools)
        DD_only_task = TasksFactory.get_DD_only_task(DD_agent, app_name)

        # Code Structure agent (no external tools required)
        CodeStructure_agent = AgentsFactory.get_CodeStructure_agent([])
        CodeStructure_task = TasksFactory.get_CodeStructure_task(CodeStructure_agent, app_name)

        # Planning/Jira agent uses Atlassian tools
        Planning_agent = AgentsFactory.get_Planning_agent(atlassian_tools)
        Planning_task = TasksFactory.get_Planning_Jira_task(Planning_agent, jira_project_key)

        # Implementation agent uses GitHub tools to build the repo and code
        Implementation_agent = AgentsFactory.get_Implementation_agent(github_tools + atlassian_tools)
        Implementation_task = TasksFactory.get_Implementation_GitHub_task(
            Implementation_agent,
            app_name,
            jira_project_key
        )

        # Create a Crew instance with the agents and tasks in strict order
        crew = Crew(
            agents=[HLD_agent, DD_agent, CodeStructure_agent, Planning_agent, Implementation_agent],
            tasks=[HLD_task, DD_only_task, CodeStructure_task, Planning_task, Implementation_task],
            process=Process.sequential,
            verbose=True
        )
        
        return crew
