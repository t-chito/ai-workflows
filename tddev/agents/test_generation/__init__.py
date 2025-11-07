"""Test Generation Agent Module.

Implements multi-step test case generation as described in arXiv:2509.25297v2:
1. Requirement Decomposition: Parse high-level requirements into discrete items
2. Requirement Elaboration: Enrich requirements with detailed specifications
3. Test Case Generation: Generate soap-opera style test cases
"""

from .agent import TestGenerationAgent

__all__ = ["TestGenerationAgent"]
