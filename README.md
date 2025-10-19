# AI Workflows

n8n と Dify を Dev Container で動かす環境

## 概要

外出先から n8n と Dify にアクセスするための環境です。Dev Container のトンネル機能を使って、自動的にサービスを起動します。

## セットアップ（初回のみ）

### 1. Dify リポジトリを clone

```bash
git clone https://github.com/langgenius/dify.git
```

### 2. 環境設定ファイルをコピー

```bash
cp dify/docker/.env.example dify/docker/.env
```

必要に応じて `dify/docker/.env` を編集してください（API キーなど）。

### 3. Dev Container を開く

VSCode でこのプロジェクトを開き、「Dev Container で再度開く」を選択します。

**自動的に以下が実行されます:**
- Dify のすべてのサービスが起動
- n8n が起動
- ポート 5678（n8n）と 80（Dify）がフォワーディングされる

## アクセス

- **n8n**: http://localhost:5678
- **Dify**: http://localhost

初回アクセス時にそれぞれ管理者アカウントを作成してください。

## 使い方

### サービスの起動

Dev Container を開くだけで自動的に起動します。

### サービスの停止

Dev Container を閉じるとサービスも停止します。

### Dify のアップデート

```bash
cd dify
git pull
```

その後、Dev Container を再起動してください。

## トラブルシューティング

### ポートが既に使用されている

ホストマシンで 5678 または 80 番ポートを使用している場合は、該当するサービスを停止してください。

### データの永続化

- **n8n**: `n8n_data` という名前の Docker ボリュームにデータが保存されます
- **Dify**: `dify/docker/volumes/` ディレクトリにデータが保存されます

### Dev Container が起動しない

`dify/docker/.env` ファイルが存在することを確認してください。

## 構成

- **Dev Container**: 軽量な Alpine Linux コンテナ（workspace）
- **docker-compose**: Dify の公式設定 + n8n を追加（override）
- **トンネル**: VSCode の Port Forwarding 機能

詳細は [DEVELOPMENT_LOG.md](DEVELOPMENT_LOG.md) を参照してください。

## 参考

- [n8n Documentation](https://docs.n8n.io/)
- [Dify Documentation](https://docs.dify.ai/)
