"""
動画生成モジュールのインターフェース
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional

class VideoGeneratorEngine(ABC):
    """動画生成の基底クラス"""
    
    @abstractmethod
    def create_slideshow(self, image_paths: List[str], slide_duration: float = 5.0, 
                        output_filename: Optional[str] = None) -> str:
        """画像からスライドショー動画を作成する抽象メソッド

        Args:
            image_paths: 画像ファイルのパスリスト
            slide_duration: 1枚あたりの表示時間（秒）
            output_filename: 出力ファイル名（Noneの場合は自動生成）

        Returns:
            str: 生成された動画ファイルのパス
        """
        pass
    
    @abstractmethod
    def add_audio_to_video(self, video_path: str, audio_paths: List[str], 
                          bgm_path: Optional[str] = None, bgm_volume: float = 0.3,
                          output_filename: Optional[str] = None) -> str:
        """動画に音声とBGMを追加する抽象メソッド

        Args:
            video_path: 元動画のパス
            audio_paths: 音声ファイルのパスリスト
            bgm_path: BGMファイルのパス（Noneの場合はBGMなし）
            bgm_volume: BGMの音量（0.0〜1.0）
            output_filename: 出力ファイル名（Noneの場合は自動生成）

        Returns:
            str: 生成された動画ファイルのパス
        """
        pass
    
    @abstractmethod
    def add_subtitles(self, video_path: str, subtitles: List[Dict], 
                     font_size: int = 36, font_color: str = 'white',
                     output_filename: Optional[str] = None) -> str:
        """動画に字幕を追加する抽象メソッド

        Args:
            video_path: 元動画のパス
            subtitles: 字幕情報のリスト
            font_size: フォントサイズ
            font_color: フォント色
            output_filename: 出力ファイル名（Noneの場合は自動生成）

        Returns:
            str: 生成された動画ファイルのパス
        """
        pass
    
    @abstractmethod
    def generate_video(self, image_paths: List[str], audio_paths: List[Dict], 
                      intro_audio_path: Optional[str] = None,
                      bgm_path: Optional[str] = None,
                      slide_duration: float = 5.0,
                      output_filename: Optional[str] = None) -> str:
        """画像と音声から動画を生成する抽象メソッド

        Args:
            image_paths: 画像ファイルのパスリスト
            audio_paths: 音声ファイル情報のリスト
            intro_audio_path: イントロ音声のパス（Noneの場合はイントロなし）
            bgm_path: BGMファイルのパス（Noneの場合はBGMなし）
            slide_duration: 1枚あたりの表示時間（秒）
            output_filename: 出力ファイル名（Noneの場合は自動生成）

        Returns:
            str: 生成された動画ファイルのパス
        """
        pass

# 各エンジン用のクラスをインポート
from .video_generator import VideoGenerator

def create_video_generator(engine_type: str, **kwargs) -> VideoGeneratorEngine:
    """エンジンタイプに応じた動画生成エンジンを作成する

    Args:
        engine_type: エンジンタイプ ('diffusionstudio')
        **kwargs: エンジンに渡す追加パラメータ

    Returns:
        VideoGeneratorEngine: 動画生成エンジンのインスタンス
    """
    if engine_type.lower() == 'diffusionstudio':
        required_keys = ['output_dir', 'temp_dir']
        for key in required_keys:
            if key not in kwargs:
                raise ValueError(f"Video generator engine requires '{key}' parameter")
        
        return VideoGenerator(
            output_dir=kwargs['output_dir'],
            temp_dir=kwargs['temp_dir'],
            font_path=kwargs.get('font_path')
        )
    else:
        raise ValueError(f"Unsupported video generator engine type: {engine_type}")
