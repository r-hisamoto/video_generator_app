"""
X(Twitter)コメント抽出のテスト用スクリプト
"""
import os
import sys
import logging
import json

# ロギングの設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# プロジェクトのルートディレクトリをパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 設定の読み込み
from src.config import Config

# コメント抽出モジュールをインポート
from src.comment_extractor import create_extractor, detect_platform

def test_twitter_extraction(url: str, max_replies: int = None):
    """X(Twitter)からコメントを抽出するテスト

    Args:
        url: ツイートのURL
        max_replies: 取得する返信の最大数
    """
    try:
        # プラットフォームを検出
        platform = detect_platform(url)
        logger.info(f"Detected platform: {platform}")
        
        # エクストラクタを作成
        extractor = create_extractor(
            platform,
            api_key=Config.TWITTER_API_KEY,
            api_secret=Config.TWITTER_API_SECRET,
            access_token=Config.TWITTER_ACCESS_TOKEN,
            access_secret=Config.TWITTER_ACCESS_SECRET
        )
        
        # コメントを抽出
        logger.info(f"Extracting comments from: {url}")
        result = extractor.extract_comments(url, max_comments=max_replies)
        
        # 結果を表示
        logger.info(f"Title: {result['title']}")
        logger.info(f"Intro text: {result['intro_text']}")
        logger.info(f"Number of comments: {len(result['comments'])}")
        
        # 結果をJSONファイルに保存
        output_file = "twitter_extraction_result.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Results saved to: {output_file}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error in test_twitter_extraction: {e}")
        raise

if __name__ == "__main__":
    # テスト用のURLを指定
    test_url = "https://twitter.com/username/status/1234567890"
    
    # コマンドライン引数からURLを取得（指定されている場合）
    if len(sys.argv) > 1:
        test_url = sys.argv[1]
    
    # テスト実行
    test_twitter_extraction(test_url, max_replies=10)
