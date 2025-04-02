"""
動画生成モジュールのテスト用スクリプト
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

# 動画生成モジュールをインポート
from src.video_generator import create_video_generator

def test_slideshow_generation(image_paths: list, slide_duration: float = 5.0, output_dir: str = None):
    """スライドショー生成のテスト

    Args:
        image_paths: 画像ファイルのパスリスト
        slide_duration: 1枚あたりの表示時間（秒）
        output_dir: 出力ディレクトリ（Noneの場合はデフォルト）
    """
    try:
        # 出力ディレクトリの設定
        if output_dir is None:
            output_dir = os.path.join(os.getcwd(), "test_output", "videos")
        
        temp_dir = os.path.join(output_dir, "temp")
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(temp_dir, exist_ok=True)
        
        # 動画生成エンジンを作成
        video_generator = create_video_generator(
            "diffusionstudio",
            output_dir=output_dir,
            temp_dir=temp_dir
        )
        
        # スライドショーを生成
        logger.info(f"Generating slideshow with {len(image_paths)} images, duration: {slide_duration}s per slide")
        slideshow_path = video_generator.create_slideshow(
            image_paths,
            slide_duration=slide_duration,
            output_filename="test_slideshow.mp4"
        )
        
        logger.info(f"Slideshow generated successfully: {slideshow_path}")
        
        return slideshow_path
        
    except Exception as e:
        logger.error(f"Error in test_slideshow_generation: {e}")
        raise

def test_add_audio_to_video(video_path: str, audio_paths: list, bgm_path: str = None, output_dir: str = None):
    """動画に音声を追加するテスト

    Args:
        video_path: 元動画のパス
        audio_paths: 音声ファイルのパスリスト
        bgm_path: BGMファイルのパス（Noneの場合はBGMなし）
        output_dir: 出力ディレクトリ（Noneの場合はデフォルト）
    """
    try:
        # 出力ディレクトリの設定
        if output_dir is None:
            output_dir = os.path.join(os.getcwd(), "test_output", "videos")
        
        temp_dir = os.path.join(output_dir, "temp")
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(temp_dir, exist_ok=True)
        
        # 動画生成エンジンを作成
        video_generator = create_video_generator(
            "diffusionstudio",
            output_dir=output_dir,
            temp_dir=temp_dir
        )
        
        # 音声を追加
        logger.info(f"Adding {len(audio_paths)} audio files to video")
        if bgm_path:
            logger.info(f"Adding BGM: {bgm_path}")
        
        video_with_audio_path = video_generator.add_audio_to_video(
            video_path,
            audio_paths,
            bgm_path=bgm_path,
            output_filename="test_video_with_audio.mp4"
        )
        
        logger.info(f"Audio added to video successfully: {video_with_audio_path}")
        
        return video_with_audio_path
        
    except Exception as e:
        logger.error(f"Error in test_add_audio_to_video: {e}")
        raise

def test_add_subtitles(video_path: str, subtitles: list, output_dir: str = None):
    """動画に字幕を追加するテスト

    Args:
        video_path: 元動画のパス
        subtitles: 字幕情報のリスト
        output_dir: 出力ディレクトリ（Noneの場合はデフォルト）
    """
    try:
        # 出力ディレクトリの設定
        if output_dir is None:
            output_dir = os.path.join(os.getcwd(), "test_output", "videos")
        
        temp_dir = os.path.join(output_dir, "temp")
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(temp_dir, exist_ok=True)
        
        # 動画生成エンジンを作成
        video_generator = create_video_generator(
            "diffusionstudio",
            output_dir=output_dir,
            temp_dir=temp_dir
        )
        
        # 字幕を追加
        logger.info(f"Adding {len(subtitles)} subtitles to video")
        video_with_subtitles_path = video_generator.add_subtitles(
            video_path,
            subtitles,
            font_size=36,
            font_color="white",
            output_filename="test_video_with_subtitles.mp4"
        )
        
        logger.info(f"Subtitles added to video successfully: {video_with_subtitles_path}")
        
        return video_with_subtitles_path
        
    except Exception as e:
        logger.error(f"Error in test_add_subtitles: {e}")
        raise

def test_generate_video(image_paths: list, audio_paths: list, intro_audio_path: str = None, 
                       bgm_path: str = None, slide_duration: float = 5.0, output_dir: str = None):
    """動画生成のテスト

    Args:
        image_paths: 画像ファイルのパスリスト
        audio_paths: 音声ファイル情報のリスト
        intro_audio_path: イントロ音声のパス（Noneの場合はイントロなし）
        bgm_path: BGMファイルのパス（Noneの場合はBGMなし）
        slide_duration: 1枚あたりの表示時間（秒）
        output_dir: 出力ディレクトリ（Noneの場合はデフォルト）
    """
    try:
        # 出力ディレクトリの設定
        if output_dir is None:
            output_dir = os.path.join(os.getcwd(), "test_output", "videos")
        
        temp_dir = os.path.join(output_dir, "temp")
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(temp_dir, exist_ok=True)
        
        # 動画生成エンジンを作成
        video_generator = create_video_generator(
            "diffusionstudio",
            output_dir=output_dir,
            temp_dir=temp_dir
        )
        
        # 動画を生成
        logger.info(f"Generating video with {len(image_paths)} images and {len(audio_paths)} audio files")
        if intro_audio_path:
            logger.info(f"Using intro audio: {intro_audio_path}")
        if bgm_path:
            logger.info(f"Using BGM: {bgm_path}")
        
        video_path = video_generator.generate_video(
            image_paths,
            audio_paths,
            intro_audio_path=intro_audio_path,
            bgm_path=bgm_path,
            slide_duration=slide_duration,
            output_filename="test_final_video.mp4"
        )
        
        logger.info(f"Video generated successfully: {video_path}")
        
        return video_path
        
    except Exception as e:
        logger.error(f"Error in test_generate_video: {e}")
        raise

if __name__ == "__main__":
    # テスト用のディレクトリを設定
    test_output_dir = os.path.join(os.getcwd(), "test_output")
    
    # テスト用の画像パスを指定（実際のファイルパスに置き換える必要あり）
    test_image_paths = [
        os.path.join(test_output_dir, "images", "image_001.jpg"),
        os.path.join(test_output_dir, "images", "image_002.jpg"),
        os.path.join(test_output_dir, "images", "image_003.jpg"),
    ]
    
    # テスト用の音声パスを指定（実際のファイルパスに置き換える必要あり）
    test_audio_paths = [
        {
            "path": os.path.join(test_output_dir, "tts", "comment_001.mp3"),
            "text": "これは1つ目のコメントです。"
        },
        {
            "path": os.path.join(test_output_dir, "tts", "comment_002.mp3"),
            "text": "これは2つ目のコメントです。"
        },
        {
            "path": os.path.join(test_output_dir, "tts", "comment_003.mp3"),
            "text": "これは3つ目のコメントです。"
        },
    ]
    
    # テスト用のイントロ音声パスを指定（実際のファイルパスに置き換える必要あり）
    test_intro_audio_path = os.path.join(test_output_dir, "tts", "intro.mp3")
    
    # テスト用のBGMパスを指定（実際のファイルパスに置き換える必要あり）
    test_bgm_path = os.path.join(test_output_dir, "audio", "bgm.mp3")
    
    # コマンドライン引数からテスト種別を取得
    test_type = "all"
    if len(sys.argv) > 1:
        test_type = sys.argv[1]
    
    # テスト実行
    if test_type == "slideshow" or test_type == "all":
        # スライドショー生成のテスト
        slideshow_path = test_slideshow_generation(test_image_paths)
    
    if test_type == "audio" or test_type == "all":
        # 音声追加のテスト（スライドショーのテスト後）
        if 'slideshow_path' in locals():
            audio_paths = [item["path"] for item in test_audio_paths]
            video_with_audio_path = test_add_audio_to_video(slideshow_path, audio_paths, test_bgm_path)
    
    if test_type == "subtitles" or test_type == "all":
        # 字幕追加のテスト（音声追加のテスト後）
        if 'video_with_audio_path' in locals():
            subtitles = [
                {"text": item["text"], "start": i * 5, "duration": 5}
                for i, item in enumerate(test_audio_paths)
            ]
            video_with_subtitles_path = test_add_subtitles(video_with_audio_path, subtitles)
    
    if test_type == "full" or test_type == "all":
        # 完全な動画生成のテスト
        final_video_path = test_generate_video(
            test_image_paths,
            test_audio_paths,
            intro_audio_path=test_intro_audio_path,
            bgm_path=test_bgm_path
        )
