from core.crew_initializer import CrewInitializer 
from mcp import StdioServerParameters 
from crewai_tools import MCPServerAdapter 
import os 
import shutil 
from dotenv import load_dotenv 
load_dotenv() 
 
ATLASSIAN_SSE = "https://mcp.atlassian.com/v1/sse" 
GITHUB_PERSONAL_ACCESS_TOKEN = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN") 
 
def main(): 
    print("Starting AI Idea to Production workflow...") 
    
    # Define server parameters for each MCP server
    g_drive_params = StdioServerParameters( 
        command=r"C:\Users\USER\Desktop\AIdeaToProd\.venv\Scripts\python.exe", 
        args=[r"mcps\g_drive_mcp\server.py"], 
        env={"UV_PYTHON": "3.13", **os.environ}, 
        cwd=r"c:\Users\USER\Desktop\AIdeaToProd" 
    )
    
    atlassian_params = StdioServerParameters( 
        command="npx", 
        args=["-y", "mcp-remote", ATLASSIAN_SSE], 
    )
    
    github_params = StdioServerParameters( 
        command="docker", 
        args=[ 
            "run", 
            "-i", 
            "--rm", 
            "-e", "GITHUB_PERSONAL_ACCESS_TOKEN", 
            "ghcr.io/github/github-mcp-server", 
        ], 
        env={**os.environ, "GITHUB_PERSONAL_ACCESS_TOKEN": GITHUB_PERSONAL_ACCESS_TOKEN or ""}, 
    )
    
    # Use nested context managers to ensure proper cleanup
    with MCPServerAdapter(g_drive_params) as g_drive_tools, \
         MCPServerAdapter(atlassian_params) as atlassian_tools, \
         MCPServerAdapter(github_params) as github_tools:
        
        # Build a map of tools by capability/source
        tools_map = {
            "gdrive": list(g_drive_tools),
            "atlassian": list(atlassian_tools),
            "github": list(github_tools),
        }
        
        print("Available tools:", {k: [t.name for t in v] for k, v in tools_map.items()})
        
        # Initialize the crew 
        crew_initializer = CrewInitializer() 
        crew = crew_initializer.initialize_crew(tools_map) 
     
        # Run the crew 
        print("Running the crew...") 
        try:
            result = crew.kickoff()
        except KeyboardInterrupt:
            print("Interrupted, shutting down...")
            result = None

        print("Crew execution completed!")
        print(f"Result: {result}")

if __name__ == "__main__":
    main()