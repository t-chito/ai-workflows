#!/usr/bin/env python3
"""TDDev - Test-Driven Development Framework for Web Application Generation.

Automatically generates full-stack web applications from requirements via
multi-agent test-driven development.

Based on arXiv:2509.25297v2:
"Automatically Generating Web Applications from Requirements Via Multi-Agent Test-Driven Development"
by Yuxuan Wan, Tingshuo Liang, et al.

Usage:
    python main.py --input "Create a todo list app" --output ./output/todo_app
    python main.py --input "Shopping website" --image design.png --output ./output/shop
"""

import argparse
import sys
import yaml
from pathlib import Path
from loguru import logger

from utils.llm_client import LLMClient
from orchestrator.tdd_workflow import TDDWorkflow


def setup_logging(level: str = "INFO", log_file: Optional[str] = None):
    """Configure logging.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR)
        log_file: Optional log file path
    """
    logger.remove()  # Remove default handler

    # Console handler
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        level=level,
        colorize=True
    )

    # File handler
    if log_file:
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        logger.add(
            log_file,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
            level=level,
            rotation="10 MB"
        )


def load_config(config_path: str = "config/config.yaml") -> dict:
    """Load configuration from YAML file.

    Args:
        config_path: Path to config file

    Returns:
        Configuration dictionary
    """
    config_file = Path(__file__).parent / config_path

    if not config_file.exists():
        logger.warning(f"Config file not found: {config_file}")
        return {}

    with open(config_file, "r") as f:
        config = yaml.safe_load(f)

    logger.info(f"Loaded configuration from {config_file}")
    return config


def main():
    """Main entry point for TDDev."""

    # Parse arguments
    parser = argparse.ArgumentParser(
        description="TDDev - Automatic Web App Generation via Test-Driven Development",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Simple usage
  python main.py --input "Create a todo list app"

  # With design image
  python main.py --input "Shopping website" --image design.png

  # Custom output directory
  python main.py --input "Blog platform" --output ./my_blog

  # Change model
  python main.py --input "Dashboard" --model gpt-4.1 --provider openai

  # Adjust iterations
  python main.py --input "Forum app" --max-iterations 5
        """
    )

    parser.add_argument(
        "--input", "-i",
        required=True,
        help="Natural language description of the web application"
    )

    parser.add_argument(
        "--image",
        help="Optional path to design image"
    )

    parser.add_argument(
        "--output", "-o",
        default="./output/app",
        help="Output directory for generated project (default: ./output/app)"
    )

    parser.add_argument(
        "--provider",
        choices=["anthropic", "openai"],
        default="anthropic",
        help="LLM provider (default: anthropic)"
    )

    parser.add_argument(
        "--model",
        help="LLM model name (default: claude-sonnet-4-5-20250929 or gpt-4.1)"
    )

    parser.add_argument(
        "--max-iterations",
        type=int,
        default=3,
        help="Maximum TDD iterations (default: 3)"
    )

    parser.add_argument(
        "--config",
        default="config/config.yaml",
        help="Path to configuration file (default: config/config.yaml)"
    )

    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level (default: INFO)"
    )

    parser.add_argument(
        "--log-file",
        help="Optional log file path"
    )

    args = parser.parse_args()

    # Setup logging
    setup_logging(args.log_level, args.log_file)

    logger.info("=" * 80)
    logger.info("TDDev - Test-Driven Development for Web Applications")
    logger.info("Based on arXiv:2509.25297v2")
    logger.info("=" * 80)

    # Load configuration
    config = load_config(args.config)

    # Determine model
    if args.model:
        model = args.model
    elif args.provider == "anthropic":
        model = config.get("llm", {}).get("model", "claude-sonnet-4-5-20250929")
    else:  # openai
        model = "gpt-4.1"

    logger.info(f"Provider: {args.provider}")
    logger.info(f"Model: {model}")
    logger.info(f"Input: {args.input}")
    if args.image:
        logger.info(f"Design Image: {args.image}")
    logger.info(f"Output: {args.output}")
    logger.info(f"Max Iterations: {args.max_iterations}")

    # Initialize LLM client
    try:
        llm_client = LLMClient(
            provider=args.provider,
            model=model,
            temperature=config.get("llm", {}).get("temperature", 0),
            max_tokens=config.get("llm", {}).get("max_tokens", 8192)
        )
    except Exception as e:
        logger.error(f"Failed to initialize LLM client: {e}")
        logger.error("Make sure API keys are set:")
        logger.error("  - ANTHROPIC_API_KEY for Anthropic")
        logger.error("  - OPENAI_API_KEY for OpenAI")
        sys.exit(1)

    # Initialize workflow
    workflow = TDDWorkflow(
        llm_client=llm_client,
        project_root=args.output,
        config=config
    )

    # Run workflow
    try:
        result = workflow.run(
            user_input=args.input,
            design_image=args.image,
            max_iterations=args.max_iterations
        )

        # Print final summary
        logger.info("\n" + "=" * 80)
        logger.info("FINAL RESULTS")
        logger.info("=" * 80)
        logger.info(f"Success: {'✓' if result['success'] else '✗'}")
        logger.info(f"Iterations: {result['iterations']}/{args.max_iterations}")
        logger.info(f"Final Pass Rate: {result['final_pass_rate']:.1%}")
        logger.info(f"Project Path: {result['project_path']}")
        logger.info("=" * 80)

        if result['success']:
            logger.info("\n✓ Application generated successfully!")
            logger.info(f"\nTo run the application:")
            logger.info(f"  cd {result['project_path']}")
            logger.info(f"  npm install")
            logger.info(f"  npm run dev")
        else:
            logger.warning("\n⚠ Application generation incomplete.")
            logger.warning("Some tests did not pass. You may need to manually refine the code.")

        # Save summary
        summary = workflow.get_summary()
        summary_path = Path(args.output) / ".tddev" / "summary.json"
        summary_path.parent.mkdir(parents=True, exist_ok=True)

        import json
        with open(summary_path, "w") as f:
            json.dump(summary, f, indent=2)

        logger.info(f"\nSummary saved to: {summary_path}")

    except KeyboardInterrupt:
        logger.warning("\n\nWorkflow interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.exception(f"Workflow failed with error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    from typing import Optional
    main()
