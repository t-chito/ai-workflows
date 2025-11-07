"""Simple demo of TDDev functionality (without actual LLM calls).

This demonstrates the structure and flow of the TDDev system.
"""

import json
from pathlib import Path
from unittest.mock import Mock
from tddev.agents.test_generation import TestGenerationAgent
from tddev.agents.development import DevelopmentAgent
from tddev.agents.testing import TestingAgent
from tddev.utils.file_utils import FileManager


def demo_test_generation():
    """Demo: Test Generation Agent"""
    print("\n" + "=" * 80)
    print("DEMO 1: Test Generation Agent")
    print("=" * 80)

    # Create mock LLM
    mock_llm = Mock()

    # Mock responses for each stage
    mock_llm.chat.side_effect = [
        # Decomposition
        json.dumps([
            "Display list of todos",
            "Add new todo items",
            "Mark todos as complete",
            "Delete todos"
        ]),
        # Elaboration for req 1
        json.dumps({
            "requirement": "Display list of todos",
            "functionality": "Show all todos in a list",
            "ui_design": {"layout": "vertical", "components": ["TodoItem"]},
            "interactions": [],
            "data": {"type": "mock"},
            "dependencies": []
        }),
        # Elaboration for req 2
        json.dumps({
            "requirement": "Add new todo items",
            "functionality": "Add todos via input field",
            "ui_design": {"layout": "form", "components": ["Input", "Button"]},
            "interactions": [{"trigger": "click", "action": "add"}],
            "data": {"type": "mock"},
            "dependencies": []
        }),
        # Elaboration for req 3
        json.dumps({
            "requirement": "Mark todos as complete",
            "functionality": "Toggle todo completion state",
            "ui_design": {}, "interactions": [], "data": {"type": "mock"}, "dependencies": []
        }),
        # Elaboration for req 4
        json.dumps({
            "requirement": "Delete todos",
            "functionality": "Remove todos from list",
            "ui_design": {}, "interactions": [], "data": {"type": "mock"}, "dependencies": []
        }),
        # Test cases (4 total)
        json.dumps({"test_id": "test_1", "requirement": "Display list", "persona": {}, "steps": [], "validation": {}}),
        json.dumps({"test_id": "test_2", "requirement": "Add todo", "persona": {}, "steps": [], "validation": {}}),
        json.dumps({"test_id": "test_3", "requirement": "Complete todo", "persona": {}, "steps": [], "validation": {}}),
        json.dumps({"test_id": "test_4", "requirement": "Delete todo", "persona": {}, "steps": [], "validation": {}})
    ]

    agent = TestGenerationAgent(mock_llm)
    result = agent.generate_tests("Create a todo list app")

    print("\n✅ Generated Test Data:")
    print(f"  High-Level Requirements: {len(result['high_level_requirements'])}")
    print(f"  Detailed Requirements: {len(result['detailed_requirements'])}")
    print(f"  Test Cases: {len(result['test_cases'])}")

    print("\n📋 High-Level Requirements:")
    for i, req in enumerate(result['high_level_requirements'], 1):
        print(f"  {i}. {req}")

    print("\n🧪 Test Cases:")
    for tc in result['test_cases']:
        print(f"  - {tc['test_id']}: {tc['requirement']}")


def demo_file_management():
    """Demo: File Management"""
    print("\n" + "=" * 80)
    print("DEMO 2: File Management")
    print("=" * 80)

    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        fm = FileManager(tmpdir)

        # Create files
        fm.write_file(Path("package.json"), '{"name": "demo-app"}')
        fm.write_file(Path("src/App.tsx"), "import React from 'react';")
        fm.write_file(Path("src/index.css"), "body { margin: 0; }")

        print("\n✅ Created Project Files:")
        files = fm.list_files()
        for f in files:
            print(f"  - {f.relative_to(fm.project_root)}")

        # Get context buffer
        context = fm.get_context_buffer([Path("src/App.tsx")])
        print("\n📄 Context Buffer (excerpt):")
        print(f"  {context[:100]}...")

        # File tree
        print("\n🌳 Project Structure:")
        tree = fm.get_file_tree(max_depth=2)
        for line in tree.split('\n')[:10]:
            print(f"  {line}")


def demo_development_agent():
    """Demo: Development Agent"""
    print("\n" + "=" * 80)
    print("DEMO 3: Development Agent")
    print("=" * 80)

    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        mock_llm = Mock()
        fm = FileManager(tmpdir)

        agent = DevelopmentAgent(mock_llm, fm)

        # Mock template selection
        mock_llm.chat.return_value = "vite-react"

        template = agent.initialize_project(
            "Create a todo list app",
            ["Display todos", "Add todos", "Delete todos"]
        )

        print(f"\n✅ Selected Template: {template}")

        # Check created files
        files = fm.list_files()
        print(f"\n📁 Created {len(files)} files:")
        for f in sorted(files)[:5]:
            print(f"  - {f.relative_to(fm.project_root)}")
        if len(files) > 5:
            print(f"  ... and {len(files) - 5} more")


def main():
    """Run all demos."""
    print("\n" + "=" * 80)
    print("TDDev - Demonstration (Mock Mode)")
    print("=" * 80)
    print("\nThis demo shows TDDev's structure without making real LLM API calls.")

    try:
        demo_test_generation()
        demo_file_management()
        demo_development_agent()

        print("\n" + "=" * 80)
        print("✅ DEMO COMPLETE")
        print("=" * 80)
        print("\nAll components are working correctly!")
        print("\nTo run with real LLM:")
        print("  1. Set ANTHROPIC_API_KEY or OPENAI_API_KEY")
        print("  2. Run: python main.py --input 'Create a todo app'")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
