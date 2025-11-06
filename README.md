# promptfoo コードレビュー評価サンプル

promptfooを使用したコードレビュープロンプトの評価サンプル実装です。

## 概要

このプロジェクトでは、5種類のコードレビュープロンプトを2つのLLMモデル（**Claude Code**、**Codex**）で評価し、最適なプロンプト設計を見つけることを目的としています。

### 評価対象

**プロンプト（5種類）:**
1. 基本レビュー - シンプルなコードレビュー依頼
2. ベストプラクティス - モデルの判断に任せるレビュー
3. リーダブルコード準拠 - リーダブルコードの原則に従ったレビュー
4. 整理後レビュー - 観点を整理してからレビュー
5. 具体的観点付き - 詳細な観点を提示してレビュー

**モデル（2種類）:**
- **Claude Code** (Anthropic Claude Agent SDK)
- **Codex** (OpenAI codex-mini-latest)

**テストケース（2個）:**
1. 変数名が不明瞭なPython関数
2. エラーハンドリングが不十分なJavaScript関数

**実行回数:**
- 各組み合わせを3回実行（出力の揺れを確認）

## セットアップ

### 1. 前提条件

- Node.js 18以上がインストールされていること
- Claude Code APIキー または Claude Pro/Maxサブスクリプション
- OpenAI APIキー または ChatGPT Plus/Proサブスクリプション

### 2. promptfooと依存関係のインストール

```bash
# プロジェクト内の依存関係をインストール
npm install

# または、グローバルインストール
npm install -g promptfoo
```

### 3. APIキーの設定

環境変数にAPIキーを設定します。

**Linux / macOS:**
```bash
# Claude Code用（CLAUDE_API_KEYまたはCLAUDE_CODE_API_KEYのいずれか）
export CLAUDE_API_KEY="your-claude-api-key"
# または
export CLAUDE_CODE_API_KEY="your-claude-code-api-key"

# Codex用
export OPENAI_API_KEY="your-openai-api-key"
```

**Windows (PowerShell):**
```powershell
$env:CLAUDE_API_KEY="your-claude-api-key"
$env:OPENAI_API_KEY="your-openai-api-key"
```

**または、.envファイルに記載（推奨）:**
```bash
# プロジェクトルートに.envファイルを作成
echo "CLAUDE_API_KEY=your-claude-api-key" >> .env
echo "OPENAI_API_KEY=your-openai-api-key" >> .env
```

> ⚠️ **注意**: .envファイルは.gitignoreに追加して、GitHubにコミットしないでください。

### 4. サブスクリプション情報

#### Claude Code
- **Pro**: $20/月（10-40プロンプト/5時間）
- **Max**: $100/月（5x Pro）または $200/月（20x Pro）
- promptfoo経由でもusage限度にカウントされます

#### Codex
- **ChatGPT Plus**: $20/月（30-150メッセージ/5時間）
- **ChatGPT Pro**: $200/月（300-1,500メッセージ/5時間）
- promptfoo経由でもusage限度にカウントされます

### 5. 代替オプション：従量課金API

サブスクリプションではなく、従量課金APIを使用することもできます：

- **Anthropic API**: Claude Sonnet 4 - $3/1M入力トークン
- **OpenAI API**: codex-mini-latest - $1.50/1M入力トークン

大量テストを行う場合は、API従量課金の方が管理しやすい場合があります。

## 実行方法

### 基本実行

```bash
# promptfoo評価を実行
promptfoo eval

# または、npxで実行
npx promptfoo@latest eval
```

### 結果の確認

#### 1. Webダッシュボードで確認（推奨）

```bash
# Webブラウザで結果を表示
promptfoo view

# または
npx promptfoo@latest view
```

ブラウザが自動的に開き、以下のような情報が確認できます：
- 各プロンプト × モデルの組み合わせの出力結果
- 3回実行した結果の比較
- 出力の揺れ（一貫性）

#### 2. JSONファイルで確認

```bash
# 結果はprompfoo-results.jsonに保存されます
cat promptfoo-results.json | jq .
```

#### 3. CSVでエクスポート

```bash
# CSVファイルとしてエクスポート
promptfoo export --output results.csv
```

