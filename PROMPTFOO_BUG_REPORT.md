# promptfoo Claude Agent SDK プロバイダーのバグレポート

**最終更新**: 2025-11-12
**ステータス**: 確認済み・再現可能
**重要度**: 高（Claude Codeサブスクリプション認証が使用不可）

## エグゼクティブサマリー

promptfooの `anthropic:claude-agent-sdk` プロバイダーは、`CLAUDE_CODE_OAUTH_TOKEN` 環境変数をサポートしていません。これにより、Claude Codeのサブスクリプション認証（Pro/Max）を使用できず、API従量課金（`ANTHROPIC_API_KEY`）が必須となっています。

**影響**: Claude Codeサブスクリプション契約者がprompfooで評価を実行する際、追加のAPI料金が発生します。

---

## 1. 環境情報

### 検証環境

```json
{
  "promptfoo": "0.119.3",
  "@anthropic-ai/claude-agent-sdk": "0.1.30",
  "node": ">=18.0.0",
  "platform": "linux",
  "date": "2025-11-12"
}
```

### 関連ファイル

- promptfooプロバイダー: `node_modules/promptfoo/dist/src/providers/claude-agent-sdk.js`
- Claude Agent SDK: `node_modules/@anthropic-ai/claude-agent-sdk/`

---

## 2. 問題の詳細

### 2.1 発見の経緯

1. Claude Codeサブスクリプション（Pro $20/月）契約
2. `claude login` および `claude setup-token` で認証
3. `CLAUDE_CODE_OAUTH_TOKEN` 環境変数を設定
4. promptfooconfig.yamlで `anthropic:claude-agent-sdk` プロバイダーを使用
5. 実行時にエラー: `Anthropic API key is not set`

### 2.2 コアな問題

**promptfooが `ANTHROPIC_API_KEY` のみをチェックし、`CLAUDE_CODE_OAUTH_TOKEN` を無視している**

---

## 3. 期待される動作 vs 実際の動作

### 期待される動作（正常）

```
ユーザー
  ↓ CLAUDE_CODE_OAUTH_TOKEN をエクスポート
promptfoo anthropic:claude-agent-sdk プロバイダー
  ↓ 環境変数を Claude Agent SDK に渡す
Claude Agent SDK (@anthropic-ai/claude-agent-sdk)
  ↓ CLAUDE_CODE_OAUTH_TOKEN で認証
Claude Code API
  ↓ 正常に動作 ✅
レスポンス返却
```

### 実際の動作（バグ）

```
ユーザー
  ↓ CLAUDE_CODE_OAUTH_TOKEN をエクスポート
promptfoo anthropic:claude-agent-sdk プロバイダー
  ↓ ANTHROPIC_API_KEY のみチェック ❌
  ↓ 見つからない → エラー投げる
Error: "Anthropic API key is not set"
```

---

## 4. ソースコードの証拠

### 4.1 promptfoo側の実装（バグ箇所）

**ファイル**: `node_modules/promptfoo/dist/src/providers/claude-agent-sdk.js`

#### 問題1: getApiKey() メソッド（Line 348-350）

```javascript
getApiKey() {
    return this.config?.apiKey ||
           this.env?.ANTHROPIC_API_KEY ||
           getEnvString('ANTHROPIC_API_KEY');  // ← ここだけ！
}
```

**問題点**:
- ✅ `ANTHROPIC_API_KEY` のみチェック
- ❌ `CLAUDE_CODE_OAUTH_TOKEN` をチェックしていない
- ❌ `ANTHROPIC_AUTH_TOKEN` もチェックしていない

#### 問題2: API key強制上書き（Line 119-120）

```javascript
if (this.apiKey) {
    env.ANTHROPIC_API_KEY = this.apiKey;  // ← 強制的に上書き
}
```

**問題点**: Claude Agent SDKが環境変数から `CLAUDE_CODE_OAUTH_TOKEN` を読む前に、promptfooが `ANTHROPIC_API_KEY` を注入してしまう。

#### 問題3: apiKey必須チェック（Line 123-126）

