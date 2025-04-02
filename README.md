# 5ch/X コメント抽出・動画生成アプリ

## 概要

このアプリケーションは、5chのスレッドやX(Twitter)の投稿・スレッドURLを入力すると、そのコメントを抽出・音声合成し、画像を背景にスライド形式で動画を生成するWEBアプリケーションです。

## 主な機能

- **コメント抽出機能**: 5chスレッドURLまたはX(Twitter)の投稿URLからコメントを自動抽出
- **音声合成機能**: OpenAI gpt-4o-mini-tts または fish.audio による高品質な音声ナレーション生成
- **画像検索機能**: Google画像検索を利用した関連画像の自動ダウンロードとフィルタ適用
- **動画生成機能**: 抽出したコメント、合成した音声、背景画像を組み合わせた動画の生成

## スクリーンショット

（実際のアプリケーション画面のスクリーンショットを追加）

## 技術スタック

- **バックエンド**: Python, FastAPI
- **フロントエンド**: HTML, JavaScript, Bootstrap
- **コメント抽出**: BeautifulSoup (5ch), Twitter API (X)
- **音声合成**: OpenAI API (gpt-4o-mini-tts), fish.audio API
- **画像検索**: Apify API (Google Images)
- **動画生成**: diffusionstudio/core

## インストール方法

### 前提条件

- Python 3.8以上
- 必要なAPIキー:
  - OpenAI API キー
  - fish.audio API キー (オプション)
  - Twitter API キー
  - Apify API キー

### インストール手順

1. リポジトリをクローン

```bash
git clone https://github.com/yourusername/video_generator_app.git
cd video_generator_app
```

2. 仮想環境を作成してアクティベート

```bash
python -m venv venv
source venv/bin/activate  # Linuxの場合
# または
venv\Scripts\activate  # Windowsの場合
```

3. 依存パッケージをインストール

```bash
pip install -r requirements.txt
```

4. 環境変数を設定

`.env`ファイルをプロジェクトのルートディレクトリに作成し、以下の内容を設定:

```
OPENAI_API_KEY=your_openai_api_key
FISH_AUDIO_API_KEY=your_fish_audio_api_key
TWITTER_API_KEY=your_twitter_api_key
TWITTER_API_SECRET=your_twitter_api_secret
TWITTER_ACCESS_TOKEN=your_twitter_access_token
TWITTER_ACCESS_SECRET=your_twitter_access_secret
APIFY_API_KEY=your_apify_api_key
```

## 使用方法

1. アプリケーションを起動

```bash
python run.py
```

2. ブラウザで http://localhost:8000 にアクセス

3. 5chスレッドまたはX(Twitter)の投稿URLを入力

4. 画面の指示に従って、コメント編集、音声合成、画像選択、動画生成を行う

5. 生成された動画をダウンロード

## 詳細なドキュメント

- [デプロイガイド](docs/deployment_guide.md) - 本番環境へのデプロイ方法
- [要件分析](docs/requirements_analysis.md) - 要件定義と設計ドキュメント

## 開発者向け情報

### プロジェクト構造

```
video_generator_app/
├── docs/                     # ドキュメント
├── src/                      # ソースコード
│   ├── comment_extractor/    # コメント抽出モジュール
│   ├── tts/                  # 音声合成モジュール
│   ├── image_search/         # 画像検索モジュール
│   ├── video_generator/      # 動画生成モジュール
│   ├── web_interface/        # WEBインターフェース
│   └── config.py             # 設定ファイル
├── static/                   # 静的ファイル
│   ├── images/               # 画像ファイル
│   ├── audio/                # 音声ファイル
│   └── videos/               # 動画ファイル
├── templates/                # HTMLテンプレート
├── tests/                    # テストコード
├── .env                      # 環境変数（gitignore対象）
├── requirements.txt          # 依存パッケージリスト
└── run.py                    # アプリケーション起動スクリプト
```

### テスト実行

```bash
# 5chコメント抽出のテスト
python tests/test_5ch_extractor.py

# X(Twitter)コメント抽出のテスト
python tests/test_twitter_extractor.py

# OpenAI TTSのテスト
python tests/test_openai_tts.py

# fish.audio TTSのテスト
python tests/test_fish_audio_tts.py

# 話者管理機能のテスト
python tests/test_speaker_manager.py

# Google画像検索のテスト
python tests/test_google_image_search.py

# 動画生成のテスト
python tests/test_video_generator.py
```

## ライセンス

MIT

## 謝辞

- [diffusionstudio/core](https://github.com/dylanler/agentic_video_generator) - 動画生成の基盤として使用
- [OpenAI](https://openai.com/) - 音声合成技術の提供
- [fish.audio](https://fish.audio/) - 音声合成技術の提供
- [Apify](https://apify.com/) - Google画像検索APIの提供
