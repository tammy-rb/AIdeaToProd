from crewai import Agent
from typing import List


class AgentsFactory:
    """
    Factory for creating configured agents.
    """

    def __init__(self):
        pass

    @staticmethod
    def get_HLD_agent(google_drive_tools):
        return Agent(
            role="High-Level Design Architect",
            goal="Turn an app idea into an excellent, structured HLD and store it in Drive.",
            backstory=(
                "A seasoned software architect. You produce unambiguous HLDs with crisp structure. "
                "You are meticulous about naming, idempotency, and strict JSON outputs."
            ),
            tools=google_drive_tools,
            verbose=True,
            allow_delegation=False,
            constraints=[
                "Always return STRICT JSON exactly as specified.",
                "Never create duplicate folders/files: if name exists, suffix with ' - {timestamp}'.",
                "Documents must be non-empty and follow the given template."
            ]
        )

    @staticmethod
    def get_DD_agent(gdrive_and_jira_tools):
        return Agent(
            role="Detailed Design Specialist & Project Planner",
            goal=("Read the HLD, author a precise DD in the same Drive folder, then populate Jira "
                "with EPICs and STORIES and return created keys."),
            backstory=(
                "A senior technical lead. You translate HLDs into detailed specs and a pragmatic Jira plan. "
                "You use strict JSON outputs and verify every created artifact."
            ),
            tools=gdrive_and_jira_tools,
            verbose=True,
            allow_delegation=False,
            constraints=[
                "Do NOT create Jira projects; find the one named exactly as the app_name.",
                "If not found, fail with a helpful error JSON.",
                "Every STORY must include Acceptance Criteria (GIVEN/WHEN/THEN).",
                "Return STRICT JSON exactly as specified."
            ]
        )