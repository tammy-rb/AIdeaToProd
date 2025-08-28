"""
Planning step implementation for the AI Idea to Production pipeline.
Handles analysis and planning phase including HLD, DD, code structure, and Jira task creation.
"""

from typing import Dict, Any, Optional
from crewai_tools import MCPServerAdapter

from steps.step import Step
from steps.analysis_and_planning.crew.crew_initializer import CrewInitializer
from steps.analysis_and_planning.config import MCPServersConfig
from models import AppConfig

from steps.analysis_and_planning.utils.planning_metadata_saver import PlanningMetadataSaver
from types import SimpleNamespace as NS


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
    
    def execute(self, app_config: AppConfig) -> Dict[str, Any]:
        """
        Execute the planning step by running the analysis and planning crew.
        
        Args:
            app_config: AppConfig object containing idea, app_name, and jira_project_key
            
        Returns:
            Dictionary containing the crew execution result
            
        Raises:
            ValueError: If app_config is invalid
            Exception: If the crew execution fails
        """
        print(f"Starting {self.name} step...")
        
        if not app_config:
            print("Error: app_config is required")
            return {
                "status": "failed",
                "result": None,
                "config": None,
                "error": "app_config parameter is required"
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
                "config": app_config.model_dump(),
            }
            
        except KeyboardInterrupt:
            print("Planning step interrupted by user")
            return {
                "status": "interrupted",
                "result": None,
                "config": app_config.model_dump()
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
    # Example app configuration
    app_config = AppConfig(
        idea="an application that the user enter a word, and it returns the number of letters in that word",
        app_name="WordLengthChecker",
        jira_project_key="WOR"
    )
    
    planning_step = PlanningStep()
    result = planning_step.execute(app_config)
    print(f"Planning step result: {result}")
    saver = PlanningMetadataSaver(file_path="workflow_state/analysis_and_planning/result.json")
    saver.save(result)

if __name__ == "__main__":
    main()