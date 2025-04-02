"""
Google画像検索のテスト用スクリプト
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

# 画像検索モジュールをインポート
from src.image_search import create_image_search_engine, ImageManager

def test_google_image_search(query: str, max_images: int = 10, session_id: str = None, output_dir: str = None):
    """Google画像検索のテスト

    Args:
        query: 検索キーワード
        max_images: 取得する画像の最大数
        session_id: セッションID（Noneの場合は自動生成）
        output_dir: 出力ディレクトリ（Noneの場合はデフォルト）
    """
    try:
        # 出力ディレクトリの設定
        if output_dir is None:
            output_dir = os.path.join(os.getcwd(), "test_output", "images")
        
        os.makedirs(output_dir, exist_ok=True)
        
        # セッションIDの設定
        if session_id is None:
            import uuid
            session_id = str(uuid.uuid4())
        
        # 画像検索エンジンを作成
        image_search_engine = create_image_search_engine(
            "google",
            apify_api_key=Config.APIFY_API_KEY,
            output_dir=output_dir
        )
        
        # 画像管理クラスを作成
        image_manager = ImageManager(image_search_engine)
        
        # 画像を検索
        logger.info(f"Searching for images with query: {query}, max_images: {max_images}")
        image_results = image_search_engine.search_images(query, max_images)
        
        # 検索結果を表示
        logger.info(f"Found {len(image_results)} images")
        
        # 画像をダウンロード
        logger.info(f"Downloading images to: {output_dir}")
        downloaded_paths = image_search_engine.download_images(image_results, session_id)
        
        # ダウンロード結果を表示
        logger.info(f"Downloaded {len(downloaded_paths)} images")
        for i, path in enumerate(downloaded_paths):
            logger.info(f"Image {i+1}: {path}")
        
        # 結果をJSONファイルに保存
        output_file = os.path.join(output_dir, f"image_search_result_{session_id}.json")
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump({
                "query": query,
                "max_images": max_images,
                "session_id": session_id,
                "downloaded_paths": downloaded_paths
            }, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Results saved to: {output_file}")
        
        return downloaded_paths
        
    except Exception as e:
        logger.error(f"Error in test_google_image_search: {e}")
        raise

def test_image_filter(image_paths: list, filter_type: str = "grayscale", output_dir: str = None):
    """画像フィルタのテスト

    Args:
        image_paths: 画像ファイルのパスリスト
        filter_type: フィルタタイプ ('grayscale', 'sepia', 'brightness', 'contrast')
        output_dir: 出力ディレクトリ（Noneの場合はデフォルト）
    """
    try:
        # 出力ディレクトリの設定
        if output_dir is None:
            output_dir = os.path.join(os.getcwd(), "test_output", "images", "filtered")
        
        os.makedirs(output_dir, exist_ok=True)
        
        # 画像検索エンジンを作成
        image_search_engine = create_image_search_engine(
            "google",
            apify_api_key=Config.APIFY_API_KEY,
            output_dir=output_dir
        )
        
        # 画像管理クラスを作成
        image_manager = ImageManager(image_search_engine)
        
        # 利用可能なフィルタを表示
        available_filters = image_manager.get_available_filters()
        logger.info(f"Available filters: {available_filters}")
        
        # フィルタを適用
        logger.info(f"Applying filter: {filter_type}")
        filtered_paths = image_manager.apply_filter(image_paths, filter_type)
        
        # 結果を表示
        logger.info(f"Applied filter to {len(filtered_paths)} images")
        for i, path in enumerate(filtered_paths):
            logger.info(f"Filtered image {i+1}: {path}")
        
        return filtered_paths
        
    except Exception as e:
        logger.error(f"Error in test_image_filter: {e}")
        raise

if __name__ == "__main__":
    # テスト用のキーワードを指定
    test_query = "富士山 風景"
    
    # コマンドライン引数からキーワードを取得（指定されている場合）
    if len(sys.argv) > 1:
        test_query = sys.argv[1]
    
    # 画像の最大数を指定
    max_images = 5
    if len(sys.argv) > 2:
        max_images = int(sys.argv[2])
    
    # 画像検索のテスト実行
    downloaded_images = test_google_image_search(test_query, max_images)
    
    # フィルタのテスト実行（ダウンロードした画像がある場合）
    if downloaded_images:
        test_image_filter(downloaded_images, filter_type="grayscale")
