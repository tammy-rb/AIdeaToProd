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
