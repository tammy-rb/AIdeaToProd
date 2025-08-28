import json
import os
from typing import Any, Dict

class PlanningMetadataSaver:
    """
    Responsible for saving planning step results to metadata.json in a clean, decoupled way.
    """
    def __init__(self, metadata_path: str):
        self.metadata_path = metadata_path

    def extract_metadata(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extracts only relevant metadata sections from the planning result.
        """
        metadata = {
            "status": result.get("status"),
            "app_name": result.get("config", {}).get("app_name"),
            "jira_project_key": result.get("config", {}).get("jira_project_key"),
        }
        tasks = result.get("result", {}).get("tasks_output", [])
        if tasks and isinstance(tasks, list):
            if len(tasks) > 0:
                metadata["hld"] = getattr(tasks[0], "raw", None)
            if len(tasks) > 1:
                metadata["dd"] = getattr(tasks[1], "raw", None)
            if len(tasks) > 2:
                metadata["code_structure"] = getattr(tasks[2], "raw", None)
            if len(tasks) > 3:
                metadata["planning"] = getattr(tasks[3], "raw", None)
        return metadata

    def save(self, result: Dict[str, Any]):
        """
        Saves the extracted metadata to the configured file path.
        """
        metadata = self.extract_metadata(result)
        os.makedirs(os.path.dirname(self.metadata_path), exist_ok=True)
        with open(self.metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)
