# promptfoo コードレビュー評価

promptfooを使ったコードレビューの評価サンプル

## 使い方

```bash
# インストール
npm install

# 認証
# Claude Code: API従量課金のみ（サブスクリプション非対応）
export ANTHROPIC_API_KEY="sk-ant-..."

# Codex: サブスクリプション認証対応
codex auth

# 実行
npx promptfoo eval
npx promptfoo view
```

## ファイル

- `promptfooconfig.yaml`: promptfoo設定（5プロンプト × 2モデル × 2テストケース × 3回実行）
- `codex-provider.js`: Codexカスタムプロバイダー（サブスクリプション認証対応）

## 重要な制限

**Claude Codeはサブスクリプション認証が使えません。**

- Anthropic APIが `OAuth authentication is currently not supported` を返す
- `CLAUDE_CODE_OAUTH_TOKEN` は機能しない
- API従量課金（`ANTHROPIC_API_KEY`）が必須

詳細は [AUTHENTICATION_INVESTIGATION.md](./AUTHENTICATION_INVESTIGATION.md) を参照。
