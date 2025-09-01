from __future__ import annotations
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
import os, json
from pathlib import Path

from steps.repository_creation.models import (
    BuildState, RepoRef, DesignState, CodeStructureState, FileSpec
)
from steps.repository_creation.models import BuildError, ErrorCategory  # <- see module below

load_dotenv()


# ---------- helpers ----------
def _validate_incoming(b: Dict[str, Any]) -> None:
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

def _load_bundle_from_file() -> Dict[str, Any]:
    path = Path(os.getenv("ANALYSIS_AND_PLANNING_RESULT_JSON_PATH"))
    if not path.exists():
        raise FileNotFoundError(
            f"Bundle not found. Set ANALYSIS_AND_PLANNING_RESULT_JSON_PATH. Tried: {path}"
        )
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        # re-raise to be categorized in the error factory
        raise

def _make_error_state(e: Exception, *, origin: str = "LoadBundle") -> BuildState:
    """Centralized error → BuildState conversion (DRY)."""
    # classify
    if isinstance(e, FileNotFoundError):
        category = ErrorCategory.IO
        context = {"path": os.getenv("ANALYSIS_AND_PLANNING_RESULT_JSON_PATH")}
    elif isinstance(e, json.JSONDecodeError):
        category = ErrorCategory.JSON
        context = {}
    elif isinstance(e, ValueError):
        category = ErrorCategory.VALIDATION
        context = {}
    else:
        category = ErrorCategory.UNKNOWN
        context = {}

    base_owner = os.getenv("GITHUB_USERNAME", "UNKNOWN_OWNER")
    return BuildState(
        app_name="UNKNOWN_APP",
        repo=RepoRef(owner=base_owner, name="UNKNOWN_REPO"),
        design=DesignState(),
        code_structure=CodeStructureState(root=".", files=[]),
        errors=[BuildError(
            origin=origin,
            category=category,
            message=str(e),
            retryable=False,
            context=context
        )],
    )


# ---------- node ----------
def LoadBundle() -> BuildState:
    """FIRST NODE. Read the planning bundle, validate it, and return a NEW BuildState."""
    try:
        bundle = _load_bundle_from_file()
        _validate_incoming(bundle)

        app_name = bundle["app_name"]
        code_structure_input = bundle.get("code_structure", {})
        files_specs = _files_to_specs(code_structure_input.get("files", []))

        code_structure = CodeStructureState(
            root=code_structure_input.get("root", app_name),
            files=files_specs,
            assumptions=code_structure_input.get("assumptions", []),
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

        assumptions = list(code_structure.assumptions)
        impl_plan = (bundle.get("jira") or {}).get("implementation_plan")
        if impl_plan:
            assumptions.append(f"Jira plan items: {len(impl_plan)}")

        return BuildState(
            app_name=app_name,
            repo=repo,
            design=design,
            code_structure=code_structure,
            assumptions=assumptions,
        )
    except Exception as e:
        # single exit point for errors
        return _make_error_state(e, origin="LoadBundle")

# ---------- test runner ----------
if __name__ == "__main__":
    try:
        result_state = LoadBundle()
        # Print as dict/json for inspection
        if hasattr(result_state, "model_dump"):
            print(json.dumps(result_state.model_dump(), indent=2, ensure_ascii=False))
        else:
            print(result_state)
    except Exception as e:
        print(f"Error in BuildState node: {e}")