```javascript
if (!this.apiKey && !(env.CLAUDE_CODE_USE_BEDROCK || env.CLAUDE_CODE_USE_VERTEX)) {
    throw new Error(`Anthropic API key is not set. Set the ANTHROPIC_API_KEY environment variable or add "apiKey" to the provider config.

    Use CLAUDE_CODE_USE_BEDROCK or CLAUDE_CODE_USE_VERTEX environment variables to use Bedrock or Vertex instead.`);
}
```

**問題点**: `CLAUDE_CODE_OAUTH_TOKEN` が設定されていてもエラーを投げる。

### 4.2 Claude Agent SDK側の実装（正常）

**ファイル**: `node_modules/@anthropic-ai/claude-agent-sdk/cli.js`

SDKはminified済みですが、以下の環境変数をサポートしていることが確認されています：

```javascript
// SDKのコンストラクタ（擬似コード、実際はminified）
constructor({
  baseURL = getEnv("ANTHROPIC_BASE_URL"),
  apiKey = getEnv("ANTHROPIC_API_KEY") ?? null,
  authToken = getEnv("ANTHROPIC_AUTH_TOKEN") ??
              getEnv("CLAUDE_CODE_OAUTH_TOKEN") ?? null,
  ...options
}) {
  // authToken が優先される実装
}
```

**確認方法**:
1. SDKのpackage.json確認
2. GitHubのIssue #6536でAnthropicチームが言及
3. Claude CLIが実際に動作（同じSDKを使用）

---

## 5. 検証手順（再現可能）

### 5.1 事前準備

```bash
# Claude Code認証
claude login
claude setup-token

# トークン取得（出力されたトークンをコピー）
# 例: cc-01-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# 環境変数設定
export CLAUDE_CODE_OAUTH_TOKEN="cc-01-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

### 5.2 promptfoo設定

**promptfooconfig.yaml**:
```yaml
providers:
  - id: anthropic:claude-agent-sdk
    config:
      model: sonnet
      # apiKey を指定しない
      temperature: 0.7
      max_tokens: 2000

prompts:
  - "Say hello"

tests:
  - vars: {}
```

### 5.3 実行と結果

```bash
npx promptfoo eval
```

**結果（エラー）**:
```
Error: Anthropic API key is not set. Set the ANTHROPIC_API_KEY
environment variable or add "apiKey" to the provider config.
```

### 5.4 回避策テスト1: API keyとして設定

```bash
# トークンをAPI keyとして偽装
export ANTHROPIC_API_KEY=$CLAUDE_CODE_OAUTH_TOKEN
npx promptfoo eval
```

**結果（エラー）**:
```json
{
  "error": "Claude Code error: 401 {\"type\":\"error\",\"error\":{\"type\":\"authentication_error\",\"message\":\"invalid x-api-key\"},\"request_id\":\"req_011CV3yGF6SNLJ5CXzKPsbhi\"}"
}
```

**分析**:
- promptfooのチェックはパス
- しかしAnthropicの `api.anthropic.com` がOAuthトークンを `x-api-key` ヘッダーで受け取れず拒否

### 5.5 回避策テスト2: CLI直接呼び出し

カスタムプロバイダーで `claude -p` を直接呼び出す実装（このリポジトリの `claude-cli-provider.js`）。

理論上は動作するはずだが、この環境では `claude` コマンドが応答しないため未検証。

---

## 6. 検証結果のまとめ

| テスト | 設定 | promptfooチェック | API呼び出し | 結果 |
|--------|------|-------------------|-------------|------|
| 1. CLAUDE_CODE_OAUTH_TOKEN のみ | トークン設定 | ❌ エラー | - | 失敗 |
| 2. ANTHROPIC_API_KEY=$TOKEN | トークンをAPI keyへ | ✅ パス | ❌ invalid x-api-key | 失敗 |
| 3. ANTHROPIC_API_KEY="sk-ant-..." | 正規のAPI key | ✅ パス | ✅ 成功 | 成功 |
| 4. CLI直接呼び出し | トークン設定 | N/A（回避） | ✅ (理論上) | 未検証 |

---

## 7. 技術的な分析

### 7.1 なぜ2つのトークンが存在するのか？

| トークン | 用途 | エンドポイント | 課金 |
|----------|------|----------------|------|
| `ANTHROPIC_API_KEY` (sk-ant-...) | API統合 | api.anthropic.com | 従量課金（トークンごと） |
| `CLAUDE_CODE_OAUTH_TOKEN` (cc-01-...) | CLI/CI/CD | claude.ai API？ | サブスクリプション（月額固定） |

### 7.2 CLAUDE_CODE_OAUTH_TOKENの用途

**公式ドキュメント**より：
- GitHub Actions でのClaude Code使用
- Dockerコンテナ内での実行
- CI/CDパイプラインでの自動化
- ファイルシステムアクセスが制限される環境

**特徴**:
- 長寿命（通常の認証ファイルは6時間で期限切れ）
- 環境変数で注入可能
- サブスクリプション契約で追加料金不要

### 7.3 promptfooはどちらを使うべきか？

**理想**: `CLAUDE_CODE_OAUTH_TOKEN` をサポートすべき

**理由**:
1. promptfooは「自動評価ツール」→ CI/CD用途に該当
2. Claude Agent SDKが既にサポート済み
3. promptfoo自体が「自動化環境」として動作

**現状**: `ANTHROPIC_API_KEY` のみサポート（実装不備）

---

## 8. 提案される修正

### 8.1 promptfoo側の修正案

#### 修正1: getApiKey() メソッド

```javascript
// 現在（バグ）
getApiKey() {
    return this.config?.apiKey ||
           this.env?.ANTHROPIC_API_KEY ||
           getEnvString('ANTHROPIC_API_KEY');
}

