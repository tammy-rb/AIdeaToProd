from crewai import Crew, Process
from factories.agents_factory import AgentsFactory
from factories.tasks_factory import TasksFactory

class CrewInitializer:
    """Handles the initialization and setup of CrewAI crews"""
    
    def __init__(self):
        pass
    
    def initialize_crew(self, tools):
        """Initialize and configure the crew"""

        idea = "an application that helps users track their daily water intake and set hydration goals."
        app_name = "HydroTrack"

        HL_designer_agent = AgentsFactory.get_hl_design_agent(tools)
        HL_design_task = TasksFactory.get_hl_design_task(HL_designer_agent, idea, app_name)
        
        detailed_design_agent = AgentsFactory.get_detailed_design_agent(tools)
        detailed_design_task = TasksFactory.get_detailed_design_task(detailed_design_agent, app_name)

        # Create a Crew instance with the designer agent and task
        crew = Crew(
            agents=[HL_designer_agent, detailed_design_agent],
            tasks=[HL_design_task, detailed_design_task],
            process=Process.sequential,  # or Process.parallel based on your needs
            verbose=True
        )
        
        return crew
