import os
import shutil
import uvicorn
from typing import Optional
from pathlib import Path
from fastapi import FastAPI, HTTPException, Body, status
from fastapi.responses import JSONResponse
from .config import settings
from . import file_manager
from . import models

ROOT_PATH = Path(settings.ROOT_DIR).resolve()

app = FastAPI(
    title="File System API",
    description="REST API for secure file system browsing and management",
    version="1.0.0",
)


def retrieve_item(file_path: str):
    """Retrieve directory contents or file contents."""
    try:
        full_path = file_manager.safe_path(ROOT_PATH, file_path)
        if file_path == "" or full_path.is_dir():
            items = file_manager.list_directory(ROOT_PATH, file_path)
            return {"path": file_path, "type": "directory", "contents": items}
        elif full_path.is_file():
            content = file_manager.read_file(ROOT_PATH, file_path)
            return {"path": file_path, "type": "file", "content": content}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Path does not exist"
            )
    except file_manager.FileSystemError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@app.get("/", summary="List files and directories in the root directory")
def get_root():
    """List the contents of the ROOT_DIR.

    Returns:
        JSONResponse: Directory metadata
    """

    return retrieve_item("")


@app.get("/{file_path:path}", summary="Retrieve file or directory information")
def get_path(file_path: str):
    """Retrieve directory contents or file contents.

    - For directories: Returns metadata about contained files/subdirectories
    - For files: Returns the text content of the file

    Args:
        path (str): Relative path from root directory (default: empty)

    Returns:
        JSONResponse: Directory metadata or file content

    Raises:
        HTTPException: 404 if the target path does not exist
    """
    return retrieve_item(file_path)


@app.post("/{file_path:path}", summary="Create a new file or directory")
def create_path(
    file_path: str, request: Optional[models.FileCreateRequest] = Body(default=None)
):
    """Creates a new file or directory.

    - Files: Path should NOT end with '/'
    - Directories: Path MUST end with '/'

    Args:
        file_path (str): Path to create relative to root
        request (models.FileCreateRequest): Content for file creation

    Returns:
        JSONResponse: Success message

    Raises:
        HTTPException: 409 if the target path already exists
    """
    try:
        if file_path.endswith("/"):
            # Create a directory
            file_manager.create_directory(ROOT_PATH, file_path)
            return JSONResponse(
                status_code=status.HTTP_201_CREATED,
                content={"message": "Directory created", "path": file_path},
            )
        else:
            # Create a file with optional content
            content = request.content if request.content is not None else ""
            file_manager.create_file(ROOT_PATH, file_path, content)
            return JSONResponse(
                status_code=status.HTTP_201_CREATED,
                content={"message": "File created", "path": file_path},
            )
    except file_manager.FileSystemError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@app.put("/{file_path:path}", summary="Update an existing file")
def update_file(file_path: str, request: models.FileUpdateRequest = Body(...)):
    """Replaces the content of an existing file. Only file updates are supported.

    Args:
        file_path (str): Path to update relative to root
        request (models.FileUpdateRequest): Content for file update

    Returns:
        JSONResponse: Success message

    Raises:
        HTTPException: 400 if the target path is not a file
    """
    try:
        file_manager.update_file(ROOT_PATH, file_path, request.content)
        return {"message": "File updated", "path": file_path}
    except file_manager.FileSystemError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/{file_path:path}", summary="Delete a file or directory")
def delete_path(file_path: str):
    """Deletes a file or directory. For directories, deletion is recursive.

    Args:
        file_path (str): Path to delete relative to root

    Returns:
        JSONResponse: Success message

    Raises:
        HTTPException: 400 if the target path does not exist
    """
    try:
        file_manager.delete_path(ROOT_PATH, file_path)
        return {"message": "Deleted successfully", "path": file_path}
    except file_manager.FileSystemError as e:
        raise HTTPException(status_code=400, detail=str(e))


# Setting host and port for application to run on
# if __name__ == "__main__":
# 	uvicorn.run(app, host="0.0.0.0", port=80)
