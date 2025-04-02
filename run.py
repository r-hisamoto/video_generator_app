"""
アプリケーション起動スクリプト
"""
import os
import sys
import logging
import argparse
from pathlib import Path

# ロギングの設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# プロジェクトのルートディレクトリをパスに追加
project_root = Path(__file__).parent.absolute()
sys.path.append(str(project_root))

# 必要なディレクトリを作成
def create_directories():
    """アプリケーションに必要なディレクトリを作成する"""
    directories = [
        "static/images",
        "static/audio",
        "static/videos",
        "static/temp"
    ]
    
    for directory in directories:
        dir_path = project_root / directory
        dir_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"ディレクトリを作成しました: {dir_path}")

# 環境変数の設定
def setup_environment():
    """環境変数を設定する"""
    # 設定ファイルから環境変数を読み込む（存在する場合）
    env_file = project_root / ".env"
    if env_file.exists():
        logger.info(f"環境変数ファイルを読み込みます: {env_file}")
        with open(env_file, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    key, value = line.split("=", 1)
                    os.environ[key] = value
                    logger.info(f"環境変数を設定しました: {key}")

# アプリケーションの起動
def start_application(host="0.0.0.0", port=8000, debug=False):
    """アプリケーションを起動する"""
    from src.web_interface.app import app
    import uvicorn
    
    logger.info(f"アプリケーションを起動します: http://{host}:{port}")
    uvicorn.run(app, host=host, port=port, debug=debug)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="5ch/X コメント抽出・動画生成アプリ")
    parser.add_argument("--host", default="0.0.0.0", help="ホストアドレス")
    parser.add_argument("--port", type=int, default=8000, help="ポート番号")
    parser.add_argument("--debug", action="store_true", help="デバッグモードで実行")
    
    args = parser.parse_args()
    
    # 初期化処理
    create_directories()
    setup_environment()
    
    # アプリケーション起動
    start_application(args.host, args.port, args.debug)
