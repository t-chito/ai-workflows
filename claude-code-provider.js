/**
 * Custom promptfoo provider for Claude Code
 *
 * This provider uses the Anthropic SDK directly with CLAUDE_CODE_OAUTH_TOKEN,
 * allowing you to use your Claude subscription instead of API keys.
 *
 * Prerequisites:
 * - CLAUDE_CODE_OAUTH_TOKEN environment variable set
 *   (or ANTHROPIC_AUTH_TOKEN or ANTHROPIC_API_KEY as fallback)
 */

import Anthropic from '@anthropic-ai/sdk';

export default class ClaudeCodeProvider {
  constructor(options = {}) {
    this.config = options.config || {};
    this.label = options.label || 'Claude Code';
    this.model = this.config.model || 'claude-sonnet-4-20250514';

    // Initialize Anthropic client
    // The SDK checks CLAUDE_CODE_OAUTH_TOKEN, ANTHROPIC_AUTH_TOKEN, and ANTHROPIC_API_KEY
    this.client = new Anthropic({
      apiKey: process.env.ANTHROPIC_API_KEY || null,
      authToken: process.env.ANTHROPIC_AUTH_TOKEN ||
                 process.env.CLAUDE_CODE_OAUTH_TOKEN ||
                 null,
      dangerouslyAllowBrowser: false,
    });
  }

  id() {
    return 'claude-code-subscription';
  }

  async callApi(prompt, context, options) {
    try {
      const response = await this.client.messages.create({
        model: this.model,
        max_tokens: this.config.max_tokens || 2000,
        temperature: this.config.temperature ?? 0.7,
        messages: [
          {
            role: 'user',
            content: prompt,
          },
        ],
      });

      // Extract text content from response
      const textContent = response.content
        .filter((block) => block.type === 'text')
        .map((block) => block.text)
        .join('\n');

      return {
        output: textContent,
        tokenUsage: {
          total: response.usage.input_tokens + response.usage.output_tokens,
          prompt: response.usage.input_tokens,
          completion: response.usage.output_tokens,
        },
      };
    } catch (error) {
      return {
        error: `Claude Code error: ${error.message}`,
      };
    }
  }

  toString() {
    return '[Claude Code Subscription Provider]';
  }
}
