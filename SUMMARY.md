# 実装サマリー

## やったこと

promptfooでClaude CodeとCodexのサブスクリプションを使ってコードレビュープロンプトを評価できるようにしました。

## 作成ファイル

### 1. promptfooconfig.yaml
- 5種類のコードレビュープロンプト
- 2つのモデル（Claude Code、Codex）
- 2つのテストケース（Python、JavaScript）
- 各3回実行（出力の揺れ確認用）

### 2. codex-provider.js
Codex CLIを呼び出すカスタムプロバイダー。
promptfooが標準でCodexをサポートしていないため実装。

```javascript
// codex exec - でCLI呼び出し
// stdin経由でプロンプト送信
// サブスクリプション認証を使用
```

### 3. package.json
promptfoo + Claude Agent SDK

## 認証方式

### Claude Code ✅
- サブスクリプション対応済み
- `claude setup-token` → `CLAUDE_CODE_OAUTH_TOKEN`

### Codex ✅
- カスタムプロバイダー経由
- `codex auth` → 自動認証

## 使い方

```bash
# 1. インストール
npm install

# 2. 認証
claude login && claude setup-token
export CLAUDE_CODE_OAUTH_TOKEN="your-token"
codex auth

# 3. 実行
npx promptfoo eval
npx promptfoo view
```

## 料金

サブスクリプション使用（追加課金なし）:
- Claude Pro/Max: $20-200/月
- ChatGPT Plus/Pro: $20-200/月
