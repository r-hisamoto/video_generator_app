# 5ch/X コメント抽出・動画生成アプリ デプロイ手順書

## 1. 概要

このドキュメントでは、5ch/X コメント抽出・動画生成アプリケーションのデプロイ手順について説明します。このアプリケーションは、5chのスレッドやX(Twitter)の投稿・スレッドURLからコメントを抽出し、音声合成と画像を組み合わせて動画を生成するWEBアプリケーションです。

## 2. 前提条件

### 2.1 システム要件

- OS: Ubuntu 20.04 LTS 以上
- Python: 3.8 以上
- メモリ: 最低4GB（推奨8GB以上）
- ストレージ: 最低10GB（動画生成量に応じて増加）
- インターネット接続

### 2.2 必要なAPIキー

以下のAPIキーを取得し、環境変数またはconfigファイルに設定する必要があります：

- OpenAI API キー（gpt-4o-mini-tts用）
- fish.audio API キー（オプション）
- Twitter API キー（X API連携用）
- Apify API キー（Google画像検索用）

## 3. インストール手順

### 3.1 リポジトリのクローン

```bash
git clone https://github.com/yourusername/video_generator_app.git
cd video_generator_app
```

### 3.2 仮想環境の作成とアクティベーション

```bash
python -m venv venv
source venv/bin/activate  # Linuxの場合
# または
venv\Scripts\activate  # Windowsの場合
```

### 3.3 依存パッケージのインストール

```bash
pip install -r requirements.txt
```

### 3.4 環境変数の設定

`.env`ファイルをプロジェクトのルートディレクトリに作成し、以下の内容を設定します：

```
OPENAI_API_KEY=your_openai_api_key
FISH_AUDIO_API_KEY=your_fish_audio_api_key
TWITTER_API_KEY=your_twitter_api_key
TWITTER_API_SECRET=your_twitter_api_secret
TWITTER_ACCESS_TOKEN=your_twitter_access_token
TWITTER_ACCESS_SECRET=your_twitter_access_secret
APIFY_API_KEY=your_apify_api_key
```

## 4. アプリケーションの起動

### 4.1 開発環境での起動

```bash
python run.py --debug
```

アプリケーションは http://localhost:8000 でアクセスできます。

### 4.2 本番環境での起動

#### systemdサービスとして実行（推奨）

1. サービス定義ファイルの作成

```bash
sudo nano /etc/systemd/system/video-generator.service
```

以下の内容を記述：

```
[Unit]
Description=5ch/X Comment Video Generator
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/path/to/video_generator_app
ExecStart=/path/to/video_generator_app/venv/bin/python /path/to/video_generator_app/run.py
Restart=always
RestartSec=10
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=video-generator
Environment="PATH=/path/to/video_generator_app/venv/bin"
Environment="PYTHONPATH=/path/to/video_generator_app"

[Install]
WantedBy=multi-user.target
```

2. サービスの有効化と起動

```bash
sudo systemctl daemon-reload
sudo systemctl enable video-generator
sudo systemctl start video-generator
```

3. サービスのステータス確認

```bash
sudo systemctl status video-generator
```

#### Gunicornを使用した起動（高負荷対応）

1. Gunicornのインストール

```bash
pip install gunicorn
```

2. Gunicornでの起動

```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker src.web_interface.app:app -b 0.0.0.0:8000
```

## 5. Nginxを使用したリバースプロキシ設定（オプション）

1. Nginxのインストール

```bash
sudo apt update
sudo apt install nginx
```

2. Nginxの設定

```bash
sudo nano /etc/nginx/sites-available/video-generator
```

以下の内容を記述：

```
server {
    listen 80;
    server_name your_domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /path/to/video_generator_app/static;
    }
}
```

3. 設定の有効化

```bash
sudo ln -s /etc/nginx/sites-available/video-generator /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 6. セキュリティ設定

### 6.1 ファイアウォールの設定

```bash
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### 6.2 SSL/TLSの設定（Let's Encrypt）

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your_domain.com
```

## 7. メンテナンス

### 7.1 ログの確認

```bash
sudo journalctl -u video-generator
```

### 7.2 一時ファイルのクリーンアップ

以下のようなcronジョブを設定して、古い一時ファイルを定期的に削除します：

```bash
crontab -e
```

以下の行を追加：

```
0 3 * * * find /path/to/video_generator_app/static/temp -type f -mtime +7 -delete
0 3 * * * find /path/to/video_generator_app/static/videos -type f -mtime +7 -delete
```

## 8. トラブルシューティング

### 8.1 アプリケーションが起動しない場合

- ログを確認: `sudo journalctl -u video-generator`
- 環境変数が正しく設定されているか確認
- 依存パッケージが正しくインストールされているか確認

### 8.2 動画生成に失敗する場合

- ディスク容量を確認
- メモリ使用量を確認
- APIキーが有効か確認
- 一時ファイルディレクトリのパーミッションを確認

### 8.3 パフォーマンスの問題

- Gunicornのワーカー数を調整
- 画像・動画の一時ファイルを定期的にクリーンアップ
- サーバーのリソース（CPU、メモリ）を増強

## 9. バックアップと復元

### 9.1 設定のバックアップ

```bash
cp .env .env.backup
```

### 9.2 データベースのバックアップ（将来的に実装する場合）

```bash
# SQLiteの場合
cp database.db database.db.backup

# PostgreSQLの場合
pg_dump -U username dbname > backup.sql
```

## 10. アップグレード手順

```bash
cd /path/to/video_generator_app
git pull
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart video-generator
```
