"""Pydantic models for request/response data validation and serialization."""
from typing import Optional
from pydantic import BaseModel, Field


class FileCreateRequest(BaseModel):
    """Request model for creating new files."""

    content: Optional[str] = Field(default="", description="Optional text content to write to the new file.")


class FileUpdateRequest(BaseModel):
    """Request model for updating existing files."""

    content: str = Field(..., description="New text content to replace existing file content.")


class DirectoryEntry(BaseModel):
    """Response model for directory entry metadata."""

    name: str = Field(..., description="Name of the file/directory")
    owner: str = Field(..., description="Owner username or UID")
    size: int = Field(..., description="Size in bytes")
    permissions: str = Field(..., description="Octal permission string")
    is_directory: bool = Field(..., description="True if entry is a directory")


class FileContentResponse(BaseModel):
    """Response model for file content requests."""

    content: str = Field(..., description="Text content of the file")
