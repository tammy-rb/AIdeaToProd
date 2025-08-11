from crewai import Agent, Task

class TasksFactory:
    @staticmethod
    
    def get_HLD_task(agent, idea: str, app_name: str):
        return Task(
            agent=agent,
            description=f"""
    You will create a Google Drive folder and a High-Level Design document, then return STRICT JSON.

    APP INPUT:
    - idea: "{idea}"
    - app_name: "{app_name}"

    GOOGLE DRIVE:
    1) Create a NEW folder named exactly "{app_name}". 
    - If a folder with that name already exists, create "{app_name} - {{timestamp}}".
    - Capture: folder_id, folder_name.
    2) Create a file named "{app_name}_HLD.md" inside that folder.
    3) Write a well-structured HLD using the provided template sections:
    - APP_META, Problem & Goals, Personas & Top User Stories,
        System Context, Major Components & Responsibilities,
        High-Level Data Model, Interfaces/APIs (High-Level), NFRs,
        Risks & Assumptions.
    - Ensure it is clear, concise, unambiguous, implementation-agnostic.
    4) Save file, verify it's non-empty.

    OUTPUT (STRICT JSON ONLY):
    {{
    "folder_id": "<google_drive_folder_id>",
    "folder_name": "<folder_name>",
    "hl_doc_id": "<google_drive_file_id>",
    "hl_doc_name": "{app_name}_HLD.md"
    }}

    If any step fails, output STRICT JSON:
    {{"error":"<explanation>","partial":{{"folder_id":"?","hl_doc_id":"?"}}}}
    """,
            expected_output="STRICT JSON with folder_id, folder_name, hl_doc_id, hl_doc_name (or error JSON)."
        )

    @staticmethod
    def get_DD_task(agent, app_name: str):
        return Task(
            agent=agent,
            description=f"""
    You will read the HLD, produce a Detailed Design in the SAME folder, and create Jira EPICs/STORIES.

    INPUTS:
    - app_name: "{app_name}"
    - Use the previous task's JSON to get: folder_id, hl_doc_id.

    GOOGLE DRIVE:
    1) Read the HLD content from hl_doc_id.
    2) Create a file named "{app_name}_Detailed_Design.md" in folder_id.
    3) Write a DD using the template sections:
    - APP_META, Architecture & Environments, Data Model (Detailed),
        APIs/Contracts (Detailed), Workflows & Sequences,
        Security & Privacy Controls, Observability, Testing Strategy,
        Delivery Plan, Backlog Export (for Jira).
    - Ensure every EPIC/STORY is Jira-expressible with AC and points.

    JIRA (existing project required):
    4) Find a Jira project named exactly "{app_name}". 
    - If multiple match, pick the one with most recent activity.
    - If none found, STOP and return error JSON (do NOT create project).
    5) Create EPICs per Backlog Export.
    6) Under each EPIC, create STORIES with:
    - Summary, Description (short), Acceptance Criteria (GIVEN/WHEN/THEN),
        Story Points (1/2/3/5/8/13), Labels (use slugified app_name and component).
    - Link STORIES to the parent EPIC.
    7) Optionally create TASKS/SUBTASKS if the DD called for them.
    8) Validate by running JQL "project = <KEY> ORDER BY created ASC" and collect created keys.

    OUTPUT (STRICT JSON ONLY):
    {{
    "detailed_doc_id": "<google_drive_file_id>",
    "detailed_doc_name": "{app_name}_Detailed_Design.md",
    "jira_project_key": "<KEY>",
    "epic_keys": ["<KEY-1>", "..."],
    "story_keys": ["<KEY-2>", "..."]
    }}

    If any step fails, output STRICT JSON:
    {{"error":"<explanation>","partial":{{"detailed_doc_id":"?","jira_project_key":"?","created_keys":[]}}}}
    """,
            expected_output=("STRICT JSON with detailed_doc_id, detailed_doc_name, jira_project_key, epic_keys, story_keys "
                            "or error JSON with partial info.")
        )