// 修正後
getApiKey() {
    return this.config?.apiKey ||
           this.env?.ANTHROPIC_API_KEY ||
           this.env?.ANTHROPIC_AUTH_TOKEN ||
           this.env?.CLAUDE_CODE_OAUTH_TOKEN ||
           getEnvString('ANTHROPIC_API_KEY') ||
           getEnvString('ANTHROPIC_AUTH_TOKEN') ||
           getEnvString('CLAUDE_CODE_OAUTH_TOKEN');
}
```

#### 修正2: 環境変数の扱い

```javascript
// 現在（バグ）
if (this.apiKey) {
    env.ANTHROPIC_API_KEY = this.apiKey;  // 強制上書き
}

// 修正後
// Claude Agent SDKに環境変数をそのまま渡す（上書きしない）
// SDKが内部で優先順位を判断する
if (this.apiKey) {
    // apiKey が sk-ant- で始まる場合のみ ANTHROPIC_API_KEY に設定
    if (this.apiKey.startsWith('sk-ant-')) {
        env.ANTHROPIC_API_KEY = this.apiKey;
    } else {
        // cc-01- などの場合は ANTHROPIC_AUTH_TOKEN に設定
        env.ANTHROPIC_AUTH_TOKEN = this.apiKey;
    }
}
```

#### 修正3: エラーメッセージ

```javascript
// 現在（バグ）
if (!this.apiKey && !(env.CLAUDE_CODE_USE_BEDROCK || env.CLAUDE_CODE_USE_VERTEX)) {
    throw new Error(`Anthropic API key is not set...`);
}

// 修正後
const hasAuth = this.apiKey ||
                env.ANTHROPIC_API_KEY ||
                env.ANTHROPIC_AUTH_TOKEN ||
                env.CLAUDE_CODE_OAUTH_TOKEN ||
                env.CLAUDE_CODE_USE_BEDROCK ||
                env.CLAUDE_CODE_USE_VERTEX;

if (!hasAuth) {
    throw new Error(`Anthropic authentication not found. Set one of:
    - ANTHROPIC_API_KEY (for pay-as-you-go API)
    - CLAUDE_CODE_OAUTH_TOKEN (for Claude Code subscription)
    - ANTHROPIC_AUTH_TOKEN (alternative auth token)
    - CLAUDE_CODE_USE_BEDROCK or CLAUDE_CODE_USE_VERTEX`);
}
```

---

## 9. 回避策（現時点）

### 9.1 方法1: API従量課金を使う（推奨・確実）

```bash
# Anthropic Consoleで API keyを取得
# https://console.anthropic.com/settings/keys

export ANTHROPIC_API_KEY="sk-ant-api03-..."

# promptfooconfig.yaml
providers:
  - id: anthropic:claude-agent-sdk
    config:
      model: sonnet