## 設定ファイルの説明

### promptfooConfig.yaml

メインの設定ファイルです。以下の構造で構成されています：

```yaml
prompts:           # 5種類のプロンプト定義
providers:         # 2種類のモデル設定
tests:             # 2個のテストケース
commandLineOptions:
  repeat: 3        # 各テストを3回実行
```

### カスタマイズ方法

#### プロンプトを追加・変更

`prompts`セクションで新しいプロンプトを追加できます：

```yaml
prompts:
  - id: prompt-6-custom
    label: "カスタムプロンプト"
    config:
      type: raw
      content: |
        あなたのカスタムプロンプト

        コード:
        {{code}}
```

#### モデルを変更

`providers`セクションで使用するモデルを変更できます：

```yaml
providers:
  # Claude 3 Opusを使用
  - id: anthropic:claude-3-opus-20240229
    label: "Claude 3 Opus"
    config:
      temperature: 0.7
      max_tokens: 2000

  # GPT-3.5 Turboを使用
  - id: openai:gpt-3.5-turbo
    label: "GPT-3.5 Turbo"
    config:
      temperature: 0.7
      max_tokens: 2000
```

#### テストケースを追加

`tests`セクションで新しいコードサンプルを追加できます：

```yaml
tests:
  - description: "あなたのテストケース"
    vars:
      code: |
        // あなたのコードサンプル
        function example() {
          return "hello";
        }
      readable_code_principles: |
        1. 観点1
        2. 観点2
```

#### 実行回数を変更

`commandLineOptions.repeat`で実行回数を変更できます：

```yaml
commandLineOptions:
  repeat: 5  # 5回実行に変更
```

## 結果の分析方法

### 1. 人力評価

Webダッシュボード（`promptfoo view`）で以下を確認：

- **品質**: どのプロンプトが最も有用なレビューを生成しているか
- **一貫性**: 3回の実行で出力がどの程度安定しているか
- **モデル差**: Claude vs GPT-4でどのような違いがあるか

### 2. 定量分析（オプション）

JSONファイルから以下を計算できます：

```bash
# jqコマンドで結果を抽出
jq '.results[] | {prompt: .prompt.label, provider: .provider.label, output: .response.output}' promptfoo-results.json
```

後処理スクリプトで以下の指標を計算することも可能：
- 出力の長さ（トークン数、文字数）
- 揺れの定量化（レーベンシュタイン距離など）
- キーワードの出現頻度

## トラブルシューティング

### APIキーが認識されない

```bash
# 環境変数が設定されているか確認
echo $ANTHROPIC_API_KEY
echo $OPENAI_API_KEY

# .envファイルが正しい場所にあるか確認
ls -la .env
```

### promptfooコマンドが見つからない

```bash
# npxで直接実行
npx promptfoo@latest eval

# または、グローバルインストール
npm install -g promptfoo
```

### レート制限エラー

APIのレート制限に引っかかった場合、`promptfooConfig.yaml`に以下を追加：

```yaml
commandLineOptions:
  repeat: 3
  maxConcurrency: 1  # 並列実行数を1に制限
```

### モデルが利用できないエラー

使用するモデルへのアクセス権があるか確認してください：
- Claude 3.5 Sonnet: Anthropic APIコンソールで確認
- GPT-4: OpenAI APIでGPT-4へのアクセス権が必要

## 次のステップ

1. **評価実行**: `promptfoo eval` で評価を実行
2. **結果確認**: `promptfoo view` でWebダッシュボードを開く
3. **分析**: どのプロンプトが最も効果的かを判断
4. **最適化**: 結果を元にプロンプトをさらに改善
5. **本番適用**: 最適なプロンプトを実際のアプリケーションに適用

## 参考リソース

- [promptfoo公式ドキュメント](https://www.promptfoo.dev/)
- [promptfoo Configuration](https://www.promptfoo.dev/docs/configuration/)
- [promptfoo Providers](https://www.promptfoo.dev/docs/providers/)
- [リーダブルコード](https://www.oreilly.co.jp/books/9784873115658/)

## ライセンス

MIT License

## 貢献

Issue、Pull Requestを歓迎します。
