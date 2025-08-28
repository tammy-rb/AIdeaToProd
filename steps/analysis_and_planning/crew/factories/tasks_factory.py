from crewai import Agent, Task

class TasksFactory:

    @staticmethod
    def get_HLD_task(agent, idea: str, app_name: str):
        return Task(
            agent=agent,
            description=f"""
You will create a Google Drive folder and a High-Level Design (HLD) document. Return STRICT JSON only.

APP INPUT:
- idea: "{idea}"
- app_name: "{app_name}"

GOOGLE DRIVE (DO EXACTLY):
1) Create a NEW folder named exactly "{app_name}".
   - If a folder with that name already exists, create "{app_name} - {{timestamp}}".
   - Capture: folder_id, folder_name.
2) Create a file named "{app_name}_HLD.md" inside that folder.
3) Author a well-structured HLD with sections:
   - APP_META, Problem & Goals, Personas & Top User Stories,
     System Context, Major Components & Responsibilities,
     High-Level Data Model, Interfaces/APIs (High-Level), NFRs,
     Risks & Assumptions.
   - Clear, concise, unambiguous, implementation-agnostic.
4) Save the file to Google Drive and verify it's non-empty.

RULES:
- Output STRICT JSON only. No prose outside JSON.

OUTPUT (STRICT JSON ONLY):
{{
  "folder_id": "<google_drive_folder_id>",
  "folder_name": "<folder_name>",
  "hl_doc_id": "<google_drive_file_id>",
  "hl_doc_name": "{app_name}_HLD.md"
}}

ON FAILURE (STRICT JSON ONLY):
{{"error":"<explanation>","partial":{{"folder_id":"?","hl_doc_id":"?"}}}}
""",
            expected_output="STRICT JSON with folder_id, folder_name, hl_doc_id, hl_doc_name (or error JSON)."
        )

    @staticmethod
    def get_DD_only_task(agent, app_name: str):
        return Task(
            agent=agent,
            description=f"""
Read the HLD and produce a Detailed Design (DD) in the SAME Google Drive folder. Return STRICT JSON only.

INPUTS:
- app_name: "{app_name}"
- Use the previous task's JSON to get: folder_id, hl_doc_id.

GOOGLE DRIVE (DO EXACTLY):
1) Read the HLD content from hl_doc_id.
2) Create a file named "{app_name}_Detailed_Design.md" inside folder_id.
3) Author a DD with sections:
   - APP_META, Architecture & Environments, Data Model (Detailed),
     APIs/Contracts (Detailed), Workflows & Sequences,
     Security & Privacy Controls, Observability, Testing Strategy,
     Delivery Plan, Backlog Export (structure only).
   - Clear, unambiguous, concise. No code.
4) Save to Drive and verify non-empty.

RULES:
- Output STRICT JSON only. No prose outside JSON.

OUTPUT (STRICT JSON ONLY):
{{
  "detailed_doc_id": "<google_drive_file_id>",
  "detailed_doc_name": "{app_name}_Detailed_Design.md",
  "folder_id": "<pass_through_from_previous_task>"
}}

ON FAILURE (STRICT JSON ONLY):
{{"error":"<explanation>","partial":{{"detailed_doc_id":"?","folder_id":"<from_previous>"}}}}
""",
            expected_output="STRICT JSON with detailed_doc_id, detailed_doc_name, folder_id (or error JSON).",
        )

    @staticmethod
    def get_CodeStructure_task(agent, app_name: str):
        return Task(
            agent=agent,
            description=f"""
From the Detailed Design document, derive a simple, complete repository structure. **Do NOT write code.** Return STRICT JSON only.

INPUTS:
- app_name: "{app_name}"
- Use the previous task's JSON to get: detailed_doc_id and folder_id.

GOOGLE DRIVE OPERATIONS:
1) Read the Detailed Design content from detailed_doc_id.
2) Analyze DD to understand architecture, components, and requirements.
3) Based on DD, derive the repo structure.

THINKING & OUTPUT RULES:
- Prefer the simplest structure that fully supports the DD.
- Include essential files (README, config, main entrypoint, modules).
- For each file, provide a concise "purpose" (no code).
- Keep folders shallow unless justified. Do not invent dependencies.
- STRICT JSON only. No prose outside JSON.

OUTPUT (STRICT JSON ONLY):
{{
  "app_name": "{app_name}",
  "root": "{app_name}",
  "tree": "<ASCII_TREE_OF_DIRECTORIES_AND_FILES>",
  "files": [
    {{ "path": "README.md", "purpose": "<what this file explains/contains>" }},
    {{ "path": "src/main.py", "purpose": "<entrypoint responsibilities>" }}
    // add all files needed by the DD with simple structure
  ],
  "assumptions": [
    "<concise assumption if language/framework/etc was chosen>"
  ]
}}

ON FAILURE (STRICT JSON ONLY):
{{"error":"<explanation>","partial":{{"root":"{app_name}","files":[]}}}}
""",
            expected_output="STRICT JSON with app_name, root, tree, files[], assumptions[] (or error JSON).",
        )

    @staticmethod
    def get_Planning_Jira_task(agent, jira_project_key: str):
        return Task(
            agent=agent,
            description=f"""
From a code structure JSON, produce an ordered implementation plan and create Jira Epics/Stories. Return STRICT JSON only.

INPUTS:
- Use the previous task's JSON to get: code structure (root, tree, files[], assumptions[]).
- Jira project key: "{jira_project_key}"

PLANNING (OUTPUT AS LIST ITEMS, NO CODE):
- Create a concise, numbered implementation_plan of concrete developer actions.
- Keep steps short, specific, executable.
- ONLY include scope implied by the structure (no testing here).

JIRA SITE & PROJECT (use Atlassian tools precisely):
1) Resolve Jira site:
   - Call getAccessibleAtlassianResources; pick Jira resource (type "jira" or websiteUrl ending ".atlassian.net").
   - Capture: cloudId and websiteUrl/baseUrl.
2) List visible projects:
   - Call getVisibleJiraProjects with the resolved site.
   - Validate project key "{jira_project_key}" exists (case-insensitive).
   - If not found, STOP with error JSON.
3) Create EPICs grouping the implementation_plan logically (exclude testing scope).
4) Under each EPIC, create STORIES with concise Summary/Description/AC, points, labels; link to EPIC.
5) Validate with JQL "project = {jira_project_key} ORDER BY created ASC".

RULES:
- Output STRICT JSON only. No prose outside JSON.

OUTPUT (STRICT JSON ONLY):
{{
  "implementation_plan": [
    "1. Create repo and root scaffolding",
    "2. Add file src/main.py with CLI/HTTP entrypoint...",
    "..."
  ],
  "jira_project_key": "{jira_project_key}",
  "epics_created_count": <number_of_epics_created>,
  "stories_created_count": <number_of_stories_created>
}}

ON FAILURE (STRICT JSON ONLY):
{{"error":"<explanation>","partial":{{"implementation_plan":[],"jira_project_key":"{jira_project_key}","epics_created_count":0,"stories_created_count":0}}}}
""",
            expected_output=(
                "STRICT JSON with implementation_plan[], jira_project_key, epics_created_count, "
                "stories_created_count (or error JSON with partial info)."
            ),
        )
