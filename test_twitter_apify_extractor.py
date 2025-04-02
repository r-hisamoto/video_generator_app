"""
Apifyを使用したTwitter抽出のテスト
"""
import os
import sys
import json
from dotenv import load_dotenv

# プロジェクトのルートディレクトリをパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.comment_extractor import create_extractor
from src.config import Config

def test_twitter_apify_extractor():
    """TwitterApifyExtractorのテスト"""
    
    # テスト用のツイートURL
    tweet_url = "https://twitter.com/elonmusk/status/1778156306347868371"  # 適当なツイートURLに変更してください
    
    # Apify用のエクストラクタを作成
    extractor = create_extractor(
        'twitter_apify',
        apify_api_token=Config.APIFY_API_KEY,
        twitter_cookies=Config.TWITTER_COOKIES
    )
    
    # コメントを抽出
    print(f"Extracting comments from: {tweet_url}")
    result = extractor.extract_comments(tweet_url, max_comments=5)
    
    # 結果を表示
    print("\nExtracted data:")
    print(f"Title: {result['title']}")
    print(f"Intro text: {result['intro_text']}")
    print(f"Number of comments: {len(result['comments'])}")
    
    # コメントの詳細を表示
    for i, comment in enumerate(result['comments']):
        print(f"\nComment {i+1}:")
        print(f"User: @{comment['user']} ({comment['name']})")
        print(f"Text: {comment['text']}")

if __name__ == "__main__":
    # 環境変数の読み込み
    load_dotenv()
    
    # APIキーとCookiesの確認
    if not Config.APIFY_API_KEY:
        print("Error: APIFY_API_KEY is not set in .env file")
        sys.exit(1)
    
    if Config.TWITTER_COOKIES == '{}':
        print("Error: TWITTER_COOKIES is not set in .env file")
        sys.exit(1)
    
    # テスト実行
    test_twitter_apify_extractor()
