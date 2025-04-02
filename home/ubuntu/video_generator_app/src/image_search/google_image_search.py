"""
Google画像検索を利用した画像検索モジュール
"""
import os
import logging
import time
import requests
import json
from typing import Dict, List, Optional
from PIL import Image, ImageFilter, ImageEnhance

logger = logging.getLogger(__name__)

class GoogleImageSearch:
    """Google画像検索を利用した画像検索クラス"""
    
    def __init__(self, apify_api_key: str, output_dir: str):
        """初期化

        Args:
            apify_api_key: Apify API Key
            output_dir: 画像ファイルの出力ディレクトリ
        """
        self.apify_api_key = apify_api_key
        self.output_dir = output_dir
        
        # 出力ディレクトリが存在しない場合は作成
        os.makedirs(output_dir, exist_ok=True)
    
    def search_images(self, query: str, max_images: int = 10) -> List[Dict]:
        """キーワードで画像を検索する

        Args:
            query: 検索キーワード
            max_images: 取得する画像の最大数

        Returns:
            List[Dict]: 検索結果の画像情報リスト
        """
        logger.info(f"Searching for images with query: {query}, max_images: {max_images}")
        
        # Apify APIを使用してGoogle画像検索を実行
        apify_url = "https://api.apify.com/v2/acts/apify~google-images-scraper/runs"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.apify_api_key}"
        }
        
        payload = {
            "queries": query,
            "maxImagesPerQuery": max_images,
            "saveImageMetadata": True,
            "includeUnrelatedResults": False,
            "customDataFunction": "async ({ input, $, request, response, html }) => { return { url: request.url } }",
        }
        
        try:
            # Apify APIを呼び出して検索ジョブを開始
            response = requests.post(apify_url, headers=headers, json=payload)
            response.raise_for_status()
            
            run_id = response.json()["data"]["id"]
            logger.info(f"Apify job started with run ID: {run_id}")
            
            # ジョブの完了を待機
            status_url = f"https://api.apify.com/v2/actor-runs/{run_id}"
            dataset_url = f"https://api.apify.com/v2/actor-runs/{run_id}/dataset/items"
            
            # 最大30秒間待機
            max_wait_time = 30
            wait_interval = 2
            elapsed_time = 0
            
            while elapsed_time < max_wait_time:
                time.sleep(wait_interval)
                elapsed_time += wait_interval
                
                status_response = requests.get(status_url, headers=headers)
                status_response.raise_for_status()
                
                status = status_response.json()["data"]["status"]
                if status == "SUCCEEDED":
                    break
            
            # 検索結果を取得
            dataset_response = requests.get(dataset_url, headers=headers)
            dataset_response.raise_for_status()
            
            results = dataset_response.json()
            logger.info(f"Found {len(results)} images")
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching images: {e}")
            raise
    
    def download_images(self, image_results: List[Dict], session_id: str) -> List[str]:
        """検索結果から画像をダウンロードする

        Args:
            image_results: 検索結果の画像情報リスト
            session_id: セッションID（ユーザー識別用）

        Returns:
            List[str]: ダウンロードされた画像ファイルのパスリスト
        """
        # セッション用のディレクトリを作成
        session_dir = os.path.join(self.output_dir, session_id)
        os.makedirs(session_dir, exist_ok=True)
        
        downloaded_paths = []
        
        for i, result in enumerate(image_results):
            try:
                image_url = result.get("url")
                if not image_url:
                    logger.warning(f"No URL found for image result {i}")
                    continue
                
                # 画像をダウンロード
                response = requests.get(image_url, stream=True, timeout=10)
                response.raise_for_status()
                
                # ファイル名を生成
                file_extension = self._get_file_extension(response.headers.get("Content-Type", ""))
                if not file_extension:
                    file_extension = ".jpg"  # デフォルト拡張子
                
                filename = f"image_{i:03d}{file_extension}"
                file_path = os.path.join(session_dir, filename)
                
                # 画像を保存
                with open(file_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                downloaded_paths.append(file_path)
                logger.info(f"Downloaded image {i+1}/{len(image_results)}: {file_path}")
                
            except Exception as e:
                logger.error(f"Error downloading image {i}: {e}")
                continue
        
        return downloaded_paths
    
    def _get_file_extension(self, content_type: str) -> str:
        """Content-Typeからファイル拡張子を取得する

        Args:
            content_type: Content-Type

        Returns:
            str: ファイル拡張子
        """
        content_type = content_type.lower()
        
        if "jpeg" in content_type or "jpg" in content_type:
            return ".jpg"
        elif "png" in content_type:
            return ".png"
        elif "gif" in content_type:
            return ".gif"
        elif "webp" in content_type:
            return ".webp"
        elif "bmp" in content_type:
            return ".bmp"
        else:
            return ""
    
    def apply_filter(self, image_path: str, filter_type: str, output_path: Optional[str] = None) -> str:
        """画像にフィルタを適用する

        Args:
            image_path: 元画像のパス
            filter_type: フィルタタイプ ('grayscale', 'sepia', 'brightness', 'contrast')
            output_path: 出力画像のパス（Noneの場合は元画像を上書き）

        Returns:
            str: フィルタ適用後の画像パス
        """
        try:
            # 画像を開く
            img = Image.open(image_path)
            
            # フィルタを適用
            if filter_type == 'grayscale':
                filtered_img = img.convert('L').convert('RGB')
            elif filter_type == 'sepia':
                # セピア調フィルタ
                img = img.convert('RGB')
                filtered_img = img.copy()
                
                for i in range(img.width):
                    for j in range(img.height):
                        r, g, b = img.getpixel((i, j))
                        tr = int(0.393 * r + 0.769 * g + 0.189 * b)
                        tg = int(0.349 * r + 0.686 * g + 0.168 * b)
                        tb = int(0.272 * r + 0.534 * g + 0.131 * b)
                        filtered_img.putpixel((i, j), (min(tr, 255), min(tg, 255), min(tb, 255)))
            elif filter_type == 'brightness':
                # 明るさ調整（1.5倍）
                enhancer = ImageEnhance.Brightness(img)
                filtered_img = enhancer.enhance(1.5)
            elif filter_type == 'contrast':
                # コントラスト調整（1.5倍）
                enhancer = ImageEnhance.Contrast(img)
                filtered_img = enhancer.enhance(1.5)
            else:
                logger.warning(f"Unknown filter type: {filter_type}, returning original image")
                return image_path
            
            # 出力パスが指定されていない場合は元画像を上書き
            if output_path is None:
                output_path = image_path
            
            # 画像を保存
            filtered_img.save(output_path)
            
            return output_path
            
        except Exception as e:
            logger.error(f"Error applying filter: {e}")
            return image_path
    
    def apply_filter_to_all(self, image_paths: List[str], filter_type: str) -> List[str]:
        """複数の画像に同じフィルタを適用する

        Args:
            image_paths: 元画像のパスリスト
            filter_type: フィルタタイプ

        Returns:
            List[str]: フィルタ適用後の画像パスリスト
        """
        filtered_paths = []
        
        for path in image_paths:
            filtered_path = self.apply_filter(path, filter_type)
            filtered_paths.append(filtered_path)
        
        return filtered_paths
