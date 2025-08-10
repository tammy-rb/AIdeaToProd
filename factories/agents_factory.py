from crewai import Agent
from typing import List


class AgentsFactory:
    """
    Factory for creating configured agents.
    """

    def __init__(self):
        pass

    @staticmethod
    def get_hl_design_agent(google_drive_tools: List):
        """
        Create a high-level design agent with Google Drive tools.
        """
        return Agent(
            role="High-Level Design Architect",
            goal="Create comprehensive, structured high-level design documents and save them to Google Drive",
            backstory=(
                "You are an experienced software architect who translates ideas into clear high-level designs. "
                "You are careful about structure, naming, and reproducibility. You always return precise JSON with IDs."
            ),
            tools=google_drive_tools,
            verbose=True
        )

    @staticmethod
    def get_detailed_design_agent(gdrive_and_jira_tools: List):
        """
        Create a detailed design + project management agent with Google Drive and Jira tools.
        """
        return Agent(
            role="Detailed Design Specialist & Project Manager",
            goal=(
                "Read the HL design, create a detailed design doc, save it to the SAME Google Drive folder, "
                "then create a new Jira project for the app (if it doesn't exist) and populate it with issues "
                "based on the detailed design. Return the Jira project key and created issue keys."
            ),
            backstory=(
                "You are a senior technical lead who breaks high-level designs into detailed specs and drives "
                "execution by opening structured Jira work items. You ensure everything is stored neatly "
                "in Google Drive under the app's folder."
            ),
            tools=gdrive_and_jira_tools,
            verbose=True
        )

