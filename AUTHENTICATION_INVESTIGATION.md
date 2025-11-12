# promptfooでのClaude Codeサブスクリプション認証に関する調査結果

## 結論（2025-11-12 更新）

**✅ カスタムプロバイダーを使えばサブスクリプション認証が使えます！**

promptfooの組み込みプロバイダーでは `ANTHROPIC_API_KEY` が必須ですが、
カスタムプロバイダーでAnthropicのSDKを直接呼び出すことで `CLAUDE_CODE_OAUTH_TOKEN` が使えます。

## 解決策

### 1. カスタムプロバイダーの実装（推奨）

`claude-code-provider.js` を作成：

```javascript
import Anthropic from '@anthropic-ai/sdk';

export default class ClaudeCodeProvider {
  constructor(options = {}) {
    this.client = new Anthropic({
      apiKey: process.env.ANTHROPIC_API_KEY || null,
      authToken: process.env.ANTHROPIC_AUTH_TOKEN ||
                 process.env.CLAUDE_CODE_OAUTH_TOKEN ||
                 null,
      dangerouslyAllowBrowser: false,
    });
  }
  // ... callApi() implementation
}
```

promptfooconfig.yaml で使用：

```yaml
providers:
  - id: file://./claude-code-provider.js
    label: Claude Code
    config:
      model: claude-sonnet-4-20250514
```

認証：

```bash
claude login
claude setup-token
export CLAUDE_CODE_OAUTH_TOKEN="<token>"
npx promptfoo eval
```

### 2. API従量課金（代替手段）

```bash
export ANTHROPIC_API_KEY="sk-ant-api03-..."
npx promptfoo eval
```

## 背景：promptfoo組み込みプロバイダーの制限

### 問題

promptfooの組み込み `anthropic:claude-agent-sdk` プロバイダーは `CLAUDE_CODE_OAUTH_TOKEN` をサポートしていません。

### 根本原因

**ソース**: `node_modules/promptfoo/dist/src/providers/claude-agent-sdk.js:349`

```javascript
getApiKey() {
    return this.config?.apiKey ||
           this.env?.ANTHROPIC_API_KEY ||
           getEnvString('ANTHROPIC_API_KEY');
}
```

- `ANTHROPIC_API_KEY` のみをチェック
- `CLAUDE_CODE_OAUTH_TOKEN` はチェックしていない

## 認証の区別

### Claude Agent SDK（Anthropic公式SDK）
- ✅ **サブスクリプション認証対応**: `CLAUDE_CODE_OAUTH_TOKEN`、`ANTHROPIC_AUTH_TOKEN` をサポート
- ✅ API従量課金対応: `ANTHROPIC_API_KEY` をサポート
- **ソース**: `node_modules/@anthropic-ai/claude-agent-sdk/cli.js` に両方の環境変数チェックが存在

### promptfoo組み込みプロバイダー
- ❌ サブスクリプション認証非対応
- ✅ API従量課金のみ: `ANTHROPIC_API_KEY`

### カスタムプロバイダー（このリポジトリの実装）
- ✅ **サブスクリプション認証対応**: `CLAUDE_CODE_OAUTH_TOKEN` 使用可能
- ✅ API従量課金対応: `ANTHROPIC_API_KEY` 使用可能
- SDKを直接呼び出すため、SDKの全機能を利用可能

## Codexのカスタムプロバイダー

Codexも同様にカスタムプロバイダーでサブスクリプション認証を実現：

```javascript
import { spawn } from 'child_process';

export default class CodexProvider {
  async callApi(prompt) {
    const codex = spawn('codex', ['exec', '-']);
    codex.stdin.write(prompt);
    codex.stdin.end();
    // ... output handling
  }
}
```

## 調査履歴

### 初回調査（2025-11-06）

- promptfoo組み込みプロバイダーは `ANTHROPIC_API_KEY` のみ対応
- 実行結果: Claude Code 30件ERROR、Codex 30件PASS（カスタムプロバイダー）

### 解決（2025-11-12）

- カスタムプロバイダーでSDKを直接呼び出すことで解決
- 両方のモデルでサブスクリプション認証が使用可能に

## ファイル

- `claude-code-provider.js`: Claude Codeカスタムプロバイダー（サブスクリプション対応）
- `codex-provider.js`: Codexカスタムプロバイダー（サブスクリプション対応）
- `promptfooconfig.yaml`: promptfoo設定（カスタムプロバイダー使用）
