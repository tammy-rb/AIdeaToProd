from pydantic import BaseModel, Field
from typing import Literal, Optional, List, Dict
from enum import Enum
from typing import Dict, Optional
from pydantic import BaseModel, Field

class ErrorCategory(str, Enum):
    CONFIG = "config"
    IO = "io"
    JSON = "json"
    VALIDATION = "validation"
    TOOL = "tool"
    UNKNOWN = "unknown"

class BuildError(BaseModel):
    origin: str                          # which node/stage raised it, e.g., "LoadBundle"
    category: ErrorCategory
    message: str
    retryable: bool = False
    context: Dict = Field(default_factory=dict)  # optional params (e.g., path)

class FileSpec(BaseModel):
    """Planned file in the repo, with path, purpose, and optional spec."""
    path: str
    purpose: str
    spec: Optional[str] = None  # what to implement
    status: Literal["pending", "done"] = "pending"

class WorkItem(BaseModel):
    """File queued for generation/commit."""
    path: str
    purpose: str
    spec: Optional[str] = None

class RepoRef(BaseModel):
    """GitHub repo reference and status."""
    owner: str
    name: str
    default_branch: str = "main"
    created: bool = False

class DesignState(BaseModel):
    """References and text for HLD/DD design docs."""
    dd_id: Optional[str] = None
    hld_id: Optional[str] = None

class CodeStructureState(BaseModel):
    """Desired repo structure from planning step."""
    root: str
    files: List[FileSpec]
    assumptions: List[str] = []

class BuildState(BaseModel):
    app_name: str
    repo: RepoRef
    design: DesignState
    derived_requirements: List[str] = []   # constraints/interfaces extracted from DD/HLD
    code_structure: CodeStructureState
    pending_files: List[WorkItem] = []     # queue of files waiting to be generated/committed
    completed_files: List[str] = []        # paths of files already committed
    assumptions: List[str] = []            # logged guesses when design info is missing
    essential_missing: List[WorkItem] = [] # critical files detected later (e.g. __init__.py)
    last_commit_sha: Optional[str] = None  # SHA of most recent commit
    errors: List[BuildError] = []           # structured errors captured from tool/MCP calls
    report: Dict = {}                      # final build summary after Finalize
