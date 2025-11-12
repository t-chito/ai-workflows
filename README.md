# promptfoo コードレビュー評価

promptfooを使ったコードレビューの評価サンプル

## 使い方

```bash
# インストール
npm install

# 認証（サブスクリプション - 推奨）
# Claude の場合
claude login

# Codex の場合
codex auth

# 実行
npx promptfoo eval
npx promptfoo view
```

## ファイル

- `promptfooconfig.yaml`: promptfoo設定（5プロンプト × 2モデル × 2テストケース × 3回実行）
- `claude-cli-provider.js`: Claude CLIカスタムプロバイダー（サブスクリプション認証対応）
- `codex-provider.js`: Codexカスタムプロバイダー（サブスクリプション認証対応）

## 実装方法

両モデルとも**CLIコマンドを直接呼び出す**ことでサブスクリプション認証を実現：

- Claude: `claude -p` (headless mode)
- Codex: `codex exec -`

認証情報はCLIが保存するため、環境変数は不要。

## 重要な注意

**SDKを使う場合の制限**

promptfoo組み込みの `anthropic:messages` プロバイダー（SDK経由）では、`CLAUDE_CODE_OAUTH_TOKEN` を設定しても `OAuth authentication is currently not supported` エラーが発生します。

詳細は [AUTHENTICATION_INVESTIGATION.md](./AUTHENTICATION_INVESTIGATION.md) を参照。
