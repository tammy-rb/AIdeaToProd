from crewai import Crew, Process
from factories.agents_factory import AgentsFactory
from factories.tasks_factory import TasksFactory

class CrewInitializer:
    """Handles the initialization and setup of CrewAI crews"""
    
    def __init__(self):
        pass
    
    def initialize_crew(self, tools):
        """Initialize and configure the crew"""

        idea = "an application that the user enter a city, and it provides 10 jokes about that city"
        app_name = "CityJokes"

        HLD_agent = AgentsFactory.get_HLD_agent(tools)
        HLD_task = TasksFactory.get_HLD_task(HLD_agent, idea, app_name)

        DD_agent = AgentsFactory.get_DD_agent(tools)
        DD_task = TasksFactory.get_DD_task(DD_agent, app_name)

        # Create a Crew instance with the designer agent and task
        crew = Crew(
            agents=[HLD_agent, DD_agent],
            tasks=[HLD_task, DD_task],
            process=Process.sequential,  # or Process.parallel based on your needs
            verbose=True
        )
        
        return crew
