"""Test Generation Agent.

Implements the three-stage test case generation pipeline:
1. Requirement Decomposition
2. Requirement Elaboration
3. Test Case Generation (Soap Opera Testing)

Based on arXiv:2509.25297v2, Section 3.1.
"""

import json
from typing import Dict, List, Optional
from loguru import logger
from pathlib import Path

from ...utils.llm_client import LLMClient


class TestGenerationAgent:
    """Multi-step test case generation agent."""

    def __init__(self, llm_client: LLMClient, config: Optional[Dict] = None):
        """Initialize test generation agent.

        Args:
            llm_client: LLM client for API calls
            config: Configuration dictionary
        """
        self.llm = llm_client
        self.config = config or {}
        logger.info("Initialized TestGenerationAgent")

    def generate_tests(
        self,
        user_input: str,
        design_image: Optional[str] = None
    ) -> Dict:
        """Generate test cases from user requirements.

        Args:
            user_input: Natural language description of the web app
            design_image: Optional path to design image

        Returns:
            Dict containing:
                - high_level_requirements: List of requirement strings
                - detailed_requirements: List of detailed requirement dicts
                - test_cases: List of test case dicts
        """
        logger.info("Starting test generation pipeline")

        # Step 1: Requirement Decomposition
        high_level_reqs = self._decompose_requirements(user_input, design_image)
        logger.info(f"Decomposed into {len(high_level_reqs)} high-level requirements")

        # Step 2: Requirement Elaboration
        detailed_reqs = self._elaborate_requirements(
            user_input, high_level_reqs, design_image
        )
        logger.info(f"Elaborated into {len(detailed_reqs)} detailed requirements")

        # Step 3: Test Case Generation
        test_cases = self._generate_test_cases(detailed_reqs)
        logger.info(f"Generated {len(test_cases)} test cases")

        return {
            "high_level_requirements": high_level_reqs,
            "detailed_requirements": detailed_reqs,
            "test_cases": test_cases
        }

    def _decompose_requirements(
        self,
        user_input: str,
        design_image: Optional[str] = None
    ) -> List[str]:
        """Step 1: Decompose user input into high-level requirements.

        Args:
            user_input: User's natural language description
            design_image: Optional design image path

        Returns:
            List of high-level requirement strings
        """
        prompt = f"""You are an expert AI Product Manager analyzing user requirements for web application development.

Your task is to decompose the following user instruction into a structured list of discrete, high-level requirements.

User Instruction:
{user_input}

Guidelines:
1. Break down the instruction into individual functional requirements
2. Include both explicit requirements (stated) and implicit requirements (inferred necessary features)
3. Consider front-end UI elements and back-end functionality
4. Keep each requirement concise but clear
5. Ensure completeness - don't miss any aspect mentioned or implied

Output Format:
Return a JSON array of requirement strings:
["Requirement 1", "Requirement 2", ...]

Example:
Input: "Create a shopping website with product catalog and cart"
Output: [
    "Provide a product catalog page displaying available items",
    "Show product details including images, descriptions, and prices",
    "Implement a shopping cart to collect selected products",
    "Display cart contents with item quantities and total price",
    "Support adding and removing items from cart",
    "Include navigation between catalog and cart pages"
]

Now analyze the user instruction and output the requirements as a JSON array:"""

        if design_image:
            response = self.llm.chat_with_vision(prompt, design_image)
        else:
            response = self.llm.chat([{"role": "user", "content": prompt}])

        # Parse JSON response
        try:
            # Extract JSON from response (handle markdown code blocks)
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0].strip()
            else:
                json_str = response.strip()

            requirements = json.loads(json_str)
            return requirements
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse requirements JSON: {e}")
            logger.error(f"Response was: {response}")
            raise

    def _elaborate_requirements(
        self,
        user_input: str,
        high_level_reqs: List[str],
        design_image: Optional[str] = None
    ) -> List[Dict]:
        """Step 2: Elaborate requirements with detailed specifications.

        Args:
            user_input: Original user input
            high_level_reqs: List of high-level requirements
            design_image: Optional design image

        Returns:
            List of detailed requirement dictionaries
        """
        detailed_reqs = []

        for req in high_level_reqs:
            prompt = f"""You are an expert software engineer elaborating on a web application requirement.

Original User Request:
{user_input}

High-Level Requirement:
{req}

Your task is to elaborate this requirement with detailed specifications including:
1. Functionality: Precise description of what needs to be implemented
2. UI Design: Visual layout, components, styling details
3. Interactions & States: User interactions, dynamic behaviors, state management
4. Data: Data sources, schemas, mock data if needed
5. Dependencies: Required libraries, APIs, external resources

Output Format (JSON):
{{
    "requirement": "The original high-level requirement",
    "functionality": "Detailed functionality description",
    "ui_design": {{
        "layout": "Layout description",
        "components": ["Component 1", "Component 2"],
        "styling": "Color scheme, fonts, spacing details"
    }},
    "interactions": [
        {{
            "trigger": "User action that triggers interaction",
            "action": "What happens",
            "expected_result": "Expected outcome"
        }}
    ],
    "data": {{
        "type": "database|api|mock|none",
        "schema": "Data structure if applicable",
        "source": "Where data comes from"
    }},
    "dependencies": ["Library 1", "Library 2"]
}}

Provide the elaborated requirement as JSON:"""

            if design_image:
                response = self.llm.chat_with_vision(prompt, design_image)
            else:
                response = self.llm.chat([{"role": "user", "content": prompt}])

            # Parse JSON
            try:
                if "```json" in response:
                    json_str = response.split("```json")[1].split("```")[0].strip()
                elif "```" in response:
                    json_str = response.split("```")[1].split("```")[0].strip()
                else:
                    json_str = response.strip()

                detailed_req = json.loads(json_str)
                detailed_reqs.append(detailed_req)
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse detailed requirement: {e}")
                # Fallback: create simple structure
                detailed_reqs.append({
                    "requirement": req,
                    "functionality": req,
                    "ui_design": {},
                    "interactions": [],
                    "data": {"type": "none"},
                    "dependencies": []
                })

        return detailed_reqs

    def _generate_test_cases(
        self,
        detailed_reqs: List[Dict]
    ) -> List[Dict]:
        """Step 3: Generate soap-opera style test cases.

        Inspired by soap opera testing: imagine a user persona with specific goals
        and generate step-by-step test instructions.

        Args:
            detailed_reqs: List of detailed requirement dicts

        Returns:
            List of test case dictionaries
        """
        test_cases = []

        for req in detailed_reqs:
            prompt = f"""You are an expert QA engineer creating test cases using the "Soap Opera Testing" methodology.

Requirement to Test:
{json.dumps(req, indent=2)}

Soap Opera Testing Approach:
1. Create a realistic user persona with specific goals
2. Write a step-by-step scenario describing user actions
3. Specify expected outcomes at each step
4. Make it read like a story, not just technical steps

Your task is to generate ONE comprehensive test case for this requirement.

Output Format (JSON):
{{
    "test_id": "Unique identifier for this test",
    "requirement": "The requirement being tested",
    "persona": {{
        "name": "User persona name",
        "goal": "What the user wants to accomplish",
        "context": "Background context"
    }},
    "steps": [
        {{
            "step_number": 1,
            "description": "Narrative description of user action",
            "action": "Specific action to perform (e.g., click, type, navigate)",
            "expected_result": "What should happen"
        }}
    ],
    "validation": {{
        "functionality": "How to verify functional correctness",
        "visual": "How to verify visual presentation"
    }}
}}

Generate the test case as JSON:"""

            response = self.llm.chat([{"role": "user", "content": prompt}])

            try:
                if "```json" in response:
                    json_str = response.split("```json")[1].split("```")[0].strip()
                elif "```" in response:
                    json_str = response.split("```")[1].split("```")[0].strip()
                else:
                    json_str = response.strip()

                test_case = json.loads(json_str)
                test_cases.append(test_case)
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse test case: {e}")
                # Create fallback test case
                test_cases.append({
                    "test_id": f"test_{len(test_cases) + 1}",
                    "requirement": req.get("requirement", ""),
                    "persona": {"name": "User", "goal": "Test functionality"},
                    "steps": [],
                    "validation": {}
                })

        return test_cases


# Example usage
if __name__ == "__main__":
    from ...utils.llm_client import LLMClient

    llm = LLMClient(provider="anthropic", model="claude-sonnet-4-5-20250929")
    agent = TestGenerationAgent(llm)

    result = agent.generate_tests(
        "Create a simple todo list app where users can add, complete, and delete tasks"
    )

    print("=" * 80)
    print("HIGH-LEVEL REQUIREMENTS:")
    print(json.dumps(result["high_level_requirements"], indent=2))
    print("\n" + "=" * 80)
    print("TEST CASES:")
    print(json.dumps(result["test_cases"], indent=2))
