from pydantic import BaseModel
from typing import List, Optional, Dict, Any

# class HLDModel(BaseModel):
#     folder_id: str
#     folder_name: str
#     hl_doc_id: str
#     hl_doc_name: str
#     local_saved: bool

# class DDModel(BaseModel):
#     detailed_doc_id: str
#     detailed_doc_name: str
#     folder_id: str
#     local_saved: bool

class SaveFileModel(BaseModel):
    content: str

class CodeStructureFileModel(BaseModel):
    path: str
    purpose: str

class CodeStructureModel(BaseModel):
    app_name: str
    root: str
    tree: str
    files: List[CodeStructureFileModel]
    assumptions: List[str]
    local_saved: bool

class ResultModel(BaseModel):
    implementation_plan: List[str]
    jira_project_key: str
    epics_created_count: int
    stories_created_count: int
    local_saved: bool

# Optionally, add error models if you want to capture error outputs as well.
class ErrorModel(BaseModel):
    error: str
    partial: Dict[str, Any]
