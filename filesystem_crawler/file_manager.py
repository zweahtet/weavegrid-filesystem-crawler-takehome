"""
This module implements file system operations with security checks to ensure
all paths remain inside the specified root directory.
"""

import os
import pwd
import shutil
from pathlib import Path
from typing import List
from . import models


class FileSystemError(Exception):
    """Custom exception for file system operations."""
    pass

def is_subpath(child: Path, parent: Path) -> bool:
    """
    Check if 'child' is a subpath of 'parent'.
    """
    try:
        child.relative_to(parent)
        return True
    except ValueError:
        return False


def safe_path(root: Path, relative_path: str) -> Path:
    """
    Join the given relative path to the root directory safely.

    Raises:
        FileSystemError: if the resolved path is not under the root.
    """
    full_path = (root / relative_path).resolve()
    if not is_subpath(full_path, root):
        raise FileSystemError("Access outside the root directory is not allowed")
    return full_path


def get_file_info(path: Path) -> models.DirectoryEntry:
    """
    Return file or directory metadata including name, owner, size, permissions,
    and whether it is a directory.
    """
    stat = path.stat()
    try:
        owner = pwd.getpwuid(stat.st_uid).pw_name
    except KeyError:
        owner = str(stat.st_uid)
    permissions = oct(stat.st_mode & 0o777)
    return {
        "name": path.name,
        "owner": owner,
        "size": stat.st_size,
        "permissions": permissions,
        "is_directory": path.is_dir()
    }


def list_directory(root: Path, relative_path: str) -> List[models.DirectoryEntry]:
    """
    List all entries in a directory (including hidden files).

    Args:
        root: The root directory of allowed access.
        relative_path: The directory (relative to root) to list.

    Returns:
        A list of dictionaries containing metadata for each entry.

    Raises:
        FileSystemError: if the target path is not a directory.
    """
    full_path = safe_path(root, relative_path)
    if not full_path.is_dir():
        raise FileSystemError("Path is not a directory")
    items = [get_file_info(entry) for entry in full_path.iterdir()]
    return items


def read_file(root: Path, relative_path: str) -> str:
    """
    Read the content of a file.

    Args:
        root: The root directory of allowed access.
        relative_path: The file (relative to root) to read.

    Returns:
        The text content of the file.

    Raises:
        FileSystemError: if the target path is not a file.
    """
    full_path = safe_path(root, relative_path)
    if not full_path.is_file():
        raise FileSystemError("Path is not a file")
    with open(full_path, "r") as f:
        return f.read()


def create_file(root: Path, relative_path: str, content: str = "") -> None:
    """
    Create a new file with the provided content.

    Args:
        root: The root directory of allowed access.
        relative_path: The file (relative to root) to create.
        content: Text content to write to the file.

    Raises:
        FileSystemError: if the file already exists.
    """
    full_path = safe_path(root, relative_path)
    if full_path.exists():
        raise FileSystemError("File already exists")
    # Ensure the parent directory exists
    full_path.parent.mkdir(parents=True, exist_ok=True)
    with open(full_path, "w") as f:
        f.write(content)


def create_directory(root: Path, relative_path: str) -> None:
    """
    Create a new directory.

    Args:
        root: The root directory of allowed access.
        relative_path: The directory (relative to root) to create.

    Raises:
        FileSystemError: if the directory already exists.
    """
    full_path = safe_path(root, relative_path)
    if full_path.exists():
        raise FileSystemError("Directory already exists")
    full_path.mkdir(parents=True, exist_ok=False)


def update_file(root: Path, relative_path: str, content: str) -> None:
    """
    Replace the content of an existing file.

    Args:
        root: The root directory of allowed access.
        relative_path: The file (relative to root) to update.
        content: New content for the file.

    Raises:
        FileSystemError: if the target path is not a file.
    """
    full_path = safe_path(root, relative_path)
    if not full_path.is_file():
        raise FileSystemError("Path is not a file")
    with open(full_path, "w") as f:
        f.write(content)


def delete_path(root: Path, relative_path: str) -> None:
    """
    Delete a file or directory recursively.

    Args:
        root: The root directory of allowed access.
        relative_path: The file or directory (relative to root) to delete.

    Raises:
        FileSystemError: if the target path does not exist.
    """
    full_path = safe_path(root, relative_path)
    if not full_path.exists():
        raise FileSystemError("Path does not exist")
    if full_path.is_dir():
        shutil.rmtree(full_path)
    else:
        full_path.unlink()
