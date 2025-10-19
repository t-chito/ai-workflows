# Development Log - n8n & Dify Dev Container Setup

## 調査フェーズ

### 2025-10-19 - 初期調査

#### n8n について

**参考情報源:**
1. **DeepWiki MCP - n8n-io/n8n リポジトリ**
   - 最小構成: 単一の Docker コンテナで動作
   - デフォルトポート: `5678`
   - データ永続化: `/home/node/.n8n` ディレクトリをマウント
   - 最小限の環境変数: 基本的には不要（デフォルトで動作）
   - 起動コマンド例:
     ```bash
     docker volume create n8n_data
     docker run -it --rm --name n8n -p 5678:5678 -v n8n_data:/home/node/.n8n docker.n8n.io/n8nio/n8n
     ```

2. **Web Search - "n8n docker compose simple setup 2025"**
   - 公式ドキュメント: https://docs.n8n.io/hosting/installation/server-setups/docker-compose/
   - Docker Compose での構成も可能
   - 推奨メモリ: 最低 2GB RAM
   - データ永続化: `./n8n_data:/home/node/.n8n` のようにホストディレクトリをマウント
   - アクセス: `http://localhost:5678`
   - 初回アクセス時に管理者アカウント作成が必要

#### Dify について

**参考情報源:**
1. **DeepWiki MCP - langgenius/dify リポジトリ**
   - 複数サービスで構成:
     - コアサービス: `api`, `worker`, `worker_beat`, `web`
     - 依存サービス: `db` (PostgreSQL), `redis`, `sandbox`, `plugin_daemon`, `ssrf_proxy`, `nginx`
   - デフォルトポート:
     - PostgreSQL: `5432`
     - Redis: `6379`
     - Sandbox: `8194`
     - Plugin Daemon: `5002`
     - SSRF Proxy: `3128`
     - Nginx: `80`, `443`
   - デプロイ方法: `docker-compose.yaml` を使用
   - 環境変数: `.env.example` から `.env` をコピーして設定

2. **Web Search - "dify docker compose self hosted setup 2025"**
   - 公式ドキュメント: https://docs.dify.ai/en/getting-started/install-self-hosted/docker-compose
   - 公式リポジトリ: https://github.com/langgenius/dify/blob/main/docker/docker-compose.yaml
   - システム要件: 最低 2 CPU コア、4 GiB RAM
   - アーキテクチャ:
     - 3つのコアサービス: api / worker / web
     - 6つの依存コンポーネント: weaviate / db / redis / nginx / ssrf_proxy / sandbox
   - セットアップ手順:
     1. リポジトリを clone: `git clone https://github.com/langgenius/dify.git --branch 0.15.3`
     2. docker ディレクトリに移動
     3. `.env.example` から `.env` をコピー
     4. `docker compose up -d` で起動
   - 初回アクセス時に `/install` インターフェースで管理者アカウント作成

#### Dev Container の構成方針

**理解した構成:**
- Dev Container 内に Docker CLI をインストール
- ホストの Docker デーモンを使用（Docker-outside-of-Docker）
- Dev Container にアタッチ後、コマンドでサービスを起動
- VSCode の Port Forwarding（トンネル）機能で外部アクセス可能

#### Dify の Docker イメージ調査

**参考情報源:**
3. **Web Search - "dify docker image docker hub official 2025"**
   - Docker Hub に公式イメージが公開されている
   - 主要イメージ:
     - `langgenius/dify-api` - API サービス
     - `langgenius/dify-web` - Web フロントエンド
     - `langgenius/dify-sandbox` - サンドボックス環境
     - `langgenius/dify-plugin-daemon` - プラグインデーモン
   - Docker Hub ページ:
     - https://hub.docker.com/r/langgenius/dify-web
     - https://hub.docker.com/r/langgenius/dify-api
     - https://hub.docker.com/r/langgenius/dify-sandbox

4. **DeepWiki MCP - Dify の Docker イメージについて**
   - すべてのイメージは Docker Hub の `langgenius` organization でホスト
   - バージョン管理されている（例: `1.9.1`, `0.2.12`）
   - docker-compose.yaml でこれらのイメージを使用
   - リポジトリを clone せずに docker-compose.yaml だけで構成可能

