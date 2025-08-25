"""
Pydantic models for Google Drive MCP Server.
"""

from typing import Optional
from pydantic import BaseModel


class ListFilesArgs(BaseModel):
    page_size: int = 10
    cursor: Optional[str] = None
    query: Optional[str] = None


class ReadFileArgs(BaseModel):
    file_id: str


class SearchFilesArgs(BaseModel):
    query: str
    page_size: int = 10


class UploadFileArgs(BaseModel):
    file_name: str
    content: str
    mime_type: str
    folder_id: Optional[str] = None


class CreateDirectoryArgs(BaseModel):
    folder_name: str
    parent_id: Optional[str] = None
