"""Development Agent.

Implements full-stack development with:
1. Template Fetching and Selection
2. Context Selection for file editing
3. File Editing with LLM

Based on arXiv:2509.25297v2, Section 3.2.
Forked from Bolt.diy.
"""

import json
import re
from typing import Dict, List, Optional, Set
from pathlib import Path
from loguru import logger

from ...utils.llm_client import LLMClient
from ...utils.file_utils import FileManager


class DevelopmentAgent:
    """Full-stack development agent with template and file management."""

    # Template definitions from Table 3 in paper
    TEMPLATES = {
        "expo-app": {
            "name": "Expo App",
            "description": "Cross-platform mobile app development",
            "github": "https://github.com/expo/expo/tree/main/templates/expo-template-blank-typescript"
        },
        "basic-astro": {
            "name": "Basic Astro",
            "description": "Static website generation",
            "github": "https://github.com/withastro/astro/tree/main/examples/basics"
        },
        "nextjs-shadcn": {
            "name": "NextJS Shadcn",
            "description": "Full-stack Next.js with shadcn/ui components",
            "github": "https://github.com/shadcn-ui/next-template"
        },
        "vite-react": {
            "name": "Vite React",
            "description": "React with TypeScript",
            "github": "https://github.com/vitejs/vite/tree/main/packages/create-vite/template-react-ts"
        },
        "vite-typescript": {
            "name": "Vite TypeScript",
            "description": "Type-safe development",
            "github": "https://github.com/vitejs/vite/tree/main/packages/create-vite/template-vanilla-ts"
        },
        "vuejs": {
            "name": "Vue.js",
            "description": "Vue applications",
            "github": "https://github.com/vuejs/create-vue"
        },
        # ... additional templates omitted for brevity
    }

    def __init__(
        self,
        llm_client: LLMClient,
        file_manager: FileManager,
        config: Optional[Dict] = None
    ):
        """Initialize development agent.

        Args:
            llm_client: LLM client for code generation
            file_manager: File manager for project operations
            config: Configuration dictionary
        """
        self.llm = llm_client
        self.fm = file_manager
        self.config = config or {}
        self.context_buffer: List[Path] = []
        self.locked_files: Set[Path] = set()
        logger.info("Initialized DevelopmentAgent")

    def initialize_project(
        self,
        user_input: str,
        high_level_reqs: List[str]
    ) -> str:
        """Initialize project from appropriate template.

        Args:
            user_input: User's requirements
            high_level_reqs: High-level requirements list

        Returns:
            Selected template name
        """
        logger.info("Selecting template for project")
        template_name = self._select_template(user_input, high_level_reqs)
        logger.info(f"Selected template: {template_name}")

        # For now, we'll create a basic structure
        # In production, this would clone from GitHub
        self._create_basic_template(template_name)

        return template_name

    def _select_template(self, user_input: str, high_level_reqs: List[str]) -> str:
        """Select appropriate template based on requirements.

        Args:
            user_input: Original user input
            high_level_reqs: List of requirements

        Returns:
            Template identifier
        """
        # Build template options string
        template_list = "\n".join([
            f"- {key}: {info['description']}"
            for key, info in self.TEMPLATES.items()
        ])

        prompt = f"""You are selecting a web development template for a project.

User Requirements:
{user_input}

High-Level Requirements:
{json.dumps(high_level_reqs, indent=2)}

Available Templates:
{template_list}

Select the MOST APPROPRIATE template for this project.

Respond with ONLY the template key (e.g., "nextjs-shadcn", "vite-react", etc.)
Do not include any explanation, just the template key."""

        response = self.llm.chat([{"role": "user", "content": prompt}])
        template_key = response.strip().lower()

        # Validate template exists
        if template_key not in self.TEMPLATES:
            logger.warning(f"Invalid template '{template_key}', defaulting to vite-react")
            template_key = "vite-react"

        return template_key

    def _create_basic_template(self, template_name: str) -> None:
        """Create basic template structure.

        In production, this would clone from GitHub repo.
        For now, creates minimal structure.

        Args:
            template_name: Template identifier
        """
        logger.info(f"Creating basic template structure for {template_name}")

        # Create package.json
        package_json = {
            "name": "tddev-app",
            "version": "1.0.0",
            "type": "module",
            "scripts": {
                "dev": "vite",
                "build": "vite build",
                "preview": "vite preview"
            },
            "dependencies": {
                "react": "^18.2.0",
                "react-dom": "^18.2.0"
            },
            "devDependencies": {
                "@types/react": "^18.2.0",
                "@types/react-dom": "^18.2.0",
                "@vitejs/plugin-react": "^4.0.0",
                "typescript": "^5.0.0",
                "vite": "^5.0.0"
            }
        }

        self.fm.write_file(
            Path("package.json"),
            json.dumps(package_json, indent=2)
        )

        # Create basic file structure
        basic_files = {
            "index.html": """<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>TDDev App</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>""",
            "src/main.tsx": """import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)""",
            "src/App.tsx": """import React from 'react'

function App() {
  return (
    <div className="app">
      <h1>Welcome to TDDev</h1>
      <p>Your application will be generated here.</p>
    </div>
  )
}

export default App""",
            "src/index.css": """* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
  line-height: 1.6;
  color: #333;
}

.app {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}""",
            "vite.config.ts": """import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
})""",
            "tsconfig.json": """{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}"""
        }

        for file_path, content in basic_files.items():
            self.fm.write_file(Path(file_path), content)

        logger.info("Basic template structure created")

    def develop(
        self,
        user_input: str,
        high_level_reqs: List[str],
        detailed_reqs: List[Dict],
        feedback: Optional[str] = None
    ) -> Dict:
        """Generate or update code based on requirements.

        Args:
            user_input: Original user requirements
            high_level_reqs: High-level requirement list
            detailed_reqs: Detailed requirements with specifications
            feedback: Optional feedback from testing agent

        Returns:
            Dict with:
                - files_modified: List of modified file paths
                - actions_taken: List of action descriptions
        """
        logger.info("Starting development cycle")

        # Step 1: Select relevant files for context
        relevant_files = self._select_context(user_input, detailed_reqs, feedback)
        logger.info(f"Selected {len(relevant_files)} files for context")

        # Step 2: Build context buffer
        context = self.fm.get_context_buffer(relevant_files)

        # Step 3: Generate development prompt
        dev_prompt = self._build_development_prompt(
            user_input,
            high_level_reqs,
            detailed_reqs,
            context,
            feedback
        )

        # Step 4: Get LLM response with file actions
        response = self.llm.chat([{"role": "user", "content": dev_prompt}])

        # Step 5: Parse and apply file actions
        actions = self._parse_file_actions(response)
        files_modified = self._apply_file_actions(actions)

        logger.info(f"Modified {len(files_modified)} files")

        return {
            "files_modified": [str(f) for f in files_modified],
            "actions_taken": [a.get("type") for a in actions]
        }

    def _select_context(
        self,
        user_input: str,
        detailed_reqs: List[Dict],
        feedback: Optional[str]
    ) -> List[Path]:
        """Select relevant files for context (Section 3.2 Context Selection).

        Args:
            user_input: User requirements
            detailed_reqs: Detailed requirements
            feedback: Testing feedback

        Returns:
            List of relevant file paths
        """
        # Get all project files
        all_files = self.fm.list_files()

        if len(all_files) == 0:
            return []

        # Build file list string
        file_list = "\n".join([str(f.relative_to(self.fm.project_root)) for f in all_files])

        # Build current context buffer string
        current_context = "\n".join([
            str(f.relative_to(self.fm.project_root)) for f in self.context_buffer
        ])

        # Build feedback section
        feedback_section = f"Testing Feedback:\n{feedback}\n" if feedback else ""

        prompt = f"""You are a software engineer working on a project.

Available Files:
{file_list}

Current Context Buffer:
{current_context}

User Requirements:
{user_input}

Detailed Requirements:
{json.dumps(detailed_reqs, indent=2)[:1000]}...

{feedback_section}
Your task: Select only the files that are RELEVANT to implement or modify for the current requirements.

Respond in the following XML format:
<files>
<include>path/to/file1.tsx</include>
<include>path/to/file2.css</include>
<exclude>path/to/irrelevant.tsx</exclude>
</files>

Only include files that need to be read or modified. Exclude build artifacts, node_modules, etc."""

        response = self.llm.chat([{"role": "user", "content": prompt}])

        # Parse XML response
        included_files = []
        include_pattern = r'<include>(.*?)</include>'
        matches = re.findall(include_pattern, response)

        for match in matches:
            file_path = self.fm.project_root / match.strip()
            if file_path.exists():
                included_files.append(file_path)

        # Update context buffer
        self.context_buffer = included_files

        return included_files

    def _build_development_prompt(
        self,
        user_input: str,
        high_level_reqs: List[str],
        detailed_reqs: List[Dict],
        context: str,
        feedback: Optional[str]
    ) -> str:
        """Build development prompt (Section 3.2 Prompt Construction).

        Args:
            user_input: User input
            high_level_reqs: High-level requirements
            detailed_reqs: Detailed requirements
            context: Context buffer with file contents
            feedback: Testing feedback

        Returns:
            Complete development prompt
        """
        # Build feedback instruction
        if feedback:
            feedback_instruction = f"Testing Feedback:\n{feedback}\n\nPlease fix the issues identified in the testing feedback."
        else:
            feedback_instruction = "Please implement the requirements."

        prompt = f"""You are a software engineer working on a web application project.

<Context Buffer>
{context}
</Context Buffer>

User Requirements:
{user_input}

High-Level Requirements:
{json.dumps(high_level_reqs, indent=2)}

Detailed Requirements:
{json.dumps(detailed_reqs, indent=2)}

{feedback_instruction}

Instructions:
1. Generate or update files to meet the requirements
2. Ensure code is clean, well-structured, and follows best practices
3. Include necessary imports and dependencies
4. Make sure the application is functional and complete

Output Format:
For each file operation, use the following XML format:

<Action type="file" filePath="path/to/file.tsx">
[Complete file content here]
</Action>

For deleting files:
<Action type="delete" filePath="path/to/file.tsx" />

Please generate the necessary file actions:"""

        return prompt

    def _parse_file_actions(self, response: str) -> List[Dict]:
        """Parse file actions from LLM response.

        Args:
            response: LLM response with XML action tags

        Returns:
            List of action dictionaries
        """
        actions = []

        # Parse <Action> tags
        action_pattern = r'<Action\s+type="([^"]+)"\s+filePath="([^"]+)"(?:\s*/>|>(.*?)</Action>)'
        matches = re.findall(action_pattern, response, re.DOTALL)

        for match in matches:
            action_type, file_path, content = match
            actions.append({
                "type": action_type,
                "filePath": file_path,
                "content": content.strip() if content else ""
            })

        logger.debug(f"Parsed {len(actions)} file actions")
        return actions

    def _apply_file_actions(self, actions: List[Dict]) -> List[Path]:
        """Apply file actions to project.

        Args:
            actions: List of action dictionaries

        Returns:
            List of modified file paths
        """
        modified_files = []

        for action in actions:
            try:
                self.fm.apply_file_action(action)
                file_path = Path(action["filePath"])
                modified_files.append(file_path)
            except Exception as e:
                logger.error(f"Failed to apply action: {e}")

        return modified_files


# Example usage
if __name__ == "__main__":
    from ...utils.llm_client import LLMClient
    from ...utils.file_utils import FileManager

    llm = LLMClient(provider="anthropic", model="claude-sonnet-4-5-20250929")
    fm = FileManager("test_project")
    agent = DevelopmentAgent(llm, fm)

    # Initialize project
    template = agent.initialize_project(
        "Create a todo list app",
        ["Display list of todos", "Add new todos", "Mark todos as complete"]
    )
    print(f"Initialized with template: {template}")