---

## 決定事項

### Dify の構成方針
- ✅ 公式リポジトリの `docker/docker-compose.yaml` を使用
- ✅ `.env.example` から `.env` をコピーして環境変数を設定
- ✅ Quick Start の手順に従う（シンプルで過剰ではない）
- ✅ リポジトリを clone する形で進める

### n8n の構成方針

**参考情報源:**
5. **Web Search - "n8n npx install quick start 2025"**
   - 公式ドキュメント: https://docs.n8n.io/hosting/installation/npm/
   - npx での起動も可能: `npx n8n`
   - Node.js 18+ が必要
   - メリット: インストール不要、即起動
   - デメリット: Webhook 不可、自動再起動なし、データ永続化の管理が曖昧

6. **DeepWiki MCP - n8n の npx について**
   - `npx n8n` で即座に起動可能
   - 開発モードではホットリロード対応
   - データ永続化: デフォルトではホームディレクトリの `.n8n` フォルダ
   - Docker との比較:
     - Docker: ボリュームマウントで明確にデータ管理、本番環境に近い
     - npx: シンプルだが Dev Container 削除時にデータ消失の可能性

**決定:**
- ✅ Docker を使用（Dify と統一、データ永続化が明確）
- ✅ 統合された docker-compose.yml を作成（n8n と Dify を同時起動）

---

## 実装方針

### 構成
1. **Dev Container**:
   - Docker CLI をインストール
   - ホストの Docker デーモンを使用（Docker-outside-of-Docker）
   - Git をインストール（Dify リポジトリの clone 用）

2. **Dify**:
   - 公式リポジトリを clone
   - `docker/docker-compose.yaml` と `.env` を使用

3. **n8n**:
   - 統合 docker-compose.yml に追加
   - データ永続化用のボリューム設定

4. **ポートフォワーディング**:
   - n8n: 5678
   - Dify: 80 (nginx)

---

#### Dify のファイル依存関係調査

**参考情報源:**
7. **DeepWiki MCP - Dify の必要ファイルについて**
   - docker-compose.yaml 以外に必要なファイル:
     - `.env` ファイル（`.env.example` からコピー）
     - `nginx/` ディレクトリ（nginx.conf.template, proxy.conf.template, docker-entrypoint.sh など）
     - `ssrf_proxy/` ディレクトリ（squid.conf.template, docker-entrypoint.sh）
     - `certbot/` ディレクトリ（HTTPS 用、オプション）
   - docker-compose.yaml は `docker-compose-template.yaml` から自動生成される
   - 各サービスの設定ファイルがボリュームマウントされる

8. **Web Search - "dify docker compose minimum files needed nginx config 2025"**
   - Nginx サービスには複数の設定ファイルが必要
   - 環境変数: NGINX_SERVER_NAME, NGINX_HTTPS_ENABLED など
   - カスタマイズには .env ファイルで設定を反映

**結論:**
- ❌ docker-compose.yaml だけでは動かない
- ✅ リポジトリの clone が必要（nginx, ssrf_proxy などの設定ファイルが必要）

---

## 最終決定事項

### 構成方針
1. **Dify**: 公式リポジトリを clone して `docker/` ディレクトリを使用
2. **n8n**: 統合 docker-compose.yml に追加（または別ファイル）
3. **Dev Container**: Docker CLI + Git をインストール

### docker-compose の統合について
- ✅ 統合する方向で検討（デメリットは公式と少しずれるだけ）

---

#### docker-compose.override.yml の調査

**参考情報源:**
9. **Web Search - "docker compose override.yml how to use 2025"**
   - 公式ドキュメント: https://docs.docker.com/compose/how-tos/multiple-compose-files/merge/
   - override ファイルの仕組み:
     - `docker-compose.yml` と `docker-compose.override.yml` を自動的にマージ
     - `docker compose up` で自動的に適用される
     - override ファイルの設定が優先される
   - メリット:
     - 元のファイルを変更せずに設定を追加・上書きできる
     - アップデート時に影響を受けにくい
   - 使い方: 同じディレクトリに `docker-compose.override.yml` を作成するだけ

