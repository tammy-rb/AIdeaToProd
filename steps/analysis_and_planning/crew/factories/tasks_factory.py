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
    def get_DD_only_task(agent, app_name: str):
        return Task(
            agent=agent,
            description=f"""
    Read the HLD and produce a Detailed Design (DD) in the SAME Google Drive folder. Return STRICT JSON ONLY.

    INPUTS:
    - app_name: "{app_name}"
    - Use the previous task's JSON to get: folder_id, hl_doc_id.

    GOOGLE DRIVE (DO EXACTLY):
    1) Read the HLD content from hl_doc_id.
    2) Create a file named "{app_name}_Detailed_Design.md" inside folder_id.
    3) Write a DD using these sections:
       - APP_META, Architecture & Environments, Data Model (Detailed),
         APIs/Contracts (Detailed), Workflows & Sequences,
         Security & Privacy Controls, Observability, Testing Strategy,
         Delivery Plan, Backlog Export (structure only, no Jira ops).
       - Be clear, unambiguous, implementation-agnostic. Keep it concise.
    4) Save the file and verify it is non-empty.

    OUTPUT (STRICT JSON ONLY):
    {{
      "detailed_doc_id": "<google_drive_file_id>",
      "detailed_doc_name": "{app_name}_Detailed_Design.md",
      "folder_id": "<pass_through_from_previous_task>"
    }}

    If any step fails, output STRICT JSON:
    {{"error":"<explanation>","partial":{{"detailed_doc_id":"?","folder_id":"<from_previous>"}}}}
    """,
            expected_output="STRICT JSON with detailed_doc_id, detailed_doc_name, folder_id (or error JSON).",
        )

    @staticmethod
    def get_CodeStructure_task(agent, app_name: str):
        return Task(
            agent=agent,
            description=f"""
    From the Detailed Design document, derive a simple, complete repository structure. Do NOT write code. Return STRICT JSON ONLY.

    INPUTS:
    - app_name: "{app_name}"
    - Use the previous task's JSON to get: detailed_doc_id and folder_id.

    GOOGLE DRIVE OPERATIONS:
    1) Read the Detailed Design document content from detailed_doc_id using Google Drive tools.
    2) Analyze the DD content to understand the system architecture, components, and requirements.
    3) Based on the DD content, derive the appropriate repository structure.

    THINKING AND OUTPUT RULES:
    - Prefer the simplest structure that fully supports the DD.
    - Include all essential files (README, config, main entrypoint, modules, simple layers).
    - For each file, provide a clear "purpose" description (no code).
    - Avoid over-engineering (keep folders shallow unless justified).
    - Do not invent dependencies that are not implied by the DD.
    - No prose outside JSON. STRICT JSON only.

    OUTPUT (STRICT JSON ONLY):
    {{
      "root": "{app_name}",
      "tree": "<ASCII_TREE_OF_DIRECTORIES_AND_FILES>",
      "files": [
        {{ "path": "README.md", "purpose": "<what this file explains/contains>" }},
        {{ "path": "src/main.py", "purpose": "<entrypoint responsibilities>" }}
        // add all files needed by the DD with simple structure
      ],
      "assumptions": [
        "<concise assumption if you had to choose a language/framework/etc>"
      ],
      "folder_id": "<pass_through_from_previous_task>"
    }}

    If any step fails, output STRICT JSON:
    {{"error":"<explanation>","partial":{{"root":"{app_name}","files":[],"folder_id":"<from_previous>"}}}}
    """,
            expected_output="STRICT JSON with root, tree, files[], assumptions[] (or error JSON).",
        )

    @staticmethod
    def get_Planning_Jira_task(agent, jira_project_key: str):
        return Task(
            agent=agent,
            description=f"""
    From a code structure JSON, produce an ordered implementation plan and create Jira Epics/Stories. Return STRICT JSON ONLY.

    INPUTS:
    - Use the previous task's JSON to get: code structure (root, tree, files[], assumptions[]) and folder_id.
    - Jira project key to use : "{jira_project_key}"

    PLANNING (OUTPUT AS LIST ITEMS, NO CODE):
    - Create a concise, numbered implementation_plan of concrete developer actions, e.g.:
      1. Create repo and root scaffolding.
      2. Add file src/main.py with CLI/HTTP entrypoint signature and argument parsing.
      3. Add module src/jokes/client.py that fetches jokes (no implementation).
      4. Wire simple configuration handling, logging, and basic error handling.
      ...
  - Keep steps short, specific, and in executable order. Do not include code.
  - Do NOT include any testing work (no unit/integration/e2e tests, no test scaffolding or test issues). Another agent will handle all tests.
  - If the code structure includes test files or testing sections, ignore them for planning and Jira creation.

  DOMAIN GUARDRAILS:
  - Keep the plan anchored to the jokes-by-city domain regardless of the app name.
  - Use neutral naming like "jokes API", "city model", "joke model", and avoid branding or app-name-specific terms.

   JIRA SITE & PROJECT (use Atlassian tools precisely; DO NOT use Google Drive IDs):
   1) Resolve the Jira site (cloud) first:
     - Call getAccessibleAtlassianResources and pick the Jira resource (type "jira" or websiteUrl ending with ".atlassian.net").
     - Capture: cloudId and websiteUrl/baseUrl for that site.
   2) List visible projects for that site:
     - Call getVisibleJiraProjects with the resolved site (pass websiteUrl/domain or cloudId exactly as the tool expects).
     - Validate that project key "{jira_project_key}" exists (case-insensitive compare).
     - If not found, STOP and return error JSON.
  3) Create EPICs that group the implementation_plan logically (exclude any testing scope).
  4) Under each EPIC, create STORIES with (exclude test-related stories):
       - Summary, short Description, Acceptance Criteria (GIVEN/WHEN/THEN),
         Story Points (1/2/3/5/8/13), Labels (use slugified root dir and component).
       - Link STORIES to parent EPIC.
  5) Validate by running JQL "project = {jira_project_key} ORDER BY created ASC" and collect created issue keys.

    OUTPUT (STRICT JSON ONLY):
    {{
      "code_structure": {{"root":"<as_input>","tree":"<as_input>","files":[{{...}}],"assumptions":[...] }},
      "google_drive_folder_id": "<folder_id_from_previous_tasks>"
    }}

    If any step fails, output STRICT JSON:
    {{"error":"<explanation>","partial":{{"code_structure":{{}},"google_drive_folder_id":"<from_previous>"}}}}
    """,
            expected_output=(
                "STRICT JSON with code_structure and google_drive_folder_id "
                "or error JSON with partial info."
            ),
        )

