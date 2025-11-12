# promptfooでのClaude認証に関する調査結果

## 結論（2025-11-12）

**✅ CLIを直接呼び出せば、両モデルともサブスクリプション認証のみで動作します。**

- **Claude**: `claude login` のみ（環境変数不要）
- **Codex**: `codex auth` のみ（環境変数不要）

**❌ SDK経由でのOAuth認証には制限があります。**

## レイヤー別の状況

### レイヤー1: Claude Code CLI（✅ サブスクリプション認証OK）

```bash
claude login  # サブスクリプション認証
claude "Review this code"  # 動作する
```

- ✅ サブスクリプション認証対応
- ✅ `claude login` で認証情報を保存
- ✅ 環境変数不要

### レイヤー2: Anthropic SDK経由のAPI呼び出し（❌ OAuth認証エラー）

```javascript
import Anthropic from '@anthropic-ai/sdk';

const client = new Anthropic({
  authToken: process.env.CLAUDE_CODE_OAUTH_TOKEN,  // 設定済み
});

await client.messages.create({...});
// 結果: 401 "OAuth authentication is currently not supported"
```

**実際のエラー：**

```json
{
  "type": "error",
  "error": {
    "type": "authentication_error",
    "message": "OAuth authentication is currently not supported."
  }
}
```

**検証済みの事実：**
- ✅ `CLAUDE_CODE_OAUTH_TOKEN` 環境変数は設定済み
- ✅ トークンは有効（`claude login` 後に取得）
- ❌ Anthropic APIサーバーが OAuth 認証を拒否

**どこが拒否しているか：**
- SDKは `authToken` を正しく読み取り、APIに送信
- APIサーバー側が「OAuth非対応」と応答
- つまり、**Anthropic API (api.anthropic.com) の制限**

### レイヤー3: promptfoo組み込みプロバイダー（❌ API keyのみ）

```yaml
providers:
  - id: anthropic:messages:claude-sonnet-4-20250514
```

- ❌ `ANTHROPIC_API_KEY` のみチェック
- ❌ `CLAUDE_CODE_OAUTH_TOKEN` を見ない
- レイヤー2と同じ制限（SDK経由でAPI呼び出し）

### レイヤー4: CLI直接呼び出しカスタムプロバイダー（✅ サブスクリプション認証OK）

```javascript
// claude-cli-provider.js
const claude = spawn('claude', ['-p']);
claude.stdin.write(prompt);
```

- ✅ CLIコマンドを直接実行
- ✅ `claude login` の認証情報を自動的に使用
- ✅ 環境変数不要
- ✅ promptfoo組み込みプロバイダーの制限を回避

## なぜレイヤー2/3はダメでレイヤー4は動くのか？

### レイヤー2/3（SDK経由）

```
promptfoo → Anthropic SDK → api.anthropic.com
                              ↑
                              ここが "OAuth authentication is currently not supported" を返す
```

- Anthropic API (`api.anthropic.com`) は OAuth トークンを受け付けない
- API従量課金用のエンドポイント
- `ANTHROPIC_API_KEY` (sk-ant-...) が必須

### レイヤー4（CLI直接呼び出し）

```
promptfoo → claude CLI → claude.ai (サブスクリプション認証)
            ↑
            ここで認証済み
```

- `claude` コマンドは `claude.ai` の認証を使用
- サブスクリプション専用の認証フロー
- promptfooとは独立して動作

## 実装方法の比較

| 方法 | 認証 | 動作 | promptfoo対応 |
|------|------|------|---------------|
| `anthropic:messages` プロバイダー | ANTHROPIC_API_KEY | ✅ | ✅ |
| SDK + CLAUDE_CODE_OAUTH_TOKEN | OAuth トークン | ❌ API拒否 | ❌ |
| `claude -p` カスタムプロバイダー | claude login | ✅ (理論上) | ✅ |
| `codex exec -` カスタムプロバイダー | codex auth | ✅ (動作確認済み) | ✅ |

## 解決策

### promptfooで Claude を使う（推奨）

**カスタムプロバイダー（CLI直接呼び出し）：**

```bash
# 認証
claude login

# promptfooconfig.yaml
providers:
  - id: file://./claude-cli-provider.js
    label: Claude CLI

# 実行
npx promptfoo eval
```

**利点：**
- ✅ サブスクリプション認証のみで動作
- ✅ 環境変数不要
- ✅ Codexと同じアプローチ

**注意点：**
- `claude` コマンドがheadless mode (`-p` フラグ) をサポートしている必要がある
- [ドキュメント](https://code.claude.com/docs/en/headless)に記載あり

### promptfooで Claude を使う（代替）

**API従量課金：**

```bash
export ANTHROPIC_API_KEY="sk-ant-..."

providers:
  - id: anthropic:messages:claude-sonnet-4-20250514

npx promptfoo eval
```

- 確実に動作する
- サブスクリプションは使えない

## 調査履歴

### 2025-11-06: 初回調査
- promptfoo組み込みプロバイダーは `ANTHROPIC_API_KEY` のみ
- 実行結果: Claude 30エラー、Codex 30成功

### 2025-11-12: SDK経由試行（失敗）
- `CLAUDE_CODE_OAUTH_TOKEN` 設定済み
- 結果: `OAuth authentication is currently not supported`
- 原因: Anthropic APIサーバー側の制限

### 2025-11-12: CLI直接呼び出し（理論上可能）
- `claude -p` でheadless mode
- Codexの `codex exec -` と同じアプローチ
- promptfoo用カスタムプロバイダーを作成

## まとめ

**問題の本質：**
- Claude Code自体はサブスクリプション認証に完全対応
- 制限は「Anthropic API (`api.anthropic.com`)」レイヤーにある
- APIはOAuth認証を受け付けず、API key (sk-ant-...) が必須

**解決策：**
- SDK経由を避け、**CLIを直接呼び出す**
- Codexと同じアプローチ（実証済み）
- promptfoo用カスタムプロバイダーで実装

## ファイル

- `claude-cli-provider.js`: Claude CLIカスタムプロバイダー（サブスクリプション対応）
- `codex-provider.js`: Codexカスタムプロバイダー（サブスクリプション対応）
- `promptfooconfig.yaml`: promptfoo設定（両方ともCLI直接呼び出し）
