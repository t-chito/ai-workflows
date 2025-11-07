"""File management utilities for TDDev framework.

Handles file operations, context management, and project structure.
Based on arXiv:2509.25297v2 implementation.
"""

import os
import shutil
from pathlib import Path
from typing import List, Dict, Optional, Set
from loguru import logger
import fnmatch


class FileManager:
    """Manages file operations for web application development."""

    def __init__(self, project_root: str):
        """Initialize file manager.

        Args:
            project_root: Root directory of the project
        """
        self.project_root = Path(project_root)
        self.project_root.mkdir(parents=True, exist_ok=True)
        logger.info(f"Initialized FileManager at: {self.project_root}")

    def list_files(
        self,
        exclude_patterns: Optional[List[str]] = None
    ) -> List[Path]:
        """List all files in project, excluding specified patterns.

        Args:
            exclude_patterns: Glob patterns to exclude (e.g., "node_modules/**")

        Returns:
            List of file paths
        """
        if exclude_patterns is None:
            exclude_patterns = [
                "node_modules/**",
                "dist/**",
                "build/**",
                ".git/**",
                "*.log",
                "__pycache__/**",
                "*.pyc"
            ]

        all_files = []
        for path in self.project_root.rglob("*"):
            if path.is_file():
                # Check if file matches any exclude pattern
                relative_path = path.relative_to(self.project_root)
                excluded = False

                for pattern in exclude_patterns:
                    if fnmatch.fnmatch(str(relative_path), pattern):
                        excluded = True
                        break

                if not excluded:
                    all_files.append(path)

        logger.debug(f"Found {len(all_files)} files in project")
        return sorted(all_files)

    def read_file(self, file_path: Path) -> str:
        """Read file content.

        Args:
            file_path: Path to file (absolute or relative to project root)

        Returns:
            File content as string
        """
        if not file_path.is_absolute():
            file_path = self.project_root / file_path

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            logger.debug(f"Read file: {file_path}")
            return content
        except Exception as e:
            logger.error(f"Failed to read file {file_path}: {e}")
            raise

    def write_file(self, file_path: Path, content: str) -> None:
        """Write content to file.

        Args:
            file_path: Path to file (absolute or relative to project root)
            content: Content to write
        """
        if not file_path.is_absolute():
            file_path = self.project_root / file_path

        # Create parent directories
        file_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            logger.debug(f"Wrote file: {file_path}")
        except Exception as e:
            logger.error(f"Failed to write file {file_path}: {e}")
            raise

    def delete_file(self, file_path: Path) -> None:
        """Delete a file.

        Args:
            file_path: Path to file (absolute or relative to project root)
        """
        if not file_path.is_absolute():
            file_path = self.project_root / file_path

        try:
            if file_path.exists():
                file_path.unlink()
                logger.debug(f"Deleted file: {file_path}")
        except Exception as e:
            logger.error(f"Failed to delete file {file_path}: {e}")
            raise

    def copy_template(self, template_path: Path, dest_path: Optional[Path] = None) -> None:
        """Copy template to project directory.

        Args:
            template_path: Path to template directory
            dest_path: Destination path (default: project root)
        """
        if dest_path is None:
            dest_path = self.project_root

        if not dest_path.is_absolute():
            dest_path = self.project_root / dest_path

        try:
            if template_path.is_dir():
                shutil.copytree(template_path, dest_path, dirs_exist_ok=True)
                logger.info(f"Copied template from {template_path} to {dest_path}")
            else:
                raise ValueError(f"Template path is not a directory: {template_path}")
        except Exception as e:
            logger.error(f"Failed to copy template: {e}")
            raise

    def get_file_tree(self, max_depth: int = 3) -> str:
        """Get file tree representation.

        Args:
            max_depth: Maximum depth to traverse

        Returns:
            String representation of file tree
        """
        def build_tree(path: Path, prefix: str = "", depth: int = 0) -> List[str]:
            if depth > max_depth:
                return []

            items = sorted(path.iterdir(), key=lambda p: (not p.is_dir(), p.name))
            lines = []

            for i, item in enumerate(items):
                is_last = i == len(items) - 1
                current_prefix = "└── " if is_last else "├── "
                lines.append(f"{prefix}{current_prefix}{item.name}")

                if item.is_dir() and depth < max_depth:
                    extension = "    " if is_last else "│   "
                    lines.extend(build_tree(item, prefix + extension, depth + 1))

            return lines

        tree_lines = [str(self.project_root.name)]
        tree_lines.extend(build_tree(self.project_root))
        return "\n".join(tree_lines)

    def get_context_buffer(
        self,
        file_paths: List[Path],
        include_line_numbers: bool = True
    ) -> str:
        """Create context buffer with file contents.

        Args:
            file_paths: List of files to include
            include_line_numbers: Whether to add line numbers

        Returns:
            Formatted context buffer string
        """
        buffer_parts = []

        for file_path in file_paths:
            if not file_path.is_absolute():
                file_path = self.project_root / file_path

            relative_path = file_path.relative_to(self.project_root)
            content = self.read_file(file_path)

            # Format with line numbers if requested
            if include_line_numbers:
                lines = content.split("\n")
                numbered_lines = [
                    f"{i+1:4d} | {line}" for i, line in enumerate(lines)
                ]
                content = "\n".join(numbered_lines)

            # XML-like format as described in paper
            buffer_parts.append(
                f'<file filePath="{relative_path}">\n{content}\n</file>'
            )

        return "\n\n".join(buffer_parts)

    def apply_file_action(self, action: Dict) -> None:
        """Apply file action from LLM response.

        Args:
            action: Dict containing 'type', 'filePath', and 'content'
        """
        action_type = action.get("type")
        file_path = action.get("filePath")
        content = action.get("content", "")

        if not file_path:
            logger.warning("File action missing filePath")
            return

        file_path = Path(file_path)

        if action_type == "file":
            # Full file replacement
            self.write_file(file_path, content)
            logger.info(f"Applied file action: write {file_path}")

        elif action_type == "delete":
            # Delete file
            self.delete_file(file_path)
            logger.info(f"Applied file action: delete {file_path}")

        else:
            logger.warning(f"Unknown action type: {action_type}")

    def clean_project(self) -> None:
        """Clean build artifacts and temporary files."""
        patterns = [
            "node_modules",
            "dist",
            "build",
            ".next",
            "*.log"
        ]

        for pattern in patterns:
            for path in self.project_root.glob(f"**/{pattern}"):
                if path.is_dir():
                    shutil.rmtree(path)
                    logger.info(f"Removed directory: {path}")
                elif path.is_file():
                    path.unlink()
                    logger.info(f"Removed file: {path}")


# Example usage
if __name__ == "__main__":
    fm = FileManager("test_project")
    print(fm.get_file_tree())
