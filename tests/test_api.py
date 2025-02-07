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
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    names = [item["name"] for item in data["contents"]]
    assert "file1" in names
    assert "file2" in names
    assert "bar" in names
    assert ".hidden_file" in names


def test_get_file_content(temp_root):
    response = client.get("/file1")
    assert response.status_code == 200
    data = response.json()
    assert data["type"] == "file"
    assert data["content"] == "Content of file1"


def test_create_file(temp_root):
    new_file_path = "new_file"
    response = client.post(f"/{new_file_path}", json={"content": "New file content"})
    assert response.status_code == 201
    file_path = temp_root / new_file_path
    assert file_path.exists()
    assert file_path.read_text() == "New file content"


def test_create_directory(temp_root):
    new_dir_path = "new_dir/"
    response = client.post(f"/{new_dir_path}", json={})
    assert response.status_code == 201
    dir_path = temp_root / "new_dir"
    assert dir_path.exists()
    assert dir_path.is_dir()


def test_update_file(temp_root):
    response = client.put("/file1", json={"content": "Updated content"})
    assert response.status_code == 200
    file_path = temp_root / "file1"
    assert file_path.read_text() == "Updated content"


def test_delete_file(temp_root):
    response = client.delete("/file2")
    assert response.status_code == 200
    file_path = temp_root / "file2"
    assert not file_path.exists()


def test_delete_directory(temp_root):
    response = client.delete("/bar")
    assert response.status_code == 200
    dir_path = temp_root / "bar"
    assert not dir_path.exists()


def test_access_outside_root(temp_root):
    # Attempt to access a path outside the ROOT_PATH should be rejected.
    response = client.get("/%2E%2E/")
    assert response.status_code == 400
