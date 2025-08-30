from crewai import Crew, Process
from .tools_manager import (
    get_hld_tools,
    get_dd_tools,
    get_code_structure_tools,
    get_planning_tools,
)
from .factories.agents_factory import AgentsFactory
from .factories.tasks_factory import TasksFactory

class CrewInitializer:
    def __init__(self):
        pass

    def initialize_crew(self, tools, app_config):
        idea = app_config.idea
        app_name = app_config.app_name
        jira_project_key = app_config.jira_project_key

        # Get agent-specific toolsets using the new functions
        hld_tools            = get_hld_tools(tools)
        dd_tools             = get_dd_tools(tools)
        code_structure_tools = get_code_structure_tools(tools)
        planning_tools       = get_planning_tools(tools)

        # Create agents and tasks
        HLD_agent = AgentsFactory.get_HLD_agent(hld_tools)
        HLD_task  = TasksFactory.get_HLD_task(HLD_agent, idea, app_name)

        DD_agent  = AgentsFactory.get_DD_agent(dd_tools)
        DD_task   = TasksFactory.get_DD_only_task(DD_agent, app_name)

        CodeStructure_agent = AgentsFactory.get_CodeStructure_agent(code_structure_tools)
        CodeStructure_task  = TasksFactory.get_CodeStructure_task(CodeStructure_agent, app_name)

        Planning_agent = AgentsFactory.get_Planning_agent(planning_tools)
        Planning_task  = TasksFactory.get_Planning_Jira_task(Planning_agent, jira_project_key)

        crew = Crew(
            agents=[HLD_agent, DD_agent, CodeStructure_agent, Planning_agent],
            tasks=[HLD_task, DD_task, CodeStructure_task, Planning_task],
            process=Process.sequential,
            verbose=True,
        )
        return crew