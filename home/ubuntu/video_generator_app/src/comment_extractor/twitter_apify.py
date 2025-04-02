"""
X(Twitter)からコメントを抽出するモジュール（Apify版）
"""
import re
import logging
import json
from typing import Dict, List, Optional, Any
from apify_client import ApifyClient

logger = logging.getLogger(__name__)

class TwitterApifyExtractor:
    """Apifyを使用してX(Twitter)からコメントを抽出するクラス"""
    
    def __init__(self, apify_api_token: str, twitter_cookies: str):
        """初期化

        Args:
            apify_api_token: ApifyのAPIトークン
            twitter_cookies: TwitterのCookies（JSON文字列）
        """
        self.client = ApifyClient(token=apify_api_token)
        self.twitter_cookies = twitter_cookies
    
    def extract_tweet_id(self, url: str) -> str:
        """URLからツイートIDを抽出する

        Args:
            url: ツイートのURL

        Returns:
            str: ツイートID
        """
        # URLパターン: https://twitter.com/username/status/tweet_id
        # または: https://x.com/username/status/tweet_id
        pattern = r'https?://(?:twitter\.com|x\.com)/[^/]+/status/(\d+)'
        match = re.search(pattern, url)
        
        if not match:
            raise ValueError(f"Invalid Twitter/X URL: {url}")
        
        return match.group(1)
    
    def extract_username(self, url: str) -> str:
        """URLからユーザー名を抽出する

        Args:
            url: ツイートのURL

        Returns:
            str: ユーザー名
        """
        # URLパターン: https://twitter.com/username/status/tweet_id
        # または: https://x.com/username/status/tweet_id
        pattern = r'https?://(?:twitter\.com|x\.com)/([^/]+)/status/\d+'
        match = re.search(pattern, url)
        
        if not match:
            raise ValueError(f"Invalid Twitter/X URL: {url}")
        
        return match.group(1)
    
    def run_actor(self, tweet_url: str, max_replies: Optional[int] = None) -> List[Dict]:
        """Apifyアクターを実行してツイートとリプライを取得する

        Args:
            tweet_url: ツイートのURL
            max_replies: 取得する返信の最大数（Noneの場合は制限なし）

        Returns:
            List[Dict]: ツイートとリプライのリスト
        """
        try:
            # Apifyアクターの実行
            run_input = {
                "tweetUrl": tweet_url,
                "cookie": self.twitter_cookies,
                "maxItems": max_replies if max_replies else 100,
                "delay": {
                    "min": 1,
                    "max": 3
                }
            }
            
            # アクターを実行
            run = self.client.actor("curious_coder/twitter-replies-scraper").call(run_input=run_input)
            
            # 結果を取得
            items = []
            for item in self.client.dataset(run["defaultDatasetId"]).iterate_items():
                items.append(item)
            
            return items
        
        except Exception as e:
            logger.error(f"Error running Apify actor: {e}")
            raise
    
    def format_tweet_data(self, tweet: Dict) -> Dict:
        """ツイートデータを整形する

        Args:
            tweet: ツイートデータ

        Returns:
            Dict: 整形されたツイートデータ
        """
        # Apifyから返されるデータ形式に合わせて整形
        return {
            "text": tweet.get("full_text", ""),
            "user": tweet.get("user", {}).get("legacy", {}).get("screen_name", ""),
            "name": tweet.get("user", {}).get("legacy", {}).get("name", ""),
            "created_at": tweet.get("created_at", ""),
            "id": tweet.get("id_str", "")
        }
    
    def shorten_intro(self, intro_text: str, max_duration_seconds: int = 25, words_per_second: float = 3.0) -> str:
        """イントロテキストを指定の長さに短縮する

        Args:
            intro_text: 元のイントロテキスト
            max_duration_seconds: 最大の音声時間（秒）
            words_per_second: 1秒あたりの単語数の目安

        Returns:
            str: 短縮されたイントロテキスト
        """
        # 日本語の場合は文字数で計算する（おおよそ1秒あたり3〜4文字）
        max_chars = int(max_duration_seconds * words_per_second)
        
        if len(intro_text) <= max_chars:
            return intro_text
        
        # 文単位で区切る
        sentences = re.split(r'([。．！？])', intro_text)
        sentences = [''.join(i) for i in zip(sentences[0::2], sentences[1::2] + [''])]
        
        shortened_text = ""
        for sentence in sentences:
            if len(shortened_text + sentence) <= max_chars:
                shortened_text += sentence
            else:
                break
        
        # 最後に「...」を追加
        if shortened_text != intro_text:
            shortened_text = shortened_text.rstrip() + "..."
        
        return shortened_text
    
    def extract_comments(self, url: str, max_replies: Optional[int] = None, shorten_intro: bool = True) -> Dict:
        """X(Twitter)からコメントを抽出する

        Args:
            url: ツイートのURL
            max_replies: 取得する返信の最大数（Noneの場合は制限なし）
            shorten_intro: イントロを短縮するかどうか

        Returns:
            Dict: 抽出されたコメント情報
                {
                    "title": "ツイート内容",
                    "intro_text": "元ツイートのテキスト",
                    "comments": [
                        {"text": "コメント1", "user": "ユーザー名", "name": "表示名"},
                        {"text": "コメント2", "user": "ユーザー名", "name": "表示名"},
                        ...
                    ]
                }
        """
        # Apifyアクターを実行してツイートとリプライを取得
        items = self.run_actor(url, max_replies)
        
        if not items:
            logger.warning(f"No tweets found for URL: {url}")
            return {
                "title": "",
                "intro_text": "",
                "comments": []
            }
        
        # 元ツイートとリプライを分離
        original_tweet = None
        replies = []
        
        for item in items:
            # in_reply_to_status_id_strがNoneの場合は元ツイート
            if not item.get("in_reply_to_status_id_str"):
                original_tweet = item
            else:
                replies.append(item)
        
        # 元ツイートが見つからない場合は最初のツイートを使用
        if not original_tweet and items:
            original_tweet = items[0]
            replies = items[1:]
        
        # 元ツイートの情報を取得
        tweet_data = self.format_tweet_data(original_tweet) if original_tweet else {"text": "", "user": "", "name": ""}
        
        # 返信を整形
        comments = [self.format_tweet_data(reply) for reply in replies]
        
        # イントロテキスト（元ツイート）
        intro_text = tweet_data["text"]
        
        # イントロの短縮
        if shorten_intro and intro_text:
            intro_text = self.shorten_intro(intro_text)
        
        return {
            "title": intro_text[:50] + "..." if len(intro_text) > 50 else intro_text,
            "intro_text": intro_text,
            "comments": comments
        }
