/**
 * Custom promptfoo provider for OpenAI Codex CLI
 *
 * This provider calls the Codex CLI directly, allowing you to use
 * your ChatGPT Plus/Pro subscription instead of API keys.
 *
 * Prerequisites:
 * - Codex CLI installed: https://developers.openai.com/codex/cli/
 * - Authenticated: codex auth
 */

import { spawn } from 'child_process';

export default class CodexProvider {
  constructor(options = {}) {
    this.config = options.config || {};
    this.label = options.label || 'Codex';
  }

  id() {
    return 'codex-cli';
  }

  async callApi(prompt, context, options) {
    try {
      const result = await this.executeCodex(prompt);

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
        error: `Codex CLI error: ${error.message}`,
      };
    }
  }

  async executeCodex(prompt) {
    return new Promise((resolve, reject) => {
      // Use 'codex exec' for non-interactive execution
      // The '-' parameter reads from stdin
      const codex = spawn('codex', ['exec', '-'], {
        stdio: ['pipe', 'pipe', 'pipe'],
      });

      let stdout = '';
      let stderr = '';

      codex.stdout.on('data', (data) => {
        stdout += data.toString();
      });

      codex.stderr.on('data', (data) => {
        stderr += data.toString();
      });

      codex.on('close', (code) => {
        if (code !== 0) {
          reject(new Error(`Codex exited with code ${code}: ${stderr}`));
        } else {
          resolve(stdout.trim());
        }
      });

      codex.on('error', (error) => {
        reject(new Error(`Failed to spawn codex: ${error.message}`));
      });

      // Write prompt to stdin and close
      codex.stdin.write(prompt);
      codex.stdin.end();
    });
  }

  toString() {
    return '[Codex CLI Provider]';
  }
}
