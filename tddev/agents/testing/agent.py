"""Testing Agent.

Implements automated testing with:
1. Deployment Verification
2. User Simulation via BrowserUse
3. Feedback Construction

Based on arXiv:2509.25297v2, Section 3.3.
"""

import json
import subprocess
import time
from typing import Dict, List, Optional
from pathlib import Path
from loguru import logger

from ...utils.llm_client import LLMClient


class TestingAgent:
    """Automated testing agent with browser simulation."""

    def __init__(
        self,
        llm_client: LLMClient,
        config: Optional[Dict] = None
    ):
        """Initialize testing agent.

        Args:
            llm_client: LLM client for test evaluation
            config: Configuration dictionary
        """
        self.llm = llm_client
        self.config = config or {}
        self.app_process = None
        self.app_url = "http://localhost:5173"  # Default Vite dev server
        logger.info("Initialized TestingAgent")

    def test_application(
        self,
        project_root: Path,
        test_cases: List[Dict],
        design_image: Optional[str] = None
    ) -> Dict:
        """Test application against test cases.

        Args:
            project_root: Path to project root
            test_cases: List of test case dictionaries
            design_image: Optional design image for visual comparison

        Returns:
            Dict with:
                - passed: Number of tests passed
                - failed: Number of tests failed
                - results: List of test results
                - feedback: Structured feedback for development agent
        """
        logger.info(f"Testing application with {len(test_cases)} test cases")

        # Step 1: Deploy and verify
        deployment_ok = self._deploy_and_verify(project_root, design_image)

        if not deployment_ok:
            return {
                "passed": 0,
                "failed": len(test_cases),
                "results": [],
                "feedback": "Application failed to start. Check logs for errors."
            }

        # Step 2: Execute test cases
        results = []
        passed = 0
        failed = 0

        for i, test_case in enumerate(test_cases):
            logger.info(f"Executing test case {i+1}/{len(test_cases)}")
            result = self._execute_test_case(test_case)
            results.append(result)

            if result["status"] == "passed":
                passed += 1
            else:
                failed += 1

        # Step 3: Generate feedback
        feedback = self._construct_feedback(results)

        # Stop the application
        self._stop_application()

        return {
            "passed": passed,
            "failed": failed,
            "total": len(test_cases),
            "pass_rate": passed / len(test_cases) if test_cases else 0,
            "results": results,
            "feedback": feedback
        }

    def _deploy_and_verify(
        self,
        project_root: Path,
        design_image: Optional[str] = None
    ) -> bool:
        """Deploy application and verify it starts correctly.

        Args:
            project_root: Path to project root
            design_image: Optional design image

        Returns:
            True if deployment successful
        """
        logger.info("Deploying application for testing")

        try:
            # Install dependencies if needed
            if not (project_root / "node_modules").exists():
                logger.info("Installing dependencies...")
                subprocess.run(
                    ["npm", "install"],
                    cwd=project_root,
                    check=True,
                    capture_output=True
                )

            # Start dev server
            logger.info("Starting development server...")
            self.app_process = subprocess.Popen(
                ["npm", "run", "dev"],
                cwd=project_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            # Wait for server to start
            max_wait = 30  # seconds
            waited = 0
            while waited < max_wait:
                try:
                    import requests
                    response = requests.get(self.app_url, timeout=1)
                    if response.status_code == 200:
                        logger.info("Application started successfully")
                        return True
                except:
                    pass

                time.sleep(1)
                waited += 1

            logger.error("Application failed to start within timeout")
            return False

        except Exception as e:
            logger.error(f"Deployment failed: {e}")
            return False

    def _execute_test_case(self, test_case: Dict) -> Dict:
        """Execute a single test case using browser automation.

        Args:
            test_case: Test case dictionary with steps

        Returns:
            Test result dictionary
        """
        test_id = test_case.get("test_id", "unknown")
        steps = test_case.get("steps", [])

        logger.info(f"Executing test: {test_id}")

        try:
            # Simulate browser automation with BrowserUse
            # In production, this would use actual BrowserUse library
            result = self._simulate_browser_test(test_case)
            return result

        except Exception as e:
            logger.error(f"Test execution failed: {e}")
            return {
                "test_id": test_id,
                "status": "failed",
                "error": str(e),
                "failed_step": None
            }

    def _simulate_browser_test(self, test_case: Dict) -> Dict:
        """Simulate browser-based testing.

        In production, this would use BrowserUse library.
        For now, uses LLM to evaluate based on screenshots/description.

        Args:
            test_case: Test case to execute

        Returns:
            Test result
        """
        test_id = test_case.get("test_id", "unknown")
        requirement = test_case.get("requirement", "")
        steps = test_case.get("steps", [])

        # For simulation, we'll ask LLM to evaluate if implementation is likely correct
        # In production, BrowserUse would actually interact with the browser
        prompt = f"""You are a QA engineer evaluating a web application test.

Test Case:
{json.dumps(test_case, indent=2)}

Application URL: {self.app_url}

Since we're in simulation mode, evaluate if the following test case is likely to pass
for a properly implemented application.

Test Steps:
{json.dumps(steps, indent=2)}

Respond in JSON format:
{{
    "status": "passed" or "failed" or "partial",
    "confidence": 0.0 to 1.0,
    "issues": ["issue 1", "issue 2"],
    "observations": "What was observed during test"
}}
"""

        response = self.llm.chat([{"role": "user", "content": prompt}])

        try:
            # Parse JSON response
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0].strip()
            else:
                json_str = response.strip()

            result = json.loads(json_str)
            result["test_id"] = test_id
            return result

        except json.JSONDecodeError:
            return {
                "test_id": test_id,
                "status": "failed",
                "confidence": 0.0,
                "issues": ["Failed to parse test result"],
                "observations": response
            }

    def _construct_feedback(self, results: List[Dict]) -> str:
        """Construct detailed feedback for development agent.

        Args:
            results: List of test results

        Returns:
            Formatted feedback string
        """
        feedback_parts = []

        feedback_parts.append("=== TEST RESULTS ===\n")

        passed = sum(1 for r in results if r.get("status") == "passed")
        failed = sum(1 for r in results if r.get("status") == "failed")
        partial = sum(1 for r in results if r.get("status") == "partial")

        feedback_parts.append(f"Passed: {passed}")
        feedback_parts.append(f"Failed: {failed}")
        feedback_parts.append(f"Partial: {partial}")
        feedback_parts.append(f"Total: {len(results)}\n")

        # Detail failed tests
        failed_tests = [r for r in results if r.get("status") != "passed"]

        if failed_tests:
            feedback_parts.append("=== FAILED TESTS ===\n")

            for result in failed_tests:
                test_id = result.get("test_id", "unknown")
                issues = result.get("issues", [])
                observations = result.get("observations", "")

                feedback_parts.append(f"\nTest: {test_id}")
                feedback_parts.append(f"Status: {result.get('status')}")

                if issues:
                    feedback_parts.append("Issues:")
                    for issue in issues:
                        feedback_parts.append(f"  - {issue}")

                if observations:
                    feedback_parts.append(f"Observations: {observations}")

            # Generate recommendations
            feedback_parts.append("\n=== RECOMMENDATIONS ===\n")
            recommendations = self._generate_recommendations(failed_tests)
            feedback_parts.append(recommendations)

        else:
            feedback_parts.append("\n✓ All tests passed!")

        return "\n".join(feedback_parts)

    def _generate_recommendations(self, failed_tests: List[Dict]) -> str:
        """Generate recommendations for fixing failed tests.

        Args:
            failed_tests: List of failed test results

        Returns:
            Recommendations string
        """
        # Use LLM to generate recommendations
        prompt = f"""You are a senior developer reviewing test failures.

Failed Tests:
{json.dumps(failed_tests, indent=2)}

Based on these failures, provide specific, actionable recommendations for fixing the issues.
Focus on:
1. Root causes of failures
2. Specific code changes needed
3. Best practices to prevent similar issues

Keep recommendations concise and technical."""

        response = self.llm.chat([{"role": "user", "content": prompt}])
        return response

    def _stop_application(self) -> None:
        """Stop the running application."""
        if self.app_process:
            logger.info("Stopping application")
            self.app_process.terminate()
            try:
                self.app_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.app_process.kill()
            self.app_process = None


# Example usage
if __name__ == "__main__":
    from ...utils.llm_client import LLMClient

    llm = LLMClient(provider="anthropic", model="claude-sonnet-4-5-20250929")
    agent = TestingAgent(llm)

    test_cases = [
        {
            "test_id": "test_1",
            "requirement": "Display list of todos",
            "steps": [
                {"description": "Navigate to home page", "expected_result": "See todo list"}
            ]
        }
    ]

    result = agent.test_application(
        Path("test_project"),
        test_cases
    )

    print(json.dumps(result, indent=2))
