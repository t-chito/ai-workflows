# promptfoo コードレビュー評価

promptfooを使ったコードレビューの評価サンプル

## 使い方

```bash
# インストール
npm install

# 認証（サブスクリプション - 推奨）
# Claude Code の場合
claude login
claude setup-token
export CLAUDE_CODE_OAUTH_TOKEN="<token>"

# Codex の場合
codex auth

# または API従量課金
export ANTHROPIC_API_KEY="sk-ant-..."
export OPENAI_API_KEY="sk-..."

# 実行
npx promptfoo eval
npx promptfoo view
```

## ファイル

- `promptfooconfig.yaml`: promptfoo設定（5プロンプト × 2モデル × 2テストケース × 3回実行）
- `claude-code-provider.js`: Claude Code カスタムプロバイダー（サブスクリプション認証対応）
- `codex-provider.js`: Codex カスタムプロバイダー（サブスクリプション認証対応）
