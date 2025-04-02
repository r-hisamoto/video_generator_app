"""
5chスクレイピングのテスト用スクリプト
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

# コメント抽出モジュールをインポート
from src.comment_extractor import create_extractor, detect_platform

def test_5ch_extraction(url: str, max_comments: int = None):
    """5chスレッドからコメントを抽出するテスト

    Args:
        url: 5chスレッドのURL
        max_comments: 抽出するコメントの最大数
    """
    try:
        # プラットフォームを検出
        platform = detect_platform(url)
        logger.info(f"Detected platform: {platform}")
        
        # エクストラクタを作成
        extractor = create_extractor(platform)
        
        # コメントを抽出
        logger.info(f"Extracting comments from: {url}")
        result = extractor.extract_comments(url, max_comments=max_comments)
        
        # 結果を表示
        logger.info(f"Title: {result['title']}")
        logger.info(f"Intro text: {result['intro_text']}")
        logger.info(f"Number of comments: {len(result['comments'])}")
        
        # 結果をJSONファイルに保存
        output_file = "5ch_extraction_result.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Results saved to: {output_file}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error in test_5ch_extraction: {e}")
        raise

if __name__ == "__main__":
    # テスト用のURLを指定
    test_url = "https://mi.5ch.net/test/read.cgi/news4vip/1616123456/"
    
    # コマンドライン引数からURLを取得（指定されている場合）
    if len(sys.argv) > 1:
        test_url = sys.argv[1]
    
    # テスト実行
    test_5ch_extraction(test_url, max_comments=20)
