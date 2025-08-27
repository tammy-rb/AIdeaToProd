"""
Path configuration for the Analysis and Planning step.
Contains all file paths and directory structures specific to this domain.
"""

from pathlib import Path

# Base directory for this step (relative to project root)
_BASE_DIR = Path(__file__).parent.parent.parent.parent  # Go up to AIdeaToProd root
_WORKFLOW_STATE_DIR = _BASE_DIR / "workflow_state"

# Analysis and Planning step paths
ANALYSIS_PLANNING_DIR = _WORKFLOW_STATE_DIR / "analysis_and_planning"
ARTIFACTS_DIR = ANALYSIS_PLANNING_DIR / "artifacts"

# Artifact file paths (full paths)
HLD_FILE_PATH = str(ARTIFACTS_DIR / "HLD.md")
DETAILED_DESIGN_FILE_PATH = str(ARTIFACTS_DIR / "DD.md")
CODE_STRUCTURE_FILE_PATH = str(ARTIFACTS_DIR / "code_structure.json")

# Result file paths (full paths)
RESULT_FILE_PATH = str(ANALYSIS_PLANNING_DIR / "result.json")
METADATA_FILE_PATH = str(ANALYSIS_PLANNING_DIR / "metadata.json")

# FileWriterTool-compatible components
HLD_FILENAME = Path(HLD_FILE_PATH).name
HLD_DIRECTORY = str(Path(HLD_FILE_PATH).parent)

DETAILED_DESIGN_FILENAME = Path(DETAILED_DESIGN_FILE_PATH).name
DETAILED_DESIGN_DIRECTORY = str(Path(DETAILED_DESIGN_FILE_PATH).parent)

CODE_STRUCTURE_FILENAME = Path(CODE_STRUCTURE_FILE_PATH).name
CODE_STRUCTURE_DIRECTORY = str(Path(CODE_STRUCTURE_FILE_PATH).parent)

RESULT_FILENAME = Path(RESULT_FILE_PATH).name
RESULT_DIRECTORY = str(Path(RESULT_FILE_PATH).parent)


def ensure_directories():
    """
    Ensure all necessary directories for this step exist.
    """
    ANALYSIS_PLANNING_DIR.mkdir(parents=True, exist_ok=True)
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
