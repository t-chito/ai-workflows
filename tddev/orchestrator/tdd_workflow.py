"""TDD Workflow Orchestrator.

Implements the complete TDD workflow as described in arXiv:2509.25297v2.

Workflow:
1. Test Generation: Create test cases from requirements
2. Development: Implement code to pass tests
3. Testing: Execute tests and collect feedback
4. Refinement: Iterate until tests pass or max iterations reached

Based on Section 4 and experimental setup from the paper.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
from loguru import logger

from ..agents.test_generation import TestGenerationAgent
from ..agents.development import DevelopmentAgent
from ..agents.testing import TestingAgent
from ..utils.llm_client import LLMClient
from ..utils.file_utils import FileManager


class TDDWorkflow:
    """Orchestrates the TDD workflow with multiple agents."""

    def __init__(
        self,
        llm_client: LLMClient,
        project_root: str,
        config: Optional[Dict] = None
    ):
        """Initialize TDD workflow.

        Args:
            llm_client: LLM client for all agents
            project_root: Root directory for generated project
            config: Configuration dictionary
        """
        self.llm = llm_client
        self.project_root = Path(project_root)
        self.config = config or {}

        # Initialize agents
        self.fm = FileManager(str(self.project_root))
        self.test_gen_agent = TestGenerationAgent(llm_client, config)
        self.dev_agent = DevelopmentAgent(llm_client, self.fm, config)
        self.test_agent = TestingAgent(llm_client, config)

        # Workflow state
        self.test_results = []
        self.development_history = []

        logger.info(f"Initialized TDDWorkflow at {self.project_root}")

    def run(
        self,
        user_input: str,
        design_image: Optional[str] = None,
        max_iterations: int = 3
    ) -> Dict:
        """Run complete TDD workflow.

        Args:
            user_input: Natural language description of web app
            design_image: Optional path to design image
            max_iterations: Maximum refinement iterations (default: 3 from paper)

        Returns:
            Dict with:
                - success: Boolean indicating if all tests passed
                - iterations: Number of iterations performed
                - final_pass_rate: Final test pass rate
                - project_path: Path to generated project
                - test_results: Final test results
        """
        logger.info("=" * 80)
        logger.info("STARTING TDD WORKFLOW")
        logger.info("=" * 80)

        # Phase 1: Test Generation
        logger.info("\n[PHASE 1] GENERATING TEST CASES")
        test_data = self.test_gen_agent.generate_tests(user_input, design_image)

        high_level_reqs = test_data["high_level_requirements"]
        detailed_reqs = test_data["detailed_requirements"]
        test_cases = test_data["test_cases"]

        logger.info(f"Generated {len(test_cases)} test cases")
        self._save_test_data(test_data)

        # Phase 2: Initialize Project
        logger.info("\n[PHASE 2] INITIALIZING PROJECT")
        template = self.dev_agent.initialize_project(user_input, high_level_reqs)
        logger.info(f"Initialized project with template: {template}")

        # Phase 3: TDD Loop
        logger.info("\n[PHASE 3] STARTING TDD LOOP")
        feedback = None
        iteration = 0
        final_result = None

        while iteration < max_iterations:
            iteration += 1
            logger.info(f"\n{'='*80}")
            logger.info(f"ITERATION {iteration}/{max_iterations}")
            logger.info(f"{'='*80}")

            # Step 3.1: Development
            logger.info("\n[Step 1] DEVELOPMENT")
            dev_result = self.dev_agent.develop(
                user_input=user_input,
                high_level_reqs=high_level_reqs,
                detailed_reqs=detailed_reqs,
                feedback=feedback
            )
            self.development_history.append(dev_result)
            logger.info(f"Modified {len(dev_result['files_modified'])} files")

            # Step 3.2: Testing
            logger.info("\n[Step 2] TESTING")
            test_result = self.test_agent.test_application(
                self.project_root,
                test_cases,
                design_image
            )
            self.test_results.append(test_result)

            pass_rate = test_result["pass_rate"]
            logger.info(f"Pass Rate: {pass_rate:.1%} ({test_result['passed']}/{test_result['total']})")

            # Save intermediate results
            self._save_iteration_result(iteration, dev_result, test_result)

            # Check if we should continue
            if pass_rate >= 0.95:  # 95% pass rate threshold
                logger.info("\n✓ Tests passed! Workflow complete.")
                final_result = test_result
                break

            # Step 3.3: Extract feedback for next iteration
            feedback = test_result["feedback"]
            logger.info(f"\n[Step 3] FEEDBACK FOR NEXT ITERATION:")
            logger.info(feedback[:500] + "..." if len(feedback) > 500 else feedback)

            final_result = test_result

        # Phase 4: Summary
        logger.info("\n" + "=" * 80)
        logger.info("WORKFLOW COMPLETE")
        logger.info("=" * 80)

        success = final_result["pass_rate"] >= 0.95 if final_result else False
        logger.info(f"Success: {success}")
        logger.info(f"Iterations: {iteration}")
        logger.info(f"Final Pass Rate: {final_result['pass_rate']:.1%}" if final_result else "N/A")
        logger.info(f"Project Path: {self.project_root}")

        return {
            "success": success,
            "iterations": iteration,
            "final_pass_rate": final_result["pass_rate"] if final_result else 0.0,
            "project_path": str(self.project_root),
            "test_results": final_result,
            "test_data": test_data
        }

    def _save_test_data(self, test_data: Dict) -> None:
        """Save test generation data to file.

        Args:
            test_data: Test generation results
        """
        output_dir = self.project_root / ".tddev"
        output_dir.mkdir(exist_ok=True)

        # Save as JSON
        with open(output_dir / "test_data.json", "w") as f:
            json.dump(test_data, f, indent=2)

        logger.debug("Saved test data to .tddev/test_data.json")

    def _save_iteration_result(
        self,
        iteration: int,
        dev_result: Dict,
        test_result: Dict
    ) -> None:
        """Save iteration results.

        Args:
            iteration: Iteration number
            dev_result: Development result
            test_result: Test result
        """
        output_dir = self.project_root / ".tddev" / "iterations"
        output_dir.mkdir(parents=True, exist_ok=True)

        result = {
            "iteration": iteration,
            "development": dev_result,
            "testing": test_result
        }

        with open(output_dir / f"iteration_{iteration}.json", "w") as f:
            json.dump(result, f, indent=2)

        logger.debug(f"Saved iteration {iteration} results")

    def get_summary(self) -> Dict:
        """Get workflow summary.

        Returns:
            Summary dictionary with statistics
        """
        if not self.test_results:
            return {"status": "not_run"}

        final_result = self.test_results[-1]

        return {
            "iterations": len(self.test_results),
            "final_pass_rate": final_result["pass_rate"],
            "final_passed": final_result["passed"],
            "final_failed": final_result["failed"],
            "total_tests": final_result["total"],
            "files_modified_total": sum(
                len(d.get("files_modified", [])) for d in self.development_history
            ),
            "project_path": str(self.project_root)
        }


# Example usage
if __name__ == "__main__":
    from ..utils.llm_client import LLMClient

    # Initialize
    llm = LLMClient(provider="anthropic", model="claude-sonnet-4-5-20250929")
    workflow = TDDWorkflow(llm, "output/todo_app")

    # Run workflow
    result = workflow.run(
        user_input="Create a simple todo list app where users can add, complete, and delete tasks",
        max_iterations=3
    )

    # Print summary
    print("\n" + "=" * 80)
    print("FINAL SUMMARY")
    print("=" * 80)
    print(json.dumps(workflow.get_summary(), indent=2))
