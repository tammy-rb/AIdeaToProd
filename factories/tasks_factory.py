from crewai import Task

class TasksFactory:
    @staticmethod
    def get_hl_design_task(agent, idea, app_name):
        return Task(
            description=f"""
            make an initial high-level design document for the idea: '{idea}', and save it to Google Drive.
            do it step by step:
            1. go to Google Drive and create a new folder named {app_name}.
            2. make a document with the name {app_name}_HL_Design.txt
            3. populate the document with a high-level design document about the idea provided.
            4. save the document in the folder {app_name} in Google Drive.
            5. make sure the document is not empty and contains a high-level design document.
            """,
            agent=agent,
            expected_output="the google drive id of the document created",
        )

    @staticmethod
    def get_detailed_design_task(agent, app_name):
        return Task(
            description=f"""
            Create a detailed design document based on the high-level design and create Jira work items.
            Do it step by step:
            1. Read the high-level design document from Google Drive using the ID provided by the high-level design task.
            2. Create a comprehensive detailed design document that breaks down each component, module, and feature
            3. Save the detailed design as {app_name}_Detailed_Design.txt in the same Google Drive folder
            4. Extract development tasks from the detailed design
            5. Create Jira work items for each development task in the project
            6. Ensure each Jira item has proper description, acceptance criteria, and story points
            """,
            agent=agent,
            expected_output="A summary containing the Google Drive document ID for the detailed design and a list of created Jira work item IDs",
        )