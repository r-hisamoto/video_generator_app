"""
音声合成モジュールのインターフェース
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional

class TTSEngine(ABC):
    """音声合成の基底クラス"""
    
    @abstractmethod
    def generate_speech(self, text: str, voice: str, 
                       output_filename: Optional[str] = None, 
                       speed: float = 1.0) -> str:
        """テキストから音声を生成する抽象メソッド

        Args:
            text: 音声に変換するテキスト
            voice: 使用する音声モデル
            output_filename: 出力ファイル名（Noneの場合は自動生成）
            speed: 音声の速度

        Returns:
            str: 生成された音声ファイルのパス
        """
        pass
    
    @abstractmethod
    def get_available_voices(self) -> List[str]:
        """利用可能な音声モデルのリストを取得する抽象メソッド

        Returns:
            List[str]: 利用可能な音声モデルのリスト
        """
        pass
    
    @abstractmethod
    def estimate_duration(self, text: str, speed: float = 1.0) -> float:
        """テキストから音声の推定時間（秒）を計算する抽象メソッド

        Args:
            text: 音声に変換するテキスト
            speed: 音声の速度

        Returns:
            float: 推定時間（秒）
        """
        pass

# 各エンジン用のクラスをインポート
from .openai_tts import OpenAITTS
from .fish_audio_tts import FishAudioTTS

def create_tts_engine(engine_type: str, **kwargs) -> TTSEngine:
    """エンジンタイプに応じたTTSエンジンを作成する

    Args:
        engine_type: エンジンタイプ ('openai' または 'fish_audio')
        **kwargs: エンジンに渡す追加パラメータ

    Returns:
        TTSEngine: 音声合成エンジンのインスタンス
    """
    if engine_type.lower() == 'openai':
        required_keys = ['api_key', 'output_dir']
        for key in required_keys:
            if key not in kwargs:
                raise ValueError(f"OpenAI TTS engine requires '{key}' parameter")
        
        return OpenAITTS(
            api_key=kwargs['api_key'],
            output_dir=kwargs['output_dir']
        )
    elif engine_type.lower() == 'fish_audio':
        required_keys = ['api_key', 'output_dir']
        for key in required_keys:
            if key not in kwargs:
                raise ValueError(f"Fish Audio TTS engine requires '{key}' parameter")
        
        return FishAudioTTS(
            api_key=kwargs['api_key'],
            output_dir=kwargs['output_dir']
        )
    else:
        raise ValueError(f"Unsupported TTS engine type: {engine_type}")

class SpeakerManager:
    """話者管理クラス"""
    
    def __init__(self, tts_engine: TTSEngine):
        """初期化

        Args:
            tts_engine: 音声合成エンジン
        """
        self.tts_engine = tts_engine
        self.available_voices = tts_engine.get_available_voices()
        self.last_used_voice = None
    
    def assign_random_voice(self, exclude_last: bool = True) -> str:
        """ランダムな話者を割り当てる

        Args:
            exclude_last: 直前に使用した話者を除外するかどうか

        Returns:
            str: 割り当てられた話者
        """
        import random
        
        if exclude_last and self.last_used_voice and len(self.available_voices) > 1:
            voices = [v for v in self.available_voices if v != self.last_used_voice]
        else:
            voices = self.available_voices
        
        voice = random.choice(voices)
        self.last_used_voice = voice
        
        return voice
    
    def assign_voices_to_comments(self, comments: List[Dict], intro_voice: Optional[str] = None) -> List[Dict]:
        """コメントに話者を割り当てる

        Args:
            comments: コメントのリスト
            intro_voice: イントロ用の話者（Noneの場合はランダム）

        Returns:
            List[Dict]: 話者が割り当てられたコメントのリスト
        """
        result = []
        
        # イントロ用の話者を設定
        if intro_voice is None:
            intro_voice = self.assign_random_voice(exclude_last=False)
        
        self.last_used_voice = intro_voice
        
        # 各コメントに話者を割り当て
        for comment in comments:
            voice = self.assign_random_voice(exclude_last=True)
            comment_with_voice = comment.copy()
            comment_with_voice['voice'] = voice
            result.append(comment_with_voice)
        
        return result
