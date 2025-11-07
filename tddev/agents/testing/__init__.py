"""Testing Agent Module.

Implements automated testing as described in arXiv:2509.25297v2:
1. Deployment Verification: Launch app and verify it starts correctly
2. User Simulation: Execute test cases using BrowserUse
3. Feedback Construction: Generate detailed feedback for refinement

Integrates with BrowserUse (69.7k GitHub stars) for browser automation.
"""

from .agent import TestingAgent

__all__ = ["TestingAgent"]
