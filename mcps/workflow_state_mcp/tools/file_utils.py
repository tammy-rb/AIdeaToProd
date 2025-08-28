import os

WORKFLOW_STATE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'workflow_state'))

def save_file(rel_path: str, content: str):
    abs_path = os.path.join(WORKFLOW_STATE_PATH, rel_path)
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)
    with open(abs_path, 'w', encoding='utf-8') as f:
        f.write(content)

def read_file(rel_path: str) -> str:
    abs_path = os.path.join(WORKFLOW_STATE_PATH, rel_path)
    with open(abs_path, 'r', encoding='utf-8') as f:
        return f.read()
