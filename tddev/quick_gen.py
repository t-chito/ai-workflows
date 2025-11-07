#!/usr/bin/env python3
"""Quick app generator (no LLM required) - just creates basic template."""

import sys
from pathlib import Path

# Add tddev to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tddev.utils.file_utils import FileManager
from tddev.agents.development.agent import DevelopmentAgent
from unittest.mock import Mock

def main():
    """Generate basic app template without LLM."""
    print("=" * 80)
    print("Quick App Generator (Template Only - No LLM)")
    print("=" * 80)

    output_dir = Path("/home/user/ai-workflows/output/app")

    # Create file manager
    fm = FileManager(str(output_dir))

    # Create development agent with mock LLM
    mock_llm = Mock()
    mock_llm.chat.return_value = "vite-react"  # Select template

    dev_agent = DevelopmentAgent(mock_llm, fm)

    # Initialize project (creates basic template)
    print("\n📦 Creating basic Vite + React template...")
    template = dev_agent.initialize_project(
        "Counter app",
        ["Display counter", "Increment button", "Decrement button"]
    )

    print(f"✅ Template created: {template}")
    print(f"📁 Output directory: {output_dir}")

    # List created files
    files = fm.list_files()
    print(f"\n📄 Created {len(files)} files:")
    for f in sorted(files):
        rel_path = f.relative_to(fm.project_root)
        print(f"  - {rel_path}")

    print("\n" + "=" * 80)
    print("Next steps:")
    print("  cd output/app")
    print("  npm install")
    print("  npm run dev")
    print("=" * 80)

if __name__ == "__main__":
    main()
