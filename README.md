# promptfoo コードレビュー評価

promptfooでClaude CodeとCodexを使ってコードレビュープロンプトを評価します。

## クイックスタート

### 1. インストール

```bash
npm install
```

### 2. 認証

#### Claude Code
```bash
claude login
claude setup-token
export CLAUDE_CODE_OAUTH_TOKEN="表示されたトークン"
```

#### Codex
```bash
codex auth
```

### 3. 実行

```bash
npx promptfoo eval
npx promptfoo view
```

## 設定内容

- **プロンプト**: 5種類（基本、ベストプラクティス、リーダブルコード、整理後、具体的観点付き）
- **モデル**: Claude Code、Codex
- **テストケース**: 2個（Python、JavaScript）
- **実行回数**: 各3回

## ファイル構成

```
├── promptfooconfig.yaml    # promptfoo設定
├── codex-provider.js        # Codex用カスタムプロバイダー
├── package.json
└── README.md
```

## トラブルシューティング

### 認証エラー

```bash
# Claude Code
echo $CLAUDE_CODE_OAUTH_TOKEN  # 空なら再設定

# Codex
codex auth status
```

### promptfooが見つからない

```bash
npx promptfoo@latest eval
```

## 補足

- サブスクリプション: Claude Pro/Max ($20-200/月)、ChatGPT Plus/Pro ($20-200/月)
- 代替: API従量課金（ANTHROPIC_API_KEY、OPENAI_API_KEY）約$3
- promptfoo経由の実行もサブスクリプションの使用量にカウントされます
