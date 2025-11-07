"""Development Agent Module.

Implements code generation and file management as described in arXiv:2509.25297v2:
1. Template Fetching: Select and initialize from 13 starter templates
2. Context Selection: Intelligently select relevant files for editing
3. File Editing: Generate and apply code changes

Forked from Bolt.diy with extensions for TDD workflow.
"""

from .agent import DevelopmentAgent

__all__ = ["DevelopmentAgent"]
