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

## 重要な発見

### promptfooのバグ：CLAUDE_CODE_OAUTH_TOKENが使えない

`CLAUDE_CODE_OAUTH_TOKEN` は有効なトークンですが、**promptfooの実装バグ**により使用できません。

**📋 詳細な技術レポート**: [PROMPTFOO_BUG_REPORT.md](./PROMPTFOO_BUG_REPORT.md)
（バグの証拠、検証手順、Issue報告用テンプレートを含む包括的なドキュメント）

**問題の要約**:
1. **Claude Agent SDK自体はサポート**: SDKのコードに `CLAUDE_CODE_OAUTH_TOKEN` を読み取る実装がある ✅
2. **promptfooのラッパーが非対応**: `anthropic:claude-agent-sdk` プロバイダーが `ANTHROPIC_API_KEY` しかチェックしない ❌
3. **Anthropic APIの制限**: `api.anthropic.com` がOAuth認証を受け付けない ❌

つまり、**2箇所で問題**があります：
- promptfooの実装不備（`CLAUDE_CODE_OAUTH_TOKEN` を渡さない）
- Anthropic APIサーバー側の制限（OAuth非対応）

### 現実的な解決策

- **CLI直接呼び出し**（このリポジトリの実装）
- **API従量課金**（`ANTHROPIC_API_KEY` 使用）

**参考ドキュメント**:
- **[PROMPTFOO_BUG_REPORT.md](./PROMPTFOO_BUG_REPORT.md)** - promptfooのバグ詳細レポート（Issue報告用）
- **[AUTHENTICATION_INVESTIGATION.md](./AUTHENTICATION_INVESTIGATION.md)** - 認証レイヤーの調査結果
