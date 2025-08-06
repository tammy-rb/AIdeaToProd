#!/usr/bin/env python3
"""
Google Drive MCP Server

A Model Context Protocol (MCP) server that provides comprehensive access to Google Drive files.
This server enables AI assistants and other MCP clients to interact with Google Drive by:

- Listing and browsing files with pagination and filtering
- Reading file contents (text files, Google Docs, Sheets, etc.)
- Searching files by name and content
- Uploading new files to Drive
- Creating folders for organization
- Accessing recently modified files

The server handles authentication via OAuth2 and supports various file types including:
- Plain text files (.txt, .md, .py, etc.)
- Google Workspace files (Docs exported as Markdown, Sheets as CSV)
- JSON and other structured data files
- Binary files (returned as base64-encoded content)

Setup Requirements:
1. Google Cloud Project with Drive API enabled
2. OAuth2 credentials (credentials/gcp-oauth.keys.json)
3. Python environment with required dependencies

Tools Available:
- list_drive_files: Browse files with optional filtering and pagination
- read_drive_file: Download and read file contents
- search_drive_files: Search files by name and content
- upload_drive_file: Create new files in Drive
- create_drive_directory: Create folders for organization

Resources Available:
- gdrive://recent-files: Access recently modified files

For detailed usage instructions and examples, see the individual tool documentation below.
"""

import asyncio
import json
import os
from typing import Dict, List, Any, Optional

from fastmcp import FastMCP
from pydantic import BaseModel
from dotenv import load_dotenv

from gdrive_client import GoogleDriveClient
from models import ListFilesArgs, ReadFileArgs, SearchFilesArgs, UploadFileArgs, CreateDirectoryArgs

load_dotenv()

# Initialize FastMCP server
mcp = FastMCP("gdrive-mcp")

# Initialize Google Drive client
drive_client = GoogleDriveClient()


@mcp.tool()
async def list_drive_files(
    page_size: int = 10,
    cursor: Optional[str] = None,
    query: Optional[str] = None
) -> str:
    """
    List files in Google Drive with optional filtering and pagination.
    
    This tool retrieves a list of files from your Google Drive, allowing you to browse
    and discover content. It supports pagination for handling large numbers of files
    and optional filtering by filename.
    
    Args:
        page_size (int, optional): The maximum number of files to return in a single request.
            Defaults to 10. Valid range is 1-1000. Smaller values are better for
            quick browsing, larger values for bulk operations.
            
        cursor (str, optional): A pagination token returned from a previous request.
            Use this to retrieve the next page of results. When None, starts from
            the beginning. This enables you to iterate through all files in chunks.
            
        query (str, optional): A search term to filter files by name. When provided,
            only files whose names contain this text will be returned. Case-insensitive.
            Example: "document" will match "My Document.pdf", "meeting_document.txt", etc.
    
    Returns:
        str: A JSON string containing the list of files with their metadata including:
            - id: Google Drive file ID (used for other operations)
            - name: Display name of the file
            - mimeType: File type (e.g., "text/plain", "application/pdf")
            - size: File size in bytes (if available)
            - createdTime: When the file was created
            - modifiedTime: When the file was last modified
            - uri: MCP resource URI for the file (gdrive:///file_id)
            - nextCursor: Token for retrieving the next page (if more files exist)
    
    Example usage:
        - List first 5 files: list_drive_files(page_size=5)
        - Search for documents: list_drive_files(query="report")
        - Get next page: list_drive_files(cursor="previous_page_token")
    """
    args = ListFilesArgs(page_size=page_size, cursor=cursor, query=query)
    result = await drive_client.list_files(args.page_size, args.cursor, args.query)
    return result[0].text if result else "No files found"


