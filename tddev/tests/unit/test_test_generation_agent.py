"""Unit tests for TestGenerationAgent."""

import json
import pytest
from unittest.mock import Mock, MagicMock
from tddev.agents.test_generation import TestGenerationAgent


@pytest.fixture
def mock_llm():
    """Create mock LLM client."""
    mock = Mock()
    return mock


def test_test_generation_agent_initialization(mock_llm):
    """Test TestGenerationAgent initialization."""
    agent = TestGenerationAgent(mock_llm)
    assert agent.llm == mock_llm
    assert agent.config == {}


def test_decompose_requirements(mock_llm):
    """Test requirement decomposition."""
    # Mock LLM response
    mock_requirements = [
        "Display list of todos",
        "Add new todos",
        "Mark todos as complete"
    ]
    mock_llm.chat.return_value = json.dumps(mock_requirements)

    agent = TestGenerationAgent(mock_llm)
    result = agent._decompose_requirements("Create a todo list app")

    assert len(result) == 3
    assert "Display list of todos" in result
    mock_llm.chat.assert_called_once()


def test_elaborate_requirements(mock_llm):
    """Test requirement elaboration."""
    # Mock LLM response
    mock_detailed_req = {
        "requirement": "Display list of todos",
        "functionality": "Show all todos in a list",
        "ui_design": {"layout": "vertical list", "components": ["TodoItem"]},
        "interactions": [],
        "data": {"type": "mock"},
        "dependencies": []
    }
    mock_llm.chat.return_value = json.dumps(mock_detailed_req)

    agent = TestGenerationAgent(mock_llm)
    high_level_reqs = ["Display list of todos"]

    result = agent._elaborate_requirements("Create todo app", high_level_reqs)

    assert len(result) == 1
    assert result[0]["requirement"] == "Display list of todos"


def test_generate_test_cases(mock_llm):
    """Test test case generation."""
    # Mock LLM response
    mock_test_case = {
        "test_id": "test_1",
        "requirement": "Display list of todos",
        "persona": {"name": "User", "goal": "View todos"},
        "steps": [
            {
                "step_number": 1,
                "description": "Navigate to app",
                "action": "open_url",
                "expected_result": "See todo list"
            }
        ],
        "validation": {"functionality": "Check todos visible"}
    }
    mock_llm.chat.return_value = json.dumps(mock_test_case)

    agent = TestGenerationAgent(mock_llm)
    detailed_reqs = [{"requirement": "Display list of todos"}]

    result = agent._generate_test_cases(detailed_reqs)

    assert len(result) == 1
    assert result[0]["test_id"] == "test_1"


def test_generate_tests_full_pipeline(mock_llm):
    """Test full test generation pipeline."""
    # Mock responses for each stage
    mock_llm.chat.side_effect = [
        # Decomposition
        '["Requirement 1", "Requirement 2"]',
        # Elaboration for req 1
        '{"requirement": "Requirement 1", "functionality": "func", "ui_design": {}, "interactions": [], "data": {"type": "none"}, "dependencies": []}',
        # Elaboration for req 2
        '{"requirement": "Requirement 2", "functionality": "func", "ui_design": {}, "interactions": [], "data": {"type": "none"}, "dependencies": []}',
        # Test case for req 1
        '{"test_id": "test_1", "requirement": "Requirement 1", "persona": {}, "steps": [], "validation": {}}',
        # Test case for req 2
        '{"test_id": "test_2", "requirement": "Requirement 2", "persona": {}, "steps": [], "validation": {}}'
    ]

    agent = TestGenerationAgent(mock_llm)
    result = agent.generate_tests("Create an app")

    assert "high_level_requirements" in result
    assert "detailed_requirements" in result
    assert "test_cases" in result
    assert len(result["high_level_requirements"]) == 2
    assert len(result["test_cases"]) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
