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

from steps.analysis_and_planning.planning_metadata_saver import PlanningMetadataSaver
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
                "config": app_config.model_dump() if hasattr(app_config, "model_dump") else (
                    app_config.dict() if hasattr(app_config, "dict") else dict(app_config)
                ),
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
    
    # Create AppConfig object - in real use this would come from the host agent
    app_config = AppConfig(
        idea="an application that the user enter a word, and it returns the number of letters in that word",
        app_name="WordLengthChecker",
        jira_project_key="WOR"
    )
    
    try:
        result = planning_step.execute(app_config)
        print(f"Planning step result: {result}")

        #Check result status
        if result["status"] == "success":
            print("✅ Planning completed successfully!")
            # Save metadata after successful planning
            metadata_path = "workflow_state/analysis_and_planning/result.json"
            saver = PlanningMetadataSaver(metadata_path)
            saver.save(result)
        elif result["status"] == "failed":
            print(f"❌ Planning failed: {result.get('error', 'Unknown error')}")
        elif result["status"] == "interrupted":
            print("⚠️ Planning was interrupted")
            
    except Exception as e:
        print(f"Planning step failed: {str(e)}")


def build_mock_result() -> dict:
    # Task: HLD
    hld_task = NS(
        description="Create HLD",
        name=None,
        expected_output="STRICT JSON with folder_id, folder_name, hl_doc_id, hl_doc_name",
        summary="",
        raw="""```
{
  "folder_id": "1uGT5a_iUzjyygPAu8BIwS4CqOnDT19_b",
  "folder_name": "WordLengthChecker",
  "hl_doc_id": "1GuhEmy3hGth0nDpLXY6lg_BMz029PZM5",
  "hl_doc_name": "WordLengthChecker_HLD.md"
}
```""",
        pydantic=None,
        json_dict=None,
        agent="High-Level Design Architect",
        output_format="raw",
    )

    # Task: Detailed Design
    dd_task = NS(
        description="Create DD",
        name=None,
        expected_output="STRICT JSON with detailed_doc_id, detailed_doc_name, folder_id",
        summary="",
        raw="""{
  "detailed_doc_id": "1i0Byt6l7ow3-hPihm7IavetnUjy8lABi",
  "detailed_doc_name": "WordLengthChecker_Detailed_Design.md",
  "folder_id": "1uGT5a_iUzjyygPAu8BIwS4CqOnDT19_b"
}""",
        pydantic=None,
        json_dict=None,
        agent="Detailed Design Specialist",
        output_format="raw",
    )

    # Task: Code Structure
    cs_task = NS(
        description="Derive repo structure",
        name=None,
        expected_output="STRICT JSON with app_name, root, tree, files[], assumptions[]",
        summary="",
        raw="""```
{
  "app_name": "WordLengthChecker",
  "root": "WordLengthChecker",
  "tree": "WordLengthChecker/\\n├── README.md\\n├── src/\\n│   ├── main.py\\n│   └── services/\\n│       ├── word_service.py\\n│       └── api_service.py\\n├── tests/\\n│   ├── test_word_service.py\\n│   └── test_api_service.py\\n└── requirements.txt",
  "files": [
    { "path": "README.md", "purpose": "Overview of the app and setup." },
    { "path": "src/main.py", "purpose": "Main entry point orchestrating flow." },
    { "path": "src/services/word_service.py", "purpose": "Word length logic." },
    { "path": "src/services/api_service.py", "purpose": "HTTP/API handling." },
    { "path": "tests/test_word_service.py", "purpose": "Unit tests for word logic." },
    { "path": "tests/test_api_service.py", "purpose": "Unit tests for API layer." },
    { "path": "requirements.txt", "purpose": "Python dependencies." }
  ],
  "assumptions": [
    "Python implementation with a simple REST layer."
  ]
}
```""",
        pydantic=None,
        json_dict=None,
        agent="Code Structure Architect",
        output_format="raw",
    )

    # Task: Jira / Delivery planner (keep it unfenced here, like your terminal sample)
    jira_task = NS(
        description="Implementation plan + Jira",
        name=None,
        expected_output="STRICT JSON with implementation_plan[], jira_project_key, counts",
        summary="",
        raw="""{
  "implementation_plan": [
    "1. Create repo and root scaffolding",
    "2. Add file src/main.py with CLI/HTTP entrypoint",
    "3. Implement word_service.py for processing word length calculations",
    "4. Implement api_service.py for handling API requests and responses",
    "5. Add tests in tests/test_word_service.py for word_service functionality",
    "6. Add tests in tests/test_api_service.py for api_service functionality",
    "7. Create requirements.txt listing all Python dependencies"
  ],
  "jira_project_key": "WOR",
  "epics_created_count": 1,
  "stories_created_count": 1
}""",
        pydantic=None,
        json_dict=None,
        agent="Delivery Planner & Jira Project Organizer",
        output_format="raw",
    )

    # Top-level CrewOutput-like object. The 'raw' here mirrors the terminal's
    # final summary block (optional; included for realism).
    crew_output = NS(
        raw="""{
  "implementation_plan": [
    "1. Create repo and root scaffolding",
    "2. Add file src/main.py with CLI/HTTP entrypoint",
    "3. Implement word_service.py for processing word length calculations",
    "4. Implement api_service.py for handling API requests and responses",
    "5. Add tests in tests/test_word_service.py for word_service functionality",
    "6. Add tests in tests/test_api_service.py for api_service functionality",
    "7. Create requirements.txt listing all Python dependencies"
  ],
  "jira_project_key": "WOR",
  "epics_created_count": 1,
  "stories_created_count": 1
}""",
        pydantic=None,
        json_dict=None,
        tasks_output=[hld_task, dd_task, cs_task, jira_task],
    )

    return {
        "status": "success",
        "result": crew_output,
        "config": {
            "idea": "an application that the user enter a word, and it returns the number of letters in that word",
            "app_name": "WordLengthChecker",
            "jira_project_key": "WOR",
        }
    }



if __name__ == "__main__":
    # ---- Use the mock instead of running the crew ----
    # result = planning_step.execute(app_config)
    # print(f"Planning step result: {result}")

    result = build_mock_result()
    print("Planning step result:", result)  # optional: see the structure

    # Now save using your robust saver (the fixed version you implemented earlier)
    saver = PlanningMetadataSaver(file_path="workflow_state/analysis_and_planning/result.json")
    saver.save(result)
    #main()