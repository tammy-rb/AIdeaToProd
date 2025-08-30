# make it as a function the build the BuildState before invoking the graph.
# after init the buildstate invoke the langgraph.
from __future__ import annotations
from typing import Dict, Any, List
import os
import json
from pathlib import Path

# from .models import BuildState, RepoRef, DesignState, CodeStructureState, FileSpec, ToolError

# ---- Config via env (override as needed) ----
# Option 1: Direct JSON string in env (for testing/pipe): BUNDLE_JSON
# Option 2: Path to a JSON file written by the planning step: RESULT_JSON_PATH
DEFAULT_RESULT_JSON_PATH = "workflow_state/analysis_and_planning/result.json"

def _validate_incoming(b: Dict[str, Any]) -> None:
    """Minimal validation: app_name + code_structure.files must exist."""
    if not isinstance(b, dict):
        raise ValueError("incoming bundle must be a dict")
    if not b.get("app_name"):
        raise ValueError("missing required field: app_name")
    cs = b.get("code_structure") or {}
    files = cs.get("files")
    if not isinstance(files, list) or not files:
        raise ValueError("missing or empty code_structure.files")

def _files_to_specs(files: List[Dict[str, Any]]) -> List[FileSpec]:
    return [
        FileSpec(
            path=f["path"],
            purpose=f.get("purpose", "No purpose provided"),
            spec=f.get("spec"),
            status="pending",
        )
        for f in files
    ]

def _load_bundle_from_env_or_file() -> Dict[str, Any]:
    """
    Private loader. Tries (in order):
      1) BUNDLE_JSON env containing the JSON payload
      2) RESULT_JSON_PATH env pointing to a JSON file (else DEFAULT_RESULT_JSON_PATH)
    """
    raw = os.getenv("BUNDLE_JSON")
    if raw:
        try:
            return json.loads(raw)
        except json.JSONDecodeError as e:
            raise ValueError(f"BUNDLE_JSON is not valid JSON: {e}") from e

    path = Path(os.getenv("RESULT_JSON_PATH", DEFAULT_RESULT_JSON_PATH))
    if not path.exists():
        raise FileNotFoundError(
            f"Bundle not found. Set BUNDLE_JSON or RESULT_JSON_PATH. Tried: {path}"
        )
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise ValueError(f"Bundle file contains invalid JSON: {e}") from e

def LoadBundle(state: BuildState) -> BuildState:
    """
    FIRST NODE. Read the planning bundle, validate it, and return a NEW BuildState.
    Node signature stays (state)->state for consistency with LangGraph.
    """
    try:
        bundle = _load_bundle_from_env_or_file()
        _validate_incoming(bundle)

        app_name = bundle["app_name"]
        cs_in = bundle.get("code_structure", {})
        files_specs = _files_to_specs(cs_in.get("files", []))

        code_structure = CodeStructureState(
            root=cs_in.get("root", app_name),
            files=files_specs,
            assumptions=cs_in.get("assumptions", []),
        )

        design = DesignState(
            dd_id=(bundle.get("dd") or {}).get("detailed_doc_id"),
            hld_id=(bundle.get("hld") or {}).get("hl_doc_id"),
        )

        repo = RepoRef(
            owner=os.getenv("GITHUB_USERNAME", "UNKNOWN_OWNER"),
            name=app_name,
            default_branch="main",
            created=False,
        )

        # Seed initial assumptions
        assumptions = list(code_structure.assumptions)
        impl_plan = (bundle.get("jira") or {}).get("implementation_plan")
        if impl_plan:
            assumptions.append(f"Jira plan items: {len(impl_plan)}")

        # Return a brand-new state (ignore incoming state because this is the first node)
        return BuildState(
            app_name=app_name,
            repo=repo,
            design=design,
            code_structure=code_structure,
            assumptions=assumptions,
        )

    except Exception as e:
        # If called as the very first node, we still respect the (state)->state pattern:
        # return a state that carries the error so downstream Finalize can report it.
        base_owner = os.getenv("GITHUB_USERNAME", "UNKNOWN_OWNER")
        return BuildState(
            app_name="UNKNOWN_APP",
            repo=RepoRef(owner=base_owner, name="UNKNOWN_REPO"),
            design=DesignState(),
            code_structure=CodeStructureState(root=".", files=[]),
            errors=[ToolError(tool="LoadBundle", params={}, message=str(e), retryable=False)],
        )
