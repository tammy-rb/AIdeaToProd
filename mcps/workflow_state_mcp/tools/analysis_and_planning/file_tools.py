import os
from ..file_utils import save_file, read_file
from .models import SaveFileModel, CodeStructureModel, ResultModel

ANALYSIS_AND_PLANNING_DIR = "analysis_and_planning"
HLD_FILENAME = "HLD.md"
DD_FILENAME = "DD.md"
CODE_STRUCTURE_FILENAME = "code_structure.json"
RESULT_FILENAME = "result.json"

def save_HLD(model: SaveFileModel):
    rel_path = os.path.join(ANALYSIS_AND_PLANNING_DIR, HLD_FILENAME)
    save_file(rel_path, model.content)

def read_HLD() -> str:
    rel_path = os.path.join(ANALYSIS_AND_PLANNING_DIR, HLD_FILENAME)
    return read_file(rel_path)

def save_DD(model: SaveFileModel):
    rel_path = os.path.join(ANALYSIS_AND_PLANNING_DIR, DD_FILENAME)
    save_file(rel_path, model.content)

def read_DD() -> str:
    rel_path = os.path.join(ANALYSIS_AND_PLANNING_DIR, DD_FILENAME)
    return read_file(rel_path)

def save_code_structure(model: CodeStructureModel):
    import json
    rel_path = os.path.join(ANALYSIS_AND_PLANNING_DIR, CODE_STRUCTURE_FILENAME)
    save_file(rel_path, model.json())

def read_code_structure() -> CodeStructureModel:
    import json
    rel_path = os.path.join(ANALYSIS_AND_PLANNING_DIR, CODE_STRUCTURE_FILENAME)
    data = read_file(rel_path)
    return CodeStructureModel.parse_raw(data)

def save_result(model: ResultModel):
    import json
    rel_path = os.path.join(ANALYSIS_AND_PLANNING_DIR, RESULT_FILENAME)
    save_file(rel_path, model.json())

def read_result() -> ResultModel:
    import json
    rel_path = os.path.join(ANALYSIS_AND_PLANNING_DIR, RESULT_FILENAME)
    data = read_file(rel_path)
    return ResultModel.parse_raw(data)
