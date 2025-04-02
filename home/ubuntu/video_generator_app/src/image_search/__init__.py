"""
画像検索モジュールのインターフェース
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional

class ImageSearchEngine(ABC):
    """画像検索の基底クラス"""
    
    @abstractmethod
    def search_images(self, query: str, max_images: int = 10) -> List[Dict]:
        """キーワードで画像を検索する抽象メソッド

        Args:
            query: 検索キーワード
            max_images: 取得する画像の最大数

        Returns:
            List[Dict]: 検索結果の画像情報リスト
        """
        pass
    
    @abstractmethod
    def download_images(self, image_results: List[Dict], session_id: str) -> List[str]:
        """検索結果から画像をダウンロードする抽象メソッド

        Args:
            image_results: 検索結果の画像情報リスト
            session_id: セッションID（ユーザー識別用）

        Returns:
            List[str]: ダウンロードされた画像ファイルのパスリスト
        """
        pass
    
    @abstractmethod
    def apply_filter_to_all(self, image_paths: List[str], filter_type: str) -> List[str]:
        """複数の画像に同じフィルタを適用する抽象メソッド

        Args:
            image_paths: 元画像のパスリスト
            filter_type: フィルタタイプ

        Returns:
            List[str]: フィルタ適用後の画像パスリスト
        """
        pass

# 各エンジン用のクラスをインポート
from .google_image_search import GoogleImageSearch

def create_image_search_engine(engine_type: str, **kwargs) -> ImageSearchEngine:
    """エンジンタイプに応じた画像検索エンジンを作成する

    Args:
        engine_type: エンジンタイプ ('google')
        **kwargs: エンジンに渡す追加パラメータ

    Returns:
        ImageSearchEngine: 画像検索エンジンのインスタンス
    """
    if engine_type.lower() == 'google':
        required_keys = ['apify_api_key', 'output_dir']
        for key in required_keys:
            if key not in kwargs:
                raise ValueError(f"Google Image Search engine requires '{key}' parameter")
        
        return GoogleImageSearch(
            apify_api_key=kwargs['apify_api_key'],
            output_dir=kwargs['output_dir']
        )
    else:
        raise ValueError(f"Unsupported image search engine type: {engine_type}")

class ImageManager:
    """画像管理クラス"""
    
    def __init__(self, search_engine: ImageSearchEngine):
        """初期化

        Args:
            search_engine: 画像検索エンジン
        """
        self.search_engine = search_engine
        self.available_filters = ['grayscale', 'sepia', 'brightness', 'contrast']
    
    def search_and_download(self, query: str, session_id: str, max_images: int = 10) -> List[str]:
        """キーワードで画像を検索してダウンロードする

        Args:
            query: 検索キーワード
            session_id: セッションID
            max_images: 取得する画像の最大数

        Returns:
            List[str]: ダウンロードされた画像ファイルのパスリスト
        """
        # 画像を検索
        image_results = self.search_engine.search_images(query, max_images)
        
        # 画像をダウンロード
        downloaded_paths = self.search_engine.download_images(image_results, session_id)
        
        return downloaded_paths
    
    def apply_filter(self, image_paths: List[str], filter_type: str) -> List[str]:
        """画像にフィルタを適用する

        Args:
            image_paths: 元画像のパスリスト
            filter_type: フィルタタイプ

        Returns:
            List[str]: フィルタ適用後の画像パスリスト
        """
        if filter_type not in self.available_filters:
            raise ValueError(f"Unsupported filter type: {filter_type}")
        
        return self.search_engine.apply_filter_to_all(image_paths, filter_type)
    
    def get_available_filters(self) -> List[str]:
        """利用可能なフィルタのリストを取得する

        Returns:
            List[str]: 利用可能なフィルタのリスト
        """
        return self.available_filters.copy()
