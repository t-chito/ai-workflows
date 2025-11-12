# promptfooでのClaude Codeサブスクリプション認証に関する調査結果

## 結論（2025-11-12 最終確認）

**❌ Claude Codeはサブスクリプション認証が使えません。API従量課金が必須です。**

**✅ Codexはカスタムプロバイダーでサブスクリプション認証が使えます。**

## 実際に確認したエラー

カスタムプロバイダーでAnthropicのSDKを使い、`CLAUDE_CODE_OAUTH_TOKEN` で認証を試みたところ：

```json
{
  "error": "Claude Code error: 401 {\"type\":\"error\",\"error\":{\"type\":\"authentication_error\",\"message\":\"OAuth authentication is currently not supported.\"},\"request_id\":\"req_011CV3wBXPbrZPUdTTb8iNg4\"}"
}
```

**Anthropic API サーバー側が OAuth 認証を拒否しています。**

## 試したこと

### 1. Anthropic SDKを直接使用（失敗）

```javascript
import Anthropic from '@anthropic-ai/sdk';

const client = new Anthropic({
  authToken: process.env.CLAUDE_CODE_OAUTH_TOKEN,
});

// 結果: 401 "OAuth authentication is currently not supported"
```

- SDKは `CLAUDE_CODE_OAUTH_TOKEN` を読み取るコードがある
- しかし、API側がOAuth認証を拒否

### 2. claude CLIコマンドの直接呼び出し（タイムアウト）

```javascript
const claude = spawn('claude', ['-p', prompt]);
// 結果: 応答なし、タイムアウト
```

- `claude -p` (headless mode) を試したが応答なし
- `codex exec -` のようには動作しない

## なぜCodexは動くのか？

**Codexは `codex` CLIコマンドを直接呼び出している：**

```javascript
// codex-provider.js
const codex = spawn('codex', ['exec', '-'], {
  stdio: ['pipe', 'pipe', 'pipe'],
});
codex.stdin.write(prompt);
```

- `codex auth` で保存された認証情報を自動的に読み取る
- 環境変数 `OPENAI_API_KEY` は不要
- promptfooと独立して動作

## なぜClaude Codeは動かないのか？

1. **APIレベルでOAuth非対応**
   - Anthropic APIサーバーが `OAuth authentication is currently not supported` を返す
   - SDKがOAuthトークンを読んでも、サーバーが拒否

2. **CLIの非インタラクティブモードが不安定**
   - `claude -p` が応答しない
   - `codex exec -` のような安定したstdin/stdout処理がない

3. **promptfoo組み込みプロバイダーの制限**
   - `anthropic:messages` プロバイダーは `ANTHROPIC_API_KEY` のみチェック
   - カスタムプロバイダーでもAPI側が拒否するため回避不可能

## 解決策

### promptfooでClaude Codeを使う場合（唯一の方法）

```bash
# API従量課金
export ANTHROPIC_API_KEY="sk-ant-..."
npx promptfoo eval
```

promptfooconfig.yaml:

```yaml
providers:
  - id: anthropic:messages:claude-sonnet-4-20250514
    label: Claude Code
```

### promptfooでCodexを使う場合（サブスクリプション対応）

```bash
# サブスクリプション認証（環境変数不要）
codex auth
npx promptfoo eval
```

promptfooconfig.yaml:

```yaml
providers:
  - id: file://./codex-provider.js
    label: Codex
```

## 調査履歴

### 初回調査（2025-11-06）

- promptfoo組み込みプロバイダーは `ANTHROPIC_API_KEY` のみ対応
- 実行結果: Claude Code 30件ERROR、Codex 30件PASS

### カスタムプロバイダー試行（2025-11-12）

- SDKを直接使うカスタムプロバイダーを実装
- 結果: API側が `OAuth authentication is currently not supported` を返す

### CLI直接呼び出し試行（2025-11-12）

- `claude -p` (headless mode) を試行
- 結果: タイムアウト、応答なし

### 最終確認（2025-11-12）

- **結論**: Claude CodeはAPI従量課金が必須
- **理由**: APIサーバー側がOAuth認証を受け付けない
- **対比**: CodexはCLI直接呼び出しで動作

## ファイル

- `codex-provider.js`: Codexカスタムプロバイダー（サブスクリプション対応）
- `promptfooconfig.yaml`: promptfoo設定（Claude CodeはAPI key必須、Codexはサブスクリプション対応）
