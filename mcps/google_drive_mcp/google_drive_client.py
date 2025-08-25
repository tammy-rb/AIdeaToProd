"""
Google Drive Client

Handles all Google Drive authentication and file operations.
"""

import json
import os
import pathlib
import base64
from typing import Dict, List, Any, Optional

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from mcp.types import TextContent
from googleapiclient.http import MediaInMemoryUpload


# Configuration
KEYFILE_PATH = os.path.join(os.getcwd(), "mcps", "google_drive_mcp", "credentials", "gcp-oauth.keys.json")
GDRIVE_CREDENTIALS_PATH = os.path.join(os.getcwd(), "mcps", "google_drive_mcp", "credentials", ".gdrive-server-credentials.json")
DRIVE_SCOPES = ["https://www.googleapis.com/auth/drive"]
PORT = 8080


class GoogleDriveClient:
    """Google Drive client that handles authentication and file operations."""
    
    def __init__(self):
        self._drive_service = None
    
    def authenticate_and_save(self):
        """Authenticate and save credentials for Google Drive, or refresh if expired."""
        creds = None

        if os.path.exists(GDRIVE_CREDENTIALS_PATH):
            try:
                creds = Credentials.from_authorized_user_file(GDRIVE_CREDENTIALS_PATH, DRIVE_SCOPES)
            except Exception as e:
                print("Failed to load existing credentials:", e)
                creds = None

        if creds and creds.valid:
            print("Credentials are valid.")
            return creds

        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                with open(GDRIVE_CREDENTIALS_PATH, "w") as f:
                    f.write(creds.to_json())
                print("Access token refreshed.")
                return creds
            except Exception as e:
                print("Failed to refresh token:", e)
                creds = None

        # If no valid/refreshable credentials — do full login
        print("Launching login flow...")
        flow = InstalledAppFlow.from_client_secrets_file(KEYFILE_PATH, DRIVE_SCOPES)
        creds = flow.run_local_server(port=PORT)
        pathlib.Path(os.path.dirname(GDRIVE_CREDENTIALS_PATH)).mkdir(parents=True, exist_ok=True)
        with open(GDRIVE_CREDENTIALS_PATH, "w") as f:
            f.write(creds.to_json())
        print(f"New credentials saved to {GDRIVE_CREDENTIALS_PATH}")
        return creds

    def get_drive_service(self):
        """Get authenticated Google Drive service."""
        if self._drive_service is None:
            creds = self.authenticate_and_save()
            self._drive_service = build("drive", "v3", credentials=creds)
        return self._drive_service

    async def list_files(self, page_size: int = 10, cursor: Optional[str] = None, query: Optional[str] = None) -> List[TextContent]:
        """List files in Google Drive with optional filtering and pagination."""
        try:
            drive = self.get_drive_service()
            
            # Build query
            if not query:
                search_query = "trashed = false"
            else:
                search_query = f"name contains '{query}' and trashed = false"
            
            # Set up parameters
            params = {
                "pageSize": page_size,
                "fields": "nextPageToken, files(id, name, mimeType, size, createdTime, modifiedTime)",
                "q": search_query
            }
            
            if cursor:
                params["pageToken"] = cursor
                
            # Execute request
            resp = drive.files().list(**params).execute()
            files = resp.get("files", [])
            next_cursor = resp.get("nextPageToken")
            
            # Format response
            result = {
                "files": [
                    {
                        "id": f["id"],
                        "name": f["name"],
                        "mimeType": f["mimeType"],
                        "size": f.get("size", "N/A"),
                        "createdTime": f.get("createdTime", "N/A"),
                        "modifiedTime": f.get("modifiedTime", "N/A"),
                        "uri": f"gdrive:///{f['id']}"
                    }
                    for f in files
                ],
                "nextCursor": next_cursor,
                "totalFound": len(files)
            }
            
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error listing files: {str(e)}"
            )]

    async def read_file(self, file_id: str) -> List[TextContent]:
        """Read and return the content of a specific Google Drive file."""
        try:
            drive = self.get_drive_service()
            
            # Get file metadata
            meta = drive.files().get(fileId=file_id, fields="name,mimeType,size").execute()
            file_name = meta.get("name", "Unknown")
            mime_type = meta.get("mimeType", "")
            file_size = meta.get("size", "N/A")
            
            # Handle Google Workspace files (export)
            if mime_type.startswith("application/vnd.google-apps"):
                exports = {
                    "application/vnd.google-apps.document": "text/markdown",
                    "application/vnd.google-apps.spreadsheet": "text/csv", 
                    "application/vnd.google-apps.presentation": "text/plain",
                    "application/vnd.google-apps.drawing": "image/png",
                }
                
                export_type = exports.get(mime_type, "text/plain")
                content = drive.files().export(fileId=file_id, mimeType=export_type).execute()
                
                if export_type.startswith("text/"):
                    content_text = content.decode("utf-8")
                else:
                    content_text = base64.b64encode(content).decode("utf-8")
                    
            else:
                # Handle regular files
                content = drive.files().get_media(fileId=file_id).execute()
                
                if mime_type.startswith("text/") or mime_type == "application/json":
                    content_text = content.decode("utf-8")
                else:
                    # For binary files, return base64 encoded content
                    content_text = base64.b64encode(content).decode("utf-8")
            
            result = {
                "fileId": file_id,
                "fileName": file_name,
                "mimeType": mime_type,
                "size": file_size,
                "content": content_text
            }
            
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error reading file {file_id}: {str(e)}"
            )]

    async def search_files(self, query: str, page_size: int = 10) -> List[TextContent]:
        """Search for files in Google Drive by name or content."""
        try:
            drive = self.get_drive_service()
            
            # Build search query
            search_query = f"(name contains '{query}' or fullText contains '{query}') and trashed = false"
            
            params = {
                "pageSize": page_size,
                "fields": "files(id, name, mimeType, size, createdTime, modifiedTime)",
                "q": search_query
            }
            
            resp = drive.files().list(**params).execute()
            files = resp.get("files", [])
            
            result = {
                "query": query,
                "files": [
                    {
                        "id": f["id"],
                        "name": f["name"], 
                        "mimeType": f["mimeType"],
                        "size": f.get("size", "N/A"),
                        "createdTime": f.get("createdTime", "N/A"),
                        "modifiedTime": f.get("modifiedTime", "N/A"),
                        "uri": f"gdrive:///{f['id']}"
                    }
                    for f in files
                ],
                "totalFound": len(files)
            }
            
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error searching files: {str(e)}"
            )]

    async def get_recent_files(self, page_size: int = 20) -> Dict[str, Any]:
        """Get a list of recent files for resource listing."""
        try:
            drive = self.get_drive_service()
            resp = drive.files().list(
                pageSize=page_size,
                fields="files(id, name, mimeType)",
                q="trashed = false",
                orderBy="modifiedTime desc"
            ).execute()
            files = resp.get("files", [])
            
            return {
                "recent_files": [
                    {
                        "id": f["id"],
                        "name": f["name"],
                        "mimeType": f["mimeType"],
                        "uri": f"gdrive:///{f['id']}"
                    }
                    for f in files
                ]
            }
            
        except Exception as e:
            return {"error": f"Failed to list files: {str(e)}"}
        
    async def upload_file(self, file_name: str, content: str, mime_type: str, folder_id: Optional[str] = None) -> List[TextContent]:
        """Upload a file to Google Drive."""
        try:
            drive = self.get_drive_service()

            file_metadata = {
                "name": file_name
            }

            # If parent_id is provided, upload the file to that directory
            if folder_id:
                file_metadata["parents"] = [folder_id]

            media = MediaInMemoryUpload(
                body=content.encode("utf-8"),  # convert string to bytes
                mimetype=mime_type,
                resumable=False
            )

            uploaded_file = drive.files().create(
                body=file_metadata,
                media_body=media,
                fields="id, name, mimeType, createdTime"
            ).execute()

            result = {
                "status": "success",
                "uploaded": {
                    "id": uploaded_file["id"],
                    "name": uploaded_file["name"],
                    "mimeType": uploaded_file["mimeType"],
                    "createdTime": uploaded_file["createdTime"],
                    "uri": f"gdrive:///{uploaded_file['id']}"
                }
            }

            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]

        except Exception as e:
            return [TextContent(
                type="text",
                text=json.dumps({
                    "status": "error",
                    "error": str(e)
                }, indent=2)
            )]

    async def create_directory(self, folder_name: str, parent_id: Optional[str] = None) -> List[TextContent]:
        """Create a directory in Google Drive."""
        try:
            drive = self.get_drive_service()

            file_metadata = {
                "name": folder_name,
                "mimeType": "application/vnd.google-apps.folder"
            }

            # If parent_id is provided, create the folder inside that parent
            if parent_id:
                file_metadata["parents"] = [parent_id]

            created_folder = drive.files().create(
                body=file_metadata,
                fields="id, name, mimeType, createdTime, parents"
            ).execute()

            result = {
                "status": "success",
                "created": {
                    "id": created_folder["id"],
                    "name": created_folder["name"],
                    "mimeType": created_folder["mimeType"],
                    "createdTime": created_folder["createdTime"],
                    "parents": created_folder.get("parents", []),
                    "uri": f"gdrive:///{created_folder['id']}"
                }
            }

            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]

        except Exception as e:
            return [TextContent(
                type="text",
                text=json.dumps({
                    "status": "error",
                    "error": str(e)
                }, indent=2)
            )]

