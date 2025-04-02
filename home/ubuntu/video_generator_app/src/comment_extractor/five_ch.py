"""
5chスレッドからコメントを抽出するモジュール
"""
import re
import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class FiveChExtractor:
    """5chスレッドからコメントを抽出するクラス"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def extract_thread_id_and_board(self, url: str) -> Tuple[str, str]:
        """URLからスレッドIDと板名を抽出する

        Args:
            url: 5chスレッドのURL

        Returns:
            Tuple[str, str]: スレッドIDと板名のタプル
        """
        # URLパターン: https://板名.5ch.net/test/read.cgi/カテゴリ/スレッドID/
        pattern = r'https?://([^.]+)\.5ch\.net/test/read\.cgi/([^/]+)/(\d+)'
        match = re.match(pattern, url)
        
        if not match:
            raise ValueError(f"Invalid 5ch thread URL: {url}")
        
        board_name = match.group(1)
        category = match.group(2)
        thread_id = match.group(3)
        
        return thread_id, board_name
    
    def fetch_thread_content(self, url: str) -> str:
        """スレッドのHTMLコンテンツを取得する

        Args:
            url: 5chスレッドのURL

        Returns:
            str: スレッドのHTMLコンテンツ
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            logger.error(f"Error fetching thread content: {e}")
            raise
    
    def parse_comments(self, html_content: str, max_comments: Optional[int] = None) -> Dict:
        """HTMLコンテンツからコメントを抽出する

        Args:
            html_content: スレッドのHTMLコンテンツ
            max_comments: 抽出するコメントの最大数（Noneの場合は全て）

        Returns:
            Dict: 抽出されたコメント情報
                {
                    "title": "スレッドタイトル",
                    "intro_text": "1コメ目のテキスト",
                    "comments": [
                        {"text": "コメント1", "user": "名無しさん", "number": 1},
                        {"text": "コメント2", "user": "名無しさん", "number": 2},
                        ...
                    ]
                }
        """
        soup = BeautifulSoup(html_content, 'lxml')
        
        # スレッドタイトルの抽出
        title_element = soup.select_one('h1.title')
        thread_title = title_element.text.strip() if title_element else "タイトル不明"
        
        # コメントの抽出
        comments = []
        intro_text = ""
        
        # コメント要素の選択（実際のセレクタはサイト構造に合わせて調整が必要）
        comment_elements = soup.select('div.post')
        
        for i, element in enumerate(comment_elements):
            if max_comments and i >= max_comments:
                break
                
            # コメント番号
            number_element = element.select_one('span.number')
            number = int(number_element.text.strip()) if number_element else i + 1
            
            # ユーザー名
            user_element = element.select_one('span.name')
            user = user_element.text.strip() if user_element else "名無しさん"
            
            # コメント本文
            text_element = element.select_one('div.message')
            text = text_element.text.strip() if text_element else ""
            
            comment_data = {
                "text": text,
                "user": user,
                "number": number
            }
            
            # 1コメ目はイントロとして保存
            if number == 1:
                intro_text = text
            
            comments.append(comment_data)
        
        return {
            "title": thread_title,
            "intro_text": intro_text,
            "comments": comments
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
    
    def extract_comments(self, url: str, max_comments: Optional[int] = None, shorten_intro: bool = True) -> Dict:
        """5chスレッドからコメントを抽出する

        Args:
            url: 5chスレッドのURL
            max_comments: 抽出するコメントの最大数（Noneの場合は全て）
            shorten_intro: イントロを短縮するかどうか

        Returns:
            Dict: 抽出されたコメント情報
        """
        html_content = self.fetch_thread_content(url)
        result = self.parse_comments(html_content, max_comments)
        
        # イントロの短縮
        if shorten_intro and result["intro_text"]:
            result["intro_text"] = self.shorten_intro(result["intro_text"])
        
        return result