@mcp.tool()
async def read_drive_file(file_id: str) -> str:
    """
    Read and return the content of a specific Google Drive file.
    
    This tool downloads and returns the content of a file from Google Drive.
    It handles different file types appropriately:
    - Text files: Returns the actual text content
    - Google Workspace files (Docs, Sheets, etc.): Exports and returns in readable format
    - Binary files: Returns base64-encoded content
    
    Args:
        file_id (str): The unique Google Drive file identifier. This is the long
            alphanumeric string that identifies a specific file in Google Drive.
            You can get this from the list_drive_files tool or from a Google Drive
            URL (the part after /d/ and before /edit).
            Example: "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
    
    Returns:
        str: A JSON string containing the file content and metadata:
            - fileId: The Google Drive file ID that was requested
            - fileName: The display name of the file
            - mimeType: The file's MIME type
            - size: File size in bytes (if available)
            - content: The actual file content (text or base64-encoded for binary files)
    
    Supported file types:
        - Text files (.txt, .md, .py, etc.): Returned as plain text
        - Google Docs: Exported as Markdown
        - Google Sheets: Exported as CSV
        - Google Slides: Exported as plain text
        - JSON files: Returned as formatted JSON
        - Binary files: Returned as base64-encoded strings
    
    Example usage:
        - Read a text file: read_drive_file("1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms")
        - Read a Google Doc: read_drive_file("doc_file_id_here")
    """
    args = ReadFileArgs(file_id=file_id)
    result = await drive_client.read_file(args.file_id)
    return result[0].text if result else "File not found or empty"


@mcp.tool()
async def search_drive_files(query: str, page_size: int = 10) -> str:
    """
    Search for files in Google Drive by name or content.
    
    This tool performs a comprehensive search across your Google Drive files,
    looking for matches in both file names and file content (where supported).
    It's useful for finding specific documents when you remember keywords but
    not the exact location.
    
    Args:
        query (str): The search term to look for. This will be matched against:
            - File names (partial matches supported)
            - File content (for text-based files and Google Workspace documents)
            Examples: "budget", "meeting notes", "2024 report", "TODO"
            
        page_size (int, optional): The maximum number of search results to return.
            Defaults to 10. Range: 1-100. Use smaller values for quick searches,
            larger values when you need comprehensive results.
    
    Returns:
        str: A JSON string containing search results with:
            - query: The search term that was used
            - files: Array of matching files with metadata:
                * id: Google Drive file ID
                * name: File name
                * mimeType: File type
                * size: File size in bytes (if available)
                * createdTime: Creation timestamp
                * modifiedTime: Last modification timestamp
                * uri: MCP resource URI (gdrive:///file_id)
            - totalFound: Number of files found in this search
    
    Search capabilities:
        - File names: Searches for partial matches in file names
        - Content search: Searches inside text files, Google Docs, Sheets, etc.
        - Trash exclusion: Only searches non-deleted files
        - Case insensitive: Matches regardless of capitalization
    
    Example usage:
        - Find budget files: search_drive_files("budget")
        - Look for meeting notes: search_drive_files("meeting notes", page_size=20)
        - Search for code: search_drive_files("function main")
    """
    args = SearchFilesArgs(query=query, page_size=page_size)
    result = await drive_client.search_files(args.query, args.page_size)
    return result[0].text if result else "No files found"


@mcp.tool()
async def upload_drive_file(
    file_name: str,
    content: str,
    mime_type: str,
    folder_id: Optional[str] = None
) -> str:
    """
    Upload a file to Google Drive.
    
    This tool creates a new file in Google Drive with the specified content.
    You can upload to the root directory or to a specific folder, and the tool
    supports various file types through MIME type specification.
    
    Args:
        file_name (str): The name to give the file in Google Drive. Include the
            file extension to help with file type recognition.
            Examples: "report.txt", "data.json", "script.py", "notes.md"
            
        content (str): The content of the file to upload. For text files, this
            should be the actual text. For binary files, this should be base64-encoded
            content. Large files should be uploaded in chunks for better performance.
            
        mime_type (str): The MIME type that describes the file format. This helps
            Google Drive and other applications understand how to handle the file.
            Common examples:
            - "text/plain" for .txt files
            - "text/markdown" for .md files  
            - "application/json" for .json files
            - "text/x-python" for .py files
            - "text/csv" for .csv files
            - "application/pdf" for .pdf files
            
        folder_id (str, optional): The ID of the Google Drive folder where the file
            should be uploaded. If not provided, the file will be uploaded to the
            root directory of your Drive. You can get folder IDs from list_drive_files
            by looking for items with mimeType "application/vnd.google-apps.folder".
    
    Returns:
        str: A JSON string containing upload result information:
            - status: "success" or "error"
            - uploaded: (if successful) File metadata including:
                * id: The new file's Google Drive ID
                * name: The file name as stored in Drive
                * mimeType: The file's MIME type
                * createdTime: When the file was created
                * uri: MCP resource URI for the new file
            - error: (if failed) Error message describing what went wrong
    
    File size considerations:
        - Small files (< 5MB): Upload directly with this tool
        - Large files: Consider breaking into smaller chunks or using specialized upload tools
        
    Example usage:
        - Upload a text file: upload_drive_file("notes.txt", "Hello world", "text/plain")
        - Upload to folder: upload_drive_file("data.json", "{}", "application/json", "folder_id_123")
        - Upload Python script: upload_drive_file("script.py", "print('hello')", "text/x-python")
    """
    args = UploadFileArgs(
        file_name=file_name,
        content=content,
        mime_type=mime_type,
        folder_id=folder_id
    )
    result = await drive_client.upload_file(
        args.file_name, args.content, args.mime_type, args.folder_id
    )
    return result[0].text if result else "Upload failed"


