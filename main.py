from core.crew_initializer import CrewInitializer
from mcp import StdioServerParameters
from crewai_tools import MCPServerAdapter
import os

def main():
    print("Starting AI Idea to Production workflow...")
    
    server_params_list = [
        StdioServerParameters(
            command=r"C:\Users\USER\Desktop\AIdeaToProd\.venv\Scripts\python.exe",
            args=[r"mcps\g_drive_mcp\server.py"],
            env={"UV_PYTHON": "3.13", **os.environ},
            cwd=r"c:\Users\USER\Desktop\AIdeaToProd"
        ),
        StdioServerParameters(
            command="npx",
            args=[
                "@timbreeding/jira-mcp-server@latest",
                "--jira-base-url=https://rabinovitztami.atlassian.net",
                "--jira-username=rabinovitztami@gmail.com",
                "--jira-api-token=ATATT3xFfGF0K8PtcsfxM3IiOc_IKFKMOPxcpFb6eag4OyoVSdZi0hfsczwjsBEgfb1HMuKIQXLau4qEdZ1agZIgq1qGIDUv9-uVN1vkRRfGxTDOhPOaelu_fSF1VqBs73XL91eCYxWSMr41enH0yt2xt9_PjMRbYcNQpsh0MNfSjBgGI8C8D-c=F0C31AE9"
            ],
            env={
                "DEBUG": "true",
                "LOG_FILE_PATH": "",
                **os.environ
            }
        )
    ]

    with MCPServerAdapter(server_params_list) as tools:
        print([tool.name for tool in tools])
        # Initialize the crew
        crew_initializer = CrewInitializer()
        crew = crew_initializer.initialize_crew(tools)
        
        # Run the crew
        print("Running the crew...")
        result = crew.kickoff()
        
        print("Crew execution completed!")
        print(f"Result: {result}")

if __name__ == "__main__":
    main()
