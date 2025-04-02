"""
OpenAI GPT-4o-mini-tts を使用した音声合成モジュール
"""
import os
import logging
import time
from typing import Dict, List, Optional
from openai import OpenAI

logger = logging.getLogger(__name__)

class OpenAITTS:
    """OpenAI GPT-4o-mini-tts を使用した音声合成クラス"""
    
    def __init__(self, api_key: str, output_dir: str):
        """初期化

        Args:
            api_key: OpenAI API Key
            output_dir: 音声ファイルの出力ディレクトリ
        """
        self.client = OpenAI(api_key=api_key)
        self.output_dir = output_dir
        
        # 出力ディレクトリが存在しない場合は作成
        os.makedirs(output_dir, exist_ok=True)
        
        # 利用可能な話者（音声モデル）
        self.available_voices = [
            "alloy", "echo", "fable", "onyx", "nova", "shimmer"
        ]
    
    def generate_speech(self, text: str, voice: str = "alloy", 
                       output_filename: Optional[str] = None, 
                       speed: float = 1.0) -> str:
        """テキストから音声を生成する

        Args:
            text: 音声に変換するテキスト
            voice: 使用する音声モデル
            output_filename: 出力ファイル名（Noneの場合は自動生成）
            speed: 音声の速度（0.25〜4.0）

        Returns:
            str: 生成された音声ファイルのパス
        """
        if voice not in self.available_voices:
            logger.warning(f"Voice '{voice}' not available. Using 'alloy' instead.")
            voice = "alloy"
        
        if speed < 0.25 or speed > 4.0:
            logger.warning(f"Speed {speed} out of range (0.25-4.0). Clamping to valid range.")
            speed = max(0.25, min(speed, 4.0))
        
        # 出力ファイル名が指定されていない場合は自動生成
        if output_filename is None:
            timestamp = int(time.time())
            output_filename = f"speech_{timestamp}_{voice}.mp3"
        
        # 拡張子がない場合は追加
        if not output_filename.endswith('.mp3'):
            output_filename += '.mp3'
        
        output_path = os.path.join(self.output_dir, output_filename)
        
        try:
            # OpenAI APIを使用して音声を生成
            response = self.client.audio.speech.create(
                model="tts-1",  # gpt-4o-mini-tts に相当するモデル名
                voice=voice,
                input=text,
                speed=speed
            )
            
            # 音声をファイルに保存
            response.stream_to_file(output_path)
            
            logger.info(f"Speech generated successfully: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error generating speech: {e}")
            raise
    
    def get_available_voices(self) -> List[str]:
        """利用可能な音声モデルのリストを取得する

        Returns:
            List[str]: 利用可能な音声モデルのリスト
        """
        return self.available_voices.copy()
    
    def estimate_duration(self, text: str, speed: float = 1.0) -> float:
        """テキストから音声の推定時間（秒）を計算する

        Args:
            text: 音声に変換するテキスト
            speed: 音声の速度

        Returns:
            float: 推定時間（秒）
        """
        # 日本語の場合、1分あたり約350〜400文字（速度1.0の場合）
        # 速度に応じて調整
        chars_per_minute = 375 / speed
        
        # 文字数から時間を計算（分）
        duration_minutes = len(text) / chars_per_minute
        
        # 分から秒に変換
        duration_seconds = duration_minutes * 60
        
        return duration_seconds
