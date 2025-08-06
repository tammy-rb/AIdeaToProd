# Google Drive MCP Server

A comprehensive Model Context Protocol (MCP) server that provides AI assistants and other MCP clients with full access to Google Drive functionality.

## 🚀 Features

- **File Management**: List, read, upload, and organize files in Google Drive
- **Smart Search**: Search files by name and content across your entire Drive
- **Folder Organization**: Create and manage folder structures
- **Multiple File Types**: Support for text files, Google Workspace documents, and binary files
- **Pagination**: Handle large file collections efficiently
- **Recent Files**: Quick access to recently modified files

## 📋 Prerequisites

1. **Google Cloud Project** with Google Drive API enabled
2. **OAuth2 Credentials** - Download from Google Cloud Console
3. **Python 3.13+** 
4. **Virtual Environment** (recommended)

## 🛠️ Installation

1. **Clone or download this repository**
   ```bash
   cd google-drive-mcp-server
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # macOS/Linux  
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   uv sync
   # or
   pip install -r requirements.txt
   ```

4. **Set up Google Drive API credentials**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one
   - Enable the Google Drive API
   - Create OAuth 2.0 credentials (Desktop application)
   - Download the JSON file
   - Save it as `credentials/gcp-oauth.keys.json`

## 🔧 Configuration

The server will automatically guide you through OAuth authentication on first run. Your credentials will be saved for future use.

### Environment Variables (Optional)

Create a `.env` file for any custom configuration:
```env
GDRIVE_CREDENTIALS_PATH=./credentials/.gdrive-server-credentials.json
KEYFILE_PATH=./credentials/gcp-oauth.keys.json
```

## 🚀 Usage

### Running the Server

```bash
python server.py
```

The server runs using FastMCP and provides the following tools and resources.

## 📚 Available Tools

### 1. `list_drive_files`
List files in Google Drive with optional filtering and pagination.

**Parameters:**
- `page_size` (int, optional): Number of files to return (1-1000, default: 10)
- `cursor` (str, optional): Pagination token for next page
- `query` (str, optional): Filter files by name (case-insensitive)

**Example:**
```python
# List first 5 files
list_drive_files(page_size=5)

# Search for files containing "report"  
list_drive_files(query="report")

# Get next page of results
list_drive_files(cursor="previous_page_token_here")
```

### 2. `read_drive_file`
Read and return the content of a specific Google Drive file.

**Parameters:**
- `file_id` (str): Google Drive file ID (from list_drive_files or Drive URL)

**Supported File Types:**
- Text files (.txt, .md, .py): Returned as plain text
- Google Docs: Exported as Markdown
- Google Sheets: Exported as CSV  
- Google Slides: Exported as plain text
- JSON files: Returned as formatted JSON
- Binary files: Returned as base64-encoded strings

**Example:**
```python
read_drive_file("1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms")
```

### 3. `search_drive_files`
Search for files in Google Drive by name or content.

**Parameters:**
- `query` (str): Search term to look for in file names and content
- `page_size` (int, optional): Number of results to return (1-100, default: 10)

**Example:**
```python
# Find budget-related files
search_drive_files("budget")

# Search meeting notes with more results
search_drive_files("meeting notes", page_size=20)
```

### 4. `upload_drive_file`
Upload a file to Google Drive.

**Parameters:**
- `file_name` (str): Name for the file (include extension)
- `content` (str): File content (text or base64 for binary)
- `mime_type` (str): MIME type (e.g., "text/plain", "application/json")
- `folder_id` (str, optional): Parent folder ID (uploads to root if not specified)

**Common MIME Types:**
- `text/plain` - .txt files
- `text/markdown` - .md files
- `application/json` - .json files
- `text/x-python` - .py files
- `text/csv` - .csv files

**Example:**
```python
# Upload a text file to root
upload_drive_file("notes.txt", "Hello world", "text/plain")

# Upload to specific folder
upload_drive_file("data.json", '{"key": "value"}', "application/json", "folder_id_123")
```

### 5. `create_drive_directory`
Create a new folder in Google Drive.

**Parameters:**
- `folder_name` (str): Name for the new folder
- `parent_id` (str, optional): Parent folder ID (creates in root if not specified)

**Example:**
```python
# Create folder in root
create_drive_directory("My Projects")

# Create nested folder
create_drive_directory("Documentation", "parent_folder_id_123")
```

## 📁 Available Resources

### `gdrive://recent-files`
Provides access to the 20 most recently modified files in your Google Drive. Useful for quick access to files you've been working on.

## 🔍 File ID Reference

Google Drive file IDs are long alphanumeric strings that uniquely identify files. You can find them:

1. **From `list_drive_files` results** - Look for the `id` field
2. **From Google Drive URLs** - The part between `/d/` and `/edit`
   ```
   https://docs.google.com/document/d/FILE_ID_HERE/edit
   ```
3. **From search results** - The `id` field in search responses

## 🛡️ Security & Permissions

- The server only accesses files you have permission to view
- OAuth2 ensures secure authentication
- Credentials are stored locally and encrypted
- The server respects Google Drive sharing permissions

## 🐛 Troubleshooting

### Authentication Issues
- Ensure `credentials/gcp-oauth.keys.json` is properly configured
- Check that Google Drive API is enabled in your Google Cloud project
- Verify OAuth consent screen is configured

### File Access Issues  
- Confirm you have permission to access the file
- Check that the file hasn't been deleted or moved
- Verify the file ID is correct

### Large File Handling
- Files over 5MB may have slower response times
- Consider pagination for large file lists
- Binary files are base64-encoded which increases size

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📞 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review Google Drive API documentation
3. Create an issue in this repository