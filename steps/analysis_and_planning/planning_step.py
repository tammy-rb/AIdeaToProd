"""
Planning step implementation for the AI Idea to Production pipeline.
Handles analysis and planning phase including HLD, DD, code structure, and Jira task creation.
"""

from typing import Dict, Any, Optional
from crewai_tools import MCPServerAdapter

from steps.step import Step
from steps.analysis_and_planning.crew.crew_initializer import CrewInitializer
from steps.analysis_and_planning.config import MCPServersConfig
from steps.analysis_and_planning.models import AppConfig


class PlanningStep(Step):
    """
    Planning step that coordinates the analysis and planning crew.
    
    This step is responsible for:
    - Creating High-Level Design (HLD) documents
    - Creating Detailed Design (DD) documents
    - Generating code structure JSON
    - Creating Jira tasks for the project
    """
    
    def __init__(self):
        super().__init__(
            name="Analysis and Planning",
            description="Creates HLD, DD, code structure, and Jira tasks using AI agents"
        )
    
    def execute(self, input_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute the planning step by running the analysis and planning crew.
        
        Args:
            input_data: Required input containing idea, app_name, and jira_project_key
            
        Returns:
            Dictionary containing the crew execution result
            
        Raises:
            ValueError: If input data is invalid or missing
            Exception: If the crew execution fails
        """
        print(f"Starting {self.name} step...")
      
        # Parse input with Pydantic for type safety
        try:
            app_config = AppConfig(**input_data)
        except Exception as e:
            print(f"Error: Invalid input data - {e}")
            return {
                "status": "failed",
                "result": None,
                "config": input_data,
                "error": str(e)
            }
        
        try:
            # Execute the crew with MCP tools
            result = self._execute_crew_with_tools(app_config)
            
            # Store result
            self.set_result(result)
            
            print(f"{self.name} step completed successfully!")
            return {
                "status": "success",
                "result": result,
                "config": app_config.dict()
            }
            
        except KeyboardInterrupt:
            print("Planning step interrupted by user")
            return {
                "status": "interrupted",
                "result": None,
                "config": app_config.dict()
            }
        except Exception as e:
            print(f"Error in {self.name} step: {str(e)}")
            raise
    
    def _execute_crew_with_tools(self, app_config: AppConfig) -> Any:
        """
        Execute the crew with MCP tools.
        
        Args:
            app_config: AppConfig object containing idea, app_name, and jira_project_key
            
        Returns:
            Result from crew execution
        """
        # Get server parameters
        server_params = MCPServersConfig.get_all_server_params()
        
        # Use nested context managers to ensure proper cleanup
        with MCPServerAdapter(server_params["google_drive"]) as google_drive_tools, \
             MCPServerAdapter(server_params["atlassian"]) as atlassian_tools:
            
            # Build a map of tools by capability/source
            tools = {
                "google_drive": list(google_drive_tools),
                "atlassian": list(atlassian_tools),
            }
            
            print("Available tools:", {k: [t.name for t in v] for k, v in tools.items()})
            
            # Initialize and run the crew
            crew_initializer = CrewInitializer()
            crew = crew_initializer.initialize_crew(tools, app_config)
            
            print("Running the analysis and planning crew...")
            result = crew.kickoff()
            
            return result


def main():
    """
    Main entry point for running the planning step standalone.
    """
    planning_step = PlanningStep()
    
    # Example input data - in real use this would come from the host agent
    input_data = {
        "idea": "an application that the user enter a city, and it provides 10 jokes about that city",
        "app_name": "CityJokes",
        "jira_project_key": "CIT"
    }
    
    try:
        result = planning_step.execute(input_data)
        print(f"Planning step result: {result}")
        
        # Check result status
        if result["status"] == "success":
            print("✅ Planning completed successfully!")
        elif result["status"] == "failed":
            print(f"❌ Planning failed: {result.get('error', 'Unknown error')}")
        elif result["status"] == "interrupted":
            print("⚠️ Planning was interrupted")
            
    except Exception as e:
        print(f"Planning step failed: {str(e)}")


if __name__ == "__main__":
    main()