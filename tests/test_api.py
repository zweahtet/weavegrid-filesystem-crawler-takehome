import os
import pytest
from pathlib import Path
from fastapi.testclient import TestClient
from filesystem_crawler.main import app
from filesystem_crawler.config import settings

client = TestClient(app)


@pytest.fixture
def temp_root(tmp_path: Path):
    """
    Fixture that sets up a temporary file structure:
        - Creates files: 'file1' and 'file2'
        - Creates directory 'bar' with file 'file3' and an empty subdirectory 'baz'

    Also, overrides the ROOT_PATH in the application.
    """
    test_dir = tmp_path / "test_root"
    test_dir.mkdir()
    # Create files
    (test_dir / "file1").write_text("Content of file1")
    (test_dir / "file2").write_text("Content of file2")
    # Create a hidden file
    (test_dir / ".hidden_file").write_text("Hidden file content")
    # Create directory 'bar'
    bar_dir = test_dir / "bar"
    bar_dir.mkdir()
    (bar_dir / "file3").write_text("Content of file3")
    # Create empty subdirectory 'baz' inside 'bar'
    (bar_dir / "baz").mkdir()

    # Override ROOT_PATH in the app (monkeypatching the module-level variable)
    import filesystem_crawler.main as main_mod
    main_mod.ROOT_PATH = test_dir.resolve()
    return test_dir


def test_get_directory_listing(temp_root):
    """
    Test that the API returns a directory listing with hidden files.

    - Makes a GET request to the root directory
    - Asserts that the response status code is 200
    - Asserts that the response contains a list of directory entries
        - Asserts that the list contains the expected file and directory names
        - Asserts that the list contains the hidden file ".hidden_file"
    """
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    names = [item["name"] for item in data["contents"]]
    assert "file1" in names
    assert "file2" in names
    assert "bar" in names
    assert ".hidden_file" in names


def test_get_file_content(temp_root):
    """
    Test that the API returns file content correctly.

    - Makes a GET request to the '/file1' endpoint
    - Asserts that the response status code is 200
    - Asserts that the response contains a JSON object with 'type' and 'content' keys
    - Asserts that the 'type' key is 'file'
    - Asserts that the 'content' key is the content of the file 'file1'
    """
    response = client.get("/file1")
    assert response.status_code == 200
    data = response.json()
    assert data["type"] == "file"
    assert data["content"] == "Content of file1"


def test_create_file(temp_root):
    """
    Test that the API successfully creates a new file.

    - Makes a POST request to create a file with specified content
    - Asserts that the response status code is 201 (Created)
    - Asserts that the new file exists in the temporary root directory
    - Asserts that the content of the new file matches the specified content
    """
    
    new_file_path = "new_file"
    response = client.post(f"/{new_file_path}", json={"content": "New file content"})
    assert response.status_code == 201
    file_path = temp_root / new_file_path
    assert file_path.exists()
    assert file_path.read_text() == "New file content"


def test_create_directory(temp_root):
    """
    Test that the API successfully creates a new directory.

    - Makes a POST request to create a new directory
    - Asserts that the response status code is 201 (Created)
    - Asserts that the new directory exists in the temporary root directory
    - Asserts that the created path is a directory
    """
    new_dir_path = "new_dir/"
    response = client.post(f"/{new_dir_path}", json={})
    assert response.status_code == 201
    dir_path = temp_root / "new_dir"
    assert dir_path.exists()
    assert dir_path.is_dir()


def test_update_file(temp_root):
    """
    Test that the API successfully updates an existing file.

    - Makes a PUT request to update an existing file with new content
    - Asserts that the response status code is 200
    - Asserts that the content of the updated file matches the specified new content
    """
    
    response = client.put("/file1", json={"content": "Updated content"})
    assert response.status_code == 200
    file_path = temp_root / "file1"
    assert file_path.read_text() == "Updated content"


def test_delete_file(temp_root):
    """
    Test that the API successfully deletes an existing file.

    - Makes a DELETE request to delete an existing file
    - Asserts that the response status code is 200
    - Asserts that the deleted file no longer exists in the temporary root directory
    """
    response = client.delete("/file2")
    assert response.status_code == 200
    file_path = temp_root / "file2"
    assert not file_path.exists()


def test_delete_directory(temp_root):
    """
    Test that the API successfully deletes an existing directory.

    - Makes a DELETE request to delete an existing directory
    - Asserts that the response status code is 200
    - Asserts that the deleted directory no longer exists in the temporary root directory
    """
    response = client.delete("/bar")
    assert response.status_code == 200
    dir_path = temp_root / "bar"
    assert not dir_path.exists()


def test_access_outside_root(temp_root):
    # Attempt to access a path outside the ROOT_PATH should be rejected.
    """
    Test that the API prevents access to paths outside the ROOT_PATH.

    - Makes a GET request to a path that attempts to traverse outside the ROOT_PATH
    - Asserts that the response status code is 400
    """
    response = client.get("/%2E%2E/")
    assert response.status_code == 400
