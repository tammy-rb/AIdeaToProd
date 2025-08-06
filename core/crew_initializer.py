from crewai import Crew
from factories.agents_factory import AgentFactory
from factories.tasks_factory import TasksFactory

class CrewInitializer:
    """Handles the initialization and setup of CrewAI crews"""
    
    def __init__(self):
        pass
    
    def initialize_crew(self, tools):
        """Initialize and configure the crew"""

        idea = "an application that helps users track their daily water intake and set hydration goals."
        app_name = "HydroTrack"

        HL_designer_agent = AgentFactory.get_high_level_designer(tools)
        HL_design_task = TasksFactory.get_hl_design_task(HL_designer_agent, idea, app_name)
        
        # Create a Crew instance with the designer agent and task
        crew = Crew(
            agents=[HL_designer_agent],
            tasks=[HL_design_task],
            verbose=True
        )
        
        return crew
