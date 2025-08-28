# Workflow State MCP

This MCP (Model Context Protocol) server provides tools for saving and reading workflow state files for multi-agent app development processes. It is designed to support AI-driven workflows, enabling agents to persist and retrieve results of each step (such as HLD, DD, code structure, and planning results) in a structured and modular way.

## Features

- **Analysis and Planning Tools**: Save and read High-Level Design (HLD), Detailed Design (DD), code structure, and planning results.
- **Modular Design**: Tools are grouped by workflow section for extensibility (e.g., analysis_and_planning).
- **SOLID Principles**: Clean separation of concerns; file operations are delegated to utility modules.
- **Pydantic Models**: All saved content is validated and structured using Pydantic models.

## Usage

1. **Run the MCP server**:
   ```bash
   python server.py
   ```

2. **Available Tools (section: analysis_and_planning)**:
   - `save_HLD(content: str)`
   - `read_HLD()`
   - `save_DD(content: str)`
   - `read_DD()`
   - `save_code_structure(model_json: str)`
   - `read_code_structure()`
   - `save_result(model_json: str)`
   - `read_result()`

3. **File Storage**:
   - All files are saved under the `workflow_state` directory, organized by workflow section.

## Extending

To add new workflow sections (e.g., repository_creation), implement corresponding file tools and register them in the MCP server under a new section.

## Project Structure

```
mcps/
  workflow_state_mcp/
    server.py
    tools/
      analysis_and_planning/
        file_tools.py
        models.py
      file_utils.py
    workflow_state/
      analysis_and_planning/
        HLD.md
        DD.md
        code_structure.json
        result.json
```

## License

MIT License
