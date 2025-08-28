from fastmcp import FastMCP
from pydantic import ValidationError
import json

from tools.analysis_and_planning import file_tools
from tools.analysis_and_planning.models import (
    SaveFileModel, CodeStructureModel, ResultModel
)

mcp = FastMCP("workflow-state-mcp")

# ------------- helpers -------------

def ok(**payload) -> str:
    return json.dumps({"status": "success", **payload})

def err(exc: Exception, **extra) -> str:
    if isinstance(exc, ValidationError):
        return json.dumps({
            "status": "error",
            "error": "validation_error",
            "details": getattr(exc, "errors", lambda: str(exc))()
        } | extra)
    return json.dumps({"status": "error", "error": str(exc), **extra})

def _load_model_json(ModelCls, raw_json: str):
    # Pydantic v2 / v1 compatibility
    if hasattr(ModelCls, "model_validate_json"):
        return ModelCls.model_validate_json(raw_json)  # v2
    return ModelCls.parse_raw(raw_json)               # v1

def _dump_model_json(model) -> str:
    if hasattr(model, "model_dump_json"):
        return model.model_dump_json(indent=2)        # v2
    return model.json(indent=2)                       # v1


# --- Analysis & Planning tools (namespaced via function name) ---

@mcp.tool()
def analysis_and_planning__save_HLD(content: str) -> str:
    """Save HLD content (markdown) to workflow state."""
    try:
        model = SaveFileModel(content=content)
        path = file_tools.save_HLD(model)
        return ok(path=path)
    except Exception as e:
        return err(e, tool="analysis_and_planning__save_HLD")

@mcp.tool()
def analysis_and_planning__read_HLD() -> str:
    """Read HLD content from workflow state."""
    try:
        content = file_tools.read_HLD()
        return ok(content=content)
    except Exception as e:
        return err(e, tool="analysis_and_planning__read_HLD")

@mcp.tool()
def analysis_and_planning__save_DD(content: str) -> str:
    """Save DD content (markdown) to workflow state."""
    try:
        model = SaveFileModel(content=content)
        path = file_tools.save_DD(model)
        return ok(path=path)
    except Exception as e:
        return err(e, tool="analysis_and_planning__save_DD")

@mcp.tool()
def analysis_and_planning__read_DD() -> str:
    """Read DD content from workflow state."""
    try:
        content = file_tools.read_DD()
        return ok(content=content)
    except Exception as e:
        return err(e, tool="analysis_and_planning__read_DD")

@mcp.tool()
def analysis_and_planning__save_code_structure(model_json: str) -> str:
    """Save code structure JSON to workflow state."""
    try:
        model = _load_model_json(CodeStructureModel, model_json)
        path = file_tools.save_code_structure(model)
        return ok(path=path)
    except Exception as e:
        return err(e, tool="analysis_and_planning__save_code_structure")

@mcp.tool()
def analysis_and_planning__read_code_structure() -> str:
    """Read code structure JSON from workflow state."""
    try:
        model = file_tools.read_code_structure()
        return ok(model_json=_dump_model_json(model))
    except Exception as e:
        return err(e, tool="analysis_and_planning__read_code_structure")

@mcp.tool()
def analysis_and_planning__save_result(model_json: str) -> str:
    """Save planning result JSON to workflow state."""
    try:
        model = _load_model_json(ResultModel, model_json)
        path = file_tools.save_result(model)
        return ok(path=path)
    except Exception as e:
        return err(e, tool="analysis_and_planning__save_result")

@mcp.tool()
def analysis_and_planning__read_result() -> str:
    """Read planning result JSON from workflow state."""
    try:
        model = file_tools.read_result()
        return ok(model_json=_dump_model_json(model))
    except Exception as e:
        return err(e, tool="analysis_and_planning__read_result")


if __name__ == "__main__":
    mcp.run()