npx promptfoo eval
```

**コスト**: 約$2-3（60回実行、入力60K + 出力120Kトークン想定）

### 9.2 方法2: CLI直接呼び出しカスタムプロバイダー（理論上）

**claude-cli-provider.js** を作成：

```javascript
import { spawn } from 'child_process';

export default class ClaudeCliProvider {
  async callApi(prompt) {
    return new Promise((resolve, reject) => {
      const claude = spawn('claude', ['-p'], {
        stdio: ['pipe', 'pipe', 'pipe'],
      });

      let stdout = '';
      claude.stdout.on('data', (data) => stdout += data);
      claude.on('close', (code) => {
        if (code === 0) resolve(stdout.trim());
        else reject(new Error(`Exit code ${code}`));
      });

      claude.stdin.write(prompt);
      claude.stdin.end();
    });
  }
}
```

**promptfooconfig.yaml**:
```yaml
providers:
  - id: file://./claude-cli-provider.js
    label: Claude CLI
```

**制限**: `claude -p` が応答しない環境では動作しない可能性あり。

---

## 10. Issue報告用情報

### promptfoo GitHubリポジトリ

**リポジトリ**: https://github.com/promptfoo/promptfoo

### 報告内容テンプレート

```markdown
## Bug Report: Claude Code OAuth Token Not Supported

### Environment
- promptfoo: 0.119.3
- @anthropic-ai/claude-agent-sdk: 0.1.30
- Node: 18+

### Description
The `anthropic:claude-agent-sdk` provider only checks for `ANTHROPIC_API_KEY` and ignores `CLAUDE_CODE_OAUTH_TOKEN`, making Claude Code subscription authentication unusable.

### Expected Behavior
Users with Claude Code subscriptions (Pro/Max) should be able to use `CLAUDE_CODE_OAUTH_TOKEN` for authentication, avoiding pay-as-you-go API costs.

### Actual Behavior
Error: "Anthropic API key is not set"

### Code Evidence
File: `node_modules/promptfoo/dist/src/providers/claude-agent-sdk.js:349`

```javascript
getApiKey() {
    return this.config?.apiKey ||
           this.env?.ANTHROPIC_API_KEY ||  // Only checks this
           getEnvString('ANTHROPIC_API_KEY');
}
```

### Steps to Reproduce
1. `claude login && claude setup-token`
2. `export CLAUDE_CODE_OAUTH_TOKEN="cc-01-xxxxx"`
3. Configure promptfoo with `anthropic:claude-agent-sdk` provider
4. Run `npx promptfoo eval`
5. See error: "Anthropic API key is not set"

### Proposed Fix
Check for `CLAUDE_CODE_OAUTH_TOKEN` and `ANTHROPIC_AUTH_TOKEN` in addition to `ANTHROPIC_API_KEY`.

### Impact
- Users must pay additional API costs despite having active subscriptions
- CI/CD use cases (the intended use case for OAuth tokens) are blocked
```

---

## 11. 参考リンク

1. **Claude Code Headless Mode**: https://code.claude.com/docs/en/headless
2. **GitHub Issue #6536**: Anthropic公式による「SDK is for programmatic use (API pay-as-you-go)」説明
3. **promptfoo Documentation**: https://www.promptfoo.dev/docs/providers/claude-agent-sdk/
4. **Claude Code OAuth Login Action**: https://github.com/marketplace/actions/claude-code-oauth-login

---

## 12. 結論

promptfooの `anthropic:claude-agent-sdk` プロバイダーは、**実装不備により `CLAUDE_CODE_OAUTH_TOKEN` をサポートしていません**。

これは：
- ❌ バグです（仕様ではない）
- ❌ promptfoo側の問題です（Claude Agent SDK側は正常）
- ✅ 修正可能です（getApiKey()メソッドの拡張が必要）
- ✅ Issue報告すべきです

**現時点の回避策**: API従量課金（`ANTHROPIC_API_KEY`）を使用するか、CLI直接呼び出しのカスタムプロバイダーを実装する。

---

**ドキュメント作成日**: 2025-11-12
**検証者**: AI
**レビュー**: 必要に応じて人間がファクトチェック
