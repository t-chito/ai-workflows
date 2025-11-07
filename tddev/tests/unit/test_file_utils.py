"""Unit tests for FileManager utility."""

import tempfile
import pytest
from pathlib import Path
from tddev.utils.file_utils import FileManager


def test_file_manager_initialization():
    """Test FileManager initialization."""
    with tempfile.TemporaryDirectory() as tmpdir:
        fm = FileManager(tmpdir)
        assert fm.project_root.exists()
        assert fm.project_root.is_dir()


def test_write_and_read_file():
    """Test writing and reading files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        fm = FileManager(tmpdir)

        # Write file
        content = "Hello, TDDev!"
        file_path = Path("test.txt")
        fm.write_file(file_path, content)

        # Read file
        read_content = fm.read_file(file_path)
        assert read_content == content


def test_list_files():
    """Test listing files with exclusion patterns."""
    with tempfile.TemporaryDirectory() as tmpdir:
        fm = FileManager(tmpdir)

        # Create some files
        fm.write_file(Path("file1.txt"), "content1")
        fm.write_file(Path("file2.py"), "content2")
        fm.write_file(Path("node_modules/package.json"), "content3")

        # List files (should exclude node_modules)
        files = fm.list_files()
        file_names = [f.name for f in files]

        assert "file1.txt" in file_names
        assert "file2.py" in file_names
        assert "package.json" not in file_names  # excluded


def test_get_context_buffer():
    """Test context buffer generation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        fm = FileManager(tmpdir)

        # Create files
        fm.write_file(Path("app.py"), "print('hello')")
        fm.write_file(Path("config.yaml"), "setting: value")

        # Get context buffer
        files = [Path("app.py"), Path("config.yaml")]
        context = fm.get_context_buffer(files, include_line_numbers=True)

        assert "app.py" in context
        assert "config.yaml" in context
        assert "print('hello')" in context
        assert "setting: value" in context


def test_apply_file_action():
    """Test applying file actions."""
    with tempfile.TemporaryDirectory() as tmpdir:
        fm = FileManager(tmpdir)

        # Test write action
        action = {
            "type": "file",
            "filePath": "new_file.txt",
            "content": "New content"
        }
        fm.apply_file_action(action)

        assert (fm.project_root / "new_file.txt").exists()
        assert fm.read_file(Path("new_file.txt")) == "New content"

        # Test delete action
        delete_action = {
            "type": "delete",
            "filePath": "new_file.txt"
        }
        fm.apply_file_action(delete_action)

        assert not (fm.project_root / "new_file.txt").exists()


def test_get_file_tree():
    """Test file tree generation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        fm = FileManager(tmpdir)

        # Create directory structure
        fm.write_file(Path("src/main.py"), "content")
        fm.write_file(Path("src/utils.py"), "content")
        fm.write_file(Path("README.md"), "content")

        tree = fm.get_file_tree(max_depth=2)

        assert "src" in tree
        assert "main.py" in tree
        assert "README.md" in tree


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
