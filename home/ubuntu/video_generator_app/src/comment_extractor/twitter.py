"""
X(Twitter)からコメントを抽出するモジュール
"""
import tweepy
import re
import logging
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

class TwitterExtractor:
    """X(Twitter)からコメントを抽出するクラス"""
    
    def __init__(self, api_key: str, api_secret: str, access_token: str, access_secret: str):
        """初期化

        Args:
            api_key: Twitter API Key
            api_secret: Twitter API Secret
            access_token: Twitter Access Token
            access_secret: Twitter Access Secret
        """
        self.auth = tweepy.OAuth1UserHandler(
            api_key, api_secret, access_token, access_secret
        )
        self.api = tweepy.API(self.auth)
    
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
    
    def get_tweet(self, tweet_id: str) -> Dict:
        """ツイートを取得する

        Args:
            tweet_id: ツイートID

        Returns:
            Dict: ツイート情報
        """
        try:
            tweet = self.api.get_status(tweet_id, tweet_mode='extended')
            return tweet._json
        except tweepy.TweepyException as e:
            logger.error(f"Error fetching tweet: {e}")
            raise
    
    def get_replies(self, tweet_id: str, username: str, max_replies: Optional[int] = None) -> List[Dict]:
        """ツイートへの返信を取得する

        Args:
            tweet_id: ツイートID
            username: ツイート投稿者のユーザー名
            max_replies: 取得する返信の最大数（Noneの場合は制限なし）

        Returns:
            List[Dict]: 返信ツイートのリスト
        """
        replies = []
        
        try:
            # 検索クエリを構築（to:username）
            query = f"to:{username}"
            
            # 返信を検索
            for tweet in tweepy.Cursor(self.api.search_tweets, q=query, since_id=tweet_id, 
                                      tweet_mode='extended').items(max_replies or 100):
                # 元のツイートへの返信かどうかを確認
                if tweet.in_reply_to_status_id_str == tweet_id:
                    replies.append(tweet._json)
                
                # 最大数に達したら終了
                if max_replies and len(replies) >= max_replies:
                    break
                    
            return replies
            
        except tweepy.TweepyException as e:
            logger.error(f"Error fetching replies: {e}")
            raise
    
    def format_tweet_data(self, tweet: Dict) -> Dict:
        """ツイートデータを整形する

        Args:
            tweet: ツイートデータ

        Returns:
            Dict: 整形されたツイートデータ
        """
        return {
            "text": tweet.get("full_text", tweet.get("text", "")),
            "user": tweet.get("user", {}).get("screen_name", ""),
            "name": tweet.get("user", {}).get("name", ""),
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
        tweet_id = self.extract_tweet_id(url)
        tweet = self.get_tweet(tweet_id)
        
        # 元ツイートの情報を取得
        tweet_data = self.format_tweet_data(tweet)
        username = tweet_data["user"]
        
        # 返信を取得
        replies_data = self.get_replies(tweet_id, username, max_replies)
        
        # 返信を整形
        comments = [self.format_tweet_data(reply) for reply in replies_data]
        
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