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
            allow_delegation=False
        )

    @staticmethod
    def get_DD_agent(gdrive_tools):
        """Agent 2: Creates Detailed Design (DD) from High-Level Design (HLD)."""
        return Agent(
            role="Detailed Design Specialist",
            goal=("Read the HLD, author a precise Detailed Design in the same Drive folder."),
            backstory=(
                "A senior technical lead. You translate HLDs into detailed design documents. "
                "You use strict JSON outputs and verify every created artifact."
            ),
            tools=gdrive_tools,
            verbose=True,
            allow_delegation=False
        )
    
    @staticmethod
    def get_CodeStructure_agent(tools):
        """Agent 3: Translates DD into a simple, pragmatic repo/file structure."""
        return Agent(
            role="Code Structure Architect",
            goal=(
                "Translate the Detailed Design into a simple, pragmatic repository/file structure with minimal complexity, "
                "without writing code. For each file, define a clear purpose."
            ),
            backstory=(
                "A pragmatic architect who prefers simple, effective structures. You never miss essential components, "
                "avoid over-engineering, and output strict JSON only."
            ),
            tools=(tools or []),
            verbose=True,
            allow_delegation=False
        )

    @staticmethod
    def get_Planning_agent(atlassian_tools):
        """Agent 4: Plans delivery steps and creates Jira artifacts from the code structure."""
        return Agent(
            role="Delivery Planner & Jira Project Organizer",
            goal=(
                "From a code structure, produce a concise, ordered implementation plan and create corresponding Jira "
                "Epics and Stories that a developer can follow."
            ),
            backstory=(
                "An experienced delivery manager and technical PM who sequences work logically. "
                "You create clean Jira backlogs aligned to a simple code structure."
            ),
            tools=atlassian_tools,
            verbose=True,
            allow_delegation=False
        )

    @staticmethod
    def get_Implementation_agent(tools):
        """Agent 5: Implements the repository and code in GitHub based on the plan and Jira keys."""
        return Agent(
            role="Repository Implementer & GitHub Builder",
            goal=(
                "Using the code structure and implementation plan, create a GitHub repository, scaffold all files, "
                "and implement working code step-by-step, referencing Jira story keys in branches, commits, and PRs."
            ),
            backstory=(
                "A senior software engineer who follows a clear plan. You keep the repo simple, readable, and runnable. "
                "You create small, incremental commits aligned to Jira stories, open PRs, and merge when ready."
            ),
            tools=tools,
            verbose=True,
            allow_delegation=False
        )