@mcp.tool()
async def create_drive_directory(
    folder_name: str,
    parent_id: Optional[str] = None
) -> str:
    """
    Create a new directory/folder in Google Drive.
    
    This tool creates a new folder in Google Drive that can be used to organize
    your files. Folders can be created in the root directory or nested within
    existing folders to create a hierarchical structure.
    
    Args:
        folder_name (str): The name for the new folder. Folder names in Google Drive
            don't need to be unique (unlike file systems), so you can have multiple
            folders with the same name in different locations or even the same location.
            Examples: "Documents", "Project Files", "2024 Reports", "Backup"
            
        parent_id (str, optional): The ID of the parent folder where this new folder
            should be created. If not provided, the folder will be created in the
            root directory of your Google Drive. To create nested folders:
            1. Use list_drive_files to find folders (mimeType: "application/vnd.google-apps.folder")
            2. Use the folder's ID as the parent_id for the new folder
    
    Returns:
        str: A JSON string containing the creation result:
            - status: "success" or "error"
            - created: (if successful) Folder metadata including:
                * id: The new folder's Google Drive ID
                * name: The folder name as stored in Drive
                * mimeType: Always "application/vnd.google-apps.folder" for folders
                * createdTime: When the folder was created
                * parents: Array of parent folder IDs (empty array if in root)
                * uri: MCP resource URI for the new folder
            - error: (if failed) Error message describing what went wrong
    
    Folder organization tips:
        - Use descriptive names for better organization
        - Create a logical hierarchy (e.g., Year > Project > Documents)
        - Consider using date prefixes for time-based organization (e.g., "2024-01 January")
        
    Example usage:
        - Create root folder: create_drive_directory("My Projects")
        - Create nested folder: create_drive_directory("Documentation", "parent_folder_id_123")
        - Create dated folder: create_drive_directory("2024-08 August Reports")
    """
    args = CreateDirectoryArgs(folder_name=folder_name, parent_id=parent_id)
    result = await drive_client.create_directory(args.folder_name, args.parent_id)
    return result[0].text if result else "Directory creation failed"


@mcp.resource("gdrive://recent-files")
async def get_recent_files() -> str:
    """
    Access to Google Drive recent files.
    
    This resource provides a list of recently modified files from your Google Drive,
    making it easy to quickly access files you've been working on. This is particularly
    useful for finding files you were recently editing without having to search or
    browse through your entire Drive.
    
    The resource automatically excludes:
    - Files in the trash
    - Files you don't have access to
    - System files and hidden files
    
    Returns:
        str: A JSON string containing recent files information:
            - recent_files: Array of recently modified files with metadata:
                * id: Google Drive file ID
                * name: File display name
                * mimeType: File type identifier
                * uri: MCP resource URI (gdrive:///file_id)
    
    Files are ordered by modification time (most recent first) and limited to
    the 20 most recently modified files for performance.
    
    Usage in MCP clients:
        This resource can be accessed via the MCP resource URI: gdrive://recent-files
        Many MCP clients will automatically discover and list this resource.
    """
    result = await drive_client.get_recent_files()
    return json.dumps(result, indent=2)


if __name__ == "__main__":
    mcp.run()