**結論:**
- ✅ `docker-compose.override.yml` を使って n8n を追加
- ✅ Dify の公式ファイルは変更しない

---

## 最終決定事項（確定版）

### ファイル構成
```
/
├── .devcontainer/
│   └── devcontainer.json
├── dify/                              # Dify リポジトリ（Git 管理外）
│   └── docker/
│       ├── docker-compose.yaml        # 公式ファイル（変更しない）
│       ├── docker-compose.override.yml # n8n を追加（Git 管理）
│       ├── .env                       # .env.example からコピー（Git 管理外）
│       ├── nginx/                     # 公式の設定ファイル
│       └── ssrf_proxy/                # 公式の設定ファイル
├── .gitignore                         # dify/, .env を追加
├── README.md                          # セットアップ手順を記載
└── DEVELOPMENT_LOG.md
```

### Git 管理方針
- ❌ Dify リポジトリ: `.gitignore` に追加（手動 clone）
- ✅ `docker-compose.override.yml`: Git で管理
- ❌ `.env`: Git 管理外（機密情報が含まれる可能性）
- ✅ README: セットアップ手順とアップデート方法を記載

### セットアップフロー
1. Dev Container を開く
2. README の手順に従って Dify リポジトリを clone
3. `.env.example` から `.env` をコピー
4. `docker compose up -d` で起動

### ポートフォワーディング
- n8n: 5678
- Dify: 80 (nginx)

---

## Dev Container 構成方針の再検討

### 利用目的の明確化
- **主目的**: 外出先から n8n と Dify にアクセスしたい
- **手段**: Dev Container のトンネル機能を使う
- **用途**: 開発作業ではなく、単にサービスを動かしてアクセスするだけ

### 2つのアプローチの比較

#### アプローチ 1: Docker-outside-of-Docker
**構成:**
- Dev Container: Ubuntu ベースの作業用コンテナ
- Docker CLI をインストール
- コンテナ内から `docker compose up` を手動実行
- 実際のサービス（n8n, Dify）はホストの Docker で動く

**デメリット:**
- 手動で `docker compose up` を実行する必要がある
- Dev Container を開いただけではサービスは起動しない
- 自動化されていない

#### アプローチ 2: dockerComposeFile を使用（採用）
**構成:**
- `devcontainer.json` で `dockerComposeFile` を指定
- Dev Container を開くと自動的にサービスも起動
- 軽量な `workspace` コンテナを追加してアタッチ
- すべてが統合されている

**メリット:**
- ✅ Dev Container を開く = サービスも自動起動
- ✅ トンネルも自動で有効
- ✅ 手動操作不要
- ✅ 用途（外出先からアクセス）に最適

**採用理由:**
外出先からアクセスしたいという用途に対して、Dev Container を開くだけで全てが自動で立ち上がる方が圧倒的に楽。Docker-outside-of-Docker は手動操作が必要で、今回の用途には適さない。

---

## 最終決定事項（修正版）

### ファイル構成
```
/
├── .devcontainer/
│   ├── devcontainer.json                # dockerComposeFile を使用
│   └── docker-compose.override.yml      # n8n + workspace コンテナ
├── dify/                                # Dify リポジトリ（Git 管理外）
│   └── docker/
│       ├── docker-compose.yaml          # 公式ファイル（変更しない）
│       └── .env                         # .env.example からコピー（Git 管理外）
├── .gitignore                           # dify/, .env を追加
├── README.md                            # セットアップ手順を記載
└── DEVELOPMENT_LOG.md
```

### Dev Container の動作
1. VSCode で Dev Container を開く
2. 自動的に docker-compose が起動（Dify + n8n）
3. `workspace` コンテナにアタッチ（軽量な Alpine Linux）
4. トンネルが自動で有効になり、外出先からアクセス可能

### セットアップフロー（事前準備）
1. Dify リポジトリを clone: `git clone https://github.com/langgenius/dify.git`
2. `.env` をコピー: `cp dify/docker/.env.example dify/docker/.env`
3. Dev Container を開く → 自動的にサービス起動

---

## 次のステップ
- docker-compose.override.yml に workspace コンテナを追加
- devcontainer.json を修正
- README.md を修正
