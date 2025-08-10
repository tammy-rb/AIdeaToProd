from crewai import Agent, Task

class TasksFactory:
    @staticmethod
    def get_hl_design_task(agent: Agent, idea: str, app_name: str) -> Task:
        """
        Task: Create HL design and save it to a new Google Drive folder named after the app.
        Returns JSON with folder and file IDs.
        """
        return Task(
            description=f"""
You will create a new Google Drive folder and an HL design document for the app, then return IDs as JSON.

APP INFO:
- Idea: "{idea}"
- App name: "{app_name}"

REQUIREMENTS:
1) In Google Drive, create a NEW folder named exactly "{app_name}" (if a folder with that name already exists, create "{app_name} - {{"{{timestamp}}"}}").
   - Capture: folder_id, folder_name.
2) Create a new text file named "{app_name}_HL_Design.txt" inside that folder.
3) Populate it with a well-structured High-Level Design covering at least:
   - Problem statement & goals
   - Core user stories / personas
   - System context & external dependencies
   - Major components & responsibilities
   - Data model (high level)
   - APIs / Interfaces (high level)
   - Non-functional requirements (security, privacy, performance, availability, observability)
   - Risks & assumptions
4) Ensure the document is saved and non-empty.

OUTPUT (STRICT JSON):
{{
  "folder_id": "<google_drive_folder_id>",
  "folder_name": "<folder_name>",
  "hl_doc_id": "<google_drive_file_id>",
  "hl_doc_name": "{app_name}_HL_Design.txt"
}}
""".strip(),
            agent=agent,
            expected_output="Strict JSON with folder_id, folder_name, hl_doc_id, hl_doc_name.",
        )

    @staticmethod
    def get_detailed_design_task(
        agent: Agent,
        app_name: str,
    ) -> Task:
        """
        Task: Read HL design, create detailed design doc in same Drive folder, create Jira project if needed,
              create issues per detailed design, and return JSON with Jira project key and issue keys.
        """
        return Task(
            description=f"""
You will read the HL design doc from Google Drive, produce a detailed design, save it to the SAME folder,
then create and populate a Jira project for "{app_name}".

INPUT IDS:
- Google Drive HL doc id: given from HL_designer_agent
- Google Drive folder id (for saving outputs): given from HL_designer_agent

GOOGLE DRIVE STEPS:
1) Read HL design from Google Drive using hl_doc_id.
2) Create a new text file named "{app_name}_Detailed_Design.txt" INSIDE the SAME folder (folder_id).
3) Write a comprehensive DETAILED DESIGN that includes:
   - Component-by-component specs (APIs, data contracts, error handling, edge cases)
   - Detailed data model (entities, fields, types, indexes, constraints)
   - Sequence diagrams (described in text) for key flows
   - Deployment architecture (environments, configuration, secrets handling)
   - Observability (logs, metrics, traces, dashboards)
   - Security & privacy controls (authN/Z, PII handling, data retention)
   - Testing strategy (unit, integration, e2e) and acceptance criteria
   - Delivery plan (milestones, iterations)
   Save the file and capture: detailed_doc_id, detailed_doc_name.

JIRA PROJECT CREATION:
4) find the project in jira with the key: HYD. it is named: HydroTrack.
in this project create the necessary issues based on the detailed design.

ISSUE CREATION FROM DETAILED DESIGN:
5) Parse the DETAILED DESIGN into a backlog:
   - EPICs for major workstreams (e.g., Backend, Web App, Mobile, Infra/SRE, Auth, Analytics).
   - Under each EPIC, create STORIES with clear acceptance criteria (GIVEN/WHEN/THEN) and story points.
   - Add TASKS or SUB-TASKS for implementation details where helpful.
6) Create all issues in the Jira project. Include fields:
   - Summary, Description (from detailed design), Acceptance Criteria, Story Points (reasonable estimates).
   - Link STORIES to their EPICs.
   - Collect all created keys in creation order.

VALIDATION:
7) If tools exist to query JQL, run "project = {{jira_project_key}} ORDER BY created ASC" to confirm issues exist.

OUTPUT (STRICT JSON):
{{
  "detailed_doc_id": "<google_drive_file_id>",
  "detailed_doc_name": "{app_name}_Detailed_Design.txt",
  "jira_project_key": "<KEY>",
  "created_issue_keys": ["<KEY-1>", "<KEY-2>", "..."]
}}

ERROR HANDLING:
- If blocked, return STRICT JSON with an "error" field and a human-readable explanation, and include any partial IDs you obtained.
""".strip(),
            agent=agent,
            expected_output=(
                "Strict JSON with detailed_doc_id, detailed_doc_name, jira_project_key, created_issue_keys "
                'or an "error" JSON with explanation and any partial IDs.'
            ),
        )