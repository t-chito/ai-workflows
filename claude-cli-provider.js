/**
 * Custom promptfoo provider for Claude CLI
 *
 * This provider calls the Claude CLI directly, similar to codex-provider.js.
 * Uses claude's headless mode with stdin input.
 *
 * Prerequisites:
 * - claude login (authenticates with your Claude subscription)
 * - No environment variables needed (authentication is saved by claude login)
 *
 * Based on: https://code.claude.com/docs/en/headless
 */

import { spawn } from 'child_process';

export default class ClaudeCliProvider {
  constructor(options = {}) {
    this.config = options.config || {};
    this.label = options.label || 'Claude CLI';
  }

  id() {
    return 'claude-cli';
  }

  async callApi(prompt, context, options) {
    try {
      const result = await this.executeClaude(prompt);

      return {
        output: result,
        tokenUsage: {
          // Token usage is tracked by your subscription
          total: 0,
          prompt: 0,
          completion: 0,
        },
      };
    } catch (error) {
      return {
        error: `Claude CLI error: ${error.message}`,
      };
    }
  }

  async executeClaude(prompt) {
    return new Promise((resolve, reject) => {
      // Use 'claude -p' for headless/non-interactive mode
      // Pipe input via stdin, similar to: echo "prompt" | claude -p
      const claude = spawn('claude', ['-p'], {
        stdio: ['pipe', 'pipe', 'pipe'],
      });

      let stdout = '';
      let stderr = '';

      claude.stdout.on('data', (data) => {
        stdout += data.toString();
      });

      claude.stderr.on('data', (data) => {
        stderr += data.toString();
      });

      claude.on('close', (code) => {
        if (code !== 0) {
          reject(new Error(`Claude exited with code ${code}: ${stderr}`));
        } else {
          resolve(stdout.trim());
        }
      });

      claude.on('error', (error) => {
        reject(new Error(`Failed to spawn claude: ${error.message}`));
      });

      // Write prompt to stdin and close
      // This simulates: echo "prompt" | claude -p
      claude.stdin.write(prompt);
      claude.stdin.end();
    });
  }

  toString() {
    return '[Claude CLI Provider]';
  }
}
