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
            expected_output="Populated high-level design document in Google Drive about the idea provided"
        )