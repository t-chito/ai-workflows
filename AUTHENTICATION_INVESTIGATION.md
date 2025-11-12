# promptfooでのClaude Codeサブスクリプション認証に関する調査結果

## 結論

**promptfooでClaude Codeのサブスクリプション認証（`CLAUDE_CODE_OAUTH_TOKEN`）は使えません。**

API従量課金（`ANTHROPIC_API_KEY`）が必須です。

## ファクト

### 1. Claude Agent SDK (TypeScript版) の制限

**ソース**: [GitHub Issue #6536](https://github.com/anthropics/claude-code/issues/6536)

公式の説明（issue内のコメントより）：
> "The SDK is designed for programmatic use (building applications, scripts, agents, etc.). This type of usage is tied to the Anthropic API, which is billed based on token usage and requires a traditional API key."

- **サポートする環境変数**: `ANTHROPIC_API_KEY` のみ
- **サポートしない環境変数**: `CLAUDE_CODE_OAUTH_TOKEN`
- **理由**: SDKは「プログラマティックな使用」用に設計されており、API従量課金が前提

### 2. promptfooの実装

**ソース**: promptfooのソースコード `node_modules/promptfoo/dist/src/providers/claude-agent-sdk.js:349`

```javascript
getApiKey() {
    return this.config?.apiKey || this.env?.ANTHROPIC_API_KEY || getEnvString('ANTHROPIC_API_KEY');
}
```

- `ANTHROPIC_API_KEY` のみをチェック
- `CLAUDE_CODE_OAUTH_TOKEN` はチェックしていない

### 3. promptfoo公式ドキュメント

**ソース**: [promptfoo公式ドキュメント](https://www.promptfoo.dev/docs/providers/claude-agent-sdk/)

> "The easiest way to get started is with an Anthropic API key. You can set it with the ANTHROPIC_API_KEY environment variable..."

`CLAUDE_CODE_OAUTH_TOKEN` についての記載なし。

## 認証の区別

### Claude CLI（`claude`コマンド）
- ✅ サブスクリプション認証可能
- ✅ `CLAUDE_CODE_OAUTH_TOKEN` 使用可能
- 用途: インタラクティブな使用

### Claude Agent SDK（TypeScript/Python）
- ❌ サブスクリプション認証不可
- ✅ `ANTHROPIC_API_KEY` のみ
- 用途: プログラマティックな使用（API従量課金）

### promptfoo
- Claude Agent SDKを使用
- ❌ サブスクリプション認証不可
- ✅ `ANTHROPIC_API_KEY` のみ

## エラーの原因

promptfooで実行時に表示されるエラー：
```
Error: Anthropic API key is not set.
Use CLAUDE_CODE_OAUTH_TOKEN or CLAUDE_CODE_API_KEY environment variable
```

このエラーメッセージは**誤解を招く**：
- エラーメッセージには `CLAUDE_CODE_OAUTH_TOKEN` が記載されている
- しかし、実際には `ANTHROPIC_API_KEY` のみがサポートされている
- エラーメッセージはClaude Agent SDK側から来ている可能性があるが、実際には機能しない

## 実際の動作確認

promptfooで実行した結果：
- **Claude Code**: 30件すべてERROR（ANTHROPIC_API_KEYが未設定）
- **Codex**: 30件すべてPASS（カスタムプロバイダー経由で動作）

## 解決策

### promptfooでClaude Codeを使う場合

```bash
# API従量課金を使用（唯一の方法）
export ANTHROPIC_API_KEY="sk-ant-api03-..."
npx promptfoo eval
```

**料金**: 約$2-3（60回実行、入力60K + 出力120Kトークン想定）

### サブスクリプションを使いたい場合

Claude CLIを直接呼び出すカスタムスクリプトが必要：
```bash
# claude CLIなら動作する
claude login
claude "プロンプト" < code.py
```

ただし、promptfooの機能（マトリクス比較、Web UI）は使えない。

## 調査日時

2025-11-06

## 調査方法

1. promptfooのソースコード実装確認
2. Claude Agent SDK TypeScript版の動作確認
3. GitHub Issue #6536の公式コメント確認
4. promptfoo公式ドキュメント確認
5. 実際の実行結果確認（30エラー）
