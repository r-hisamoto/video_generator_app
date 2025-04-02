"""
コメント抽出モジュールのインターフェース
"""
from abc import ABC, abstractmethod
from typing import Dict, Optional

class CommentExtractor(ABC):
    """コメント抽出の基底クラス"""
    
    @abstractmethod
    def extract_comments(self, url: str, max_comments: Optional[int] = None, shorten_intro: bool = True) -> Dict:
        """コメントを抽出する抽象メソッド

        Args:
            url: コンテンツのURL
            max_comments: 抽出するコメントの最大数
            shorten_intro: イントロを短縮するかどうか

        Returns:
            Dict: 抽出されたコメント情報
        """
        pass

# 各プラットフォーム用のエクストラクタをインポート
from .five_ch import FiveChExtractor
from .twitter import TwitterExtractor
from .twitter_apify import TwitterApifyExtractor

def create_extractor(platform: str, **kwargs) -> CommentExtractor:
    """プラットフォームに応じたエクストラクタを作成する

    Args:
        platform: プラットフォーム名 ('5ch' または 'twitter' または 'twitter_apify')
        **kwargs: エクストラクタに渡す追加パラメータ

    Returns:
        CommentExtractor: コメント抽出クラスのインスタンス
    """
    if platform.lower() == '5ch':
        return FiveChExtractor()
    elif platform.lower() == 'twitter':
        required_keys = ['api_key', 'api_secret', 'access_token', 'access_secret']
        for key in required_keys:
            if key not in kwargs:
                raise ValueError(f"Twitter extractor requires '{key}' parameter")
        
        return TwitterExtractor(
            api_key=kwargs['api_key'],
            api_secret=kwargs['api_secret'],
            access_token=kwargs['access_token'],
            access_secret=kwargs['access_secret']
        )
    elif platform.lower() == 'twitter_apify':
        required_keys = ['apify_api_token', 'twitter_cookies']
        for key in required_keys:
            if key not in kwargs:
                raise ValueError(f"Twitter Apify extractor requires '{key}' parameter")
        
        return TwitterApifyExtractor(
            apify_api_token=kwargs['apify_api_token'],
            twitter_cookies=kwargs['twitter_cookies']
        )
    else:
        raise ValueError(f"Unsupported platform: {platform}")

def detect_platform(url: str, use_apify_for_twitter: bool = False) -> str:
    """URLからプラットフォームを検出する

    Args:
        url: コンテンツのURL
        use_apify_for_twitter: TwitterにApifyを使用するかどうか

    Returns:
        str: プラットフォーム名 ('5ch' または 'twitter' または 'twitter_apify')
    """
    if '5ch.net' in url:
        return '5ch'
    elif 'twitter.com' in url or 'x.com' in url:
        return 'twitter_apify' if use_apify_for_twitter else 'twitter'
    else:
        raise ValueError(f"Unsupported URL format: {url}")
