"""
OpenAI TTSのテスト用スクリプト
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

# TTSモジュールをインポート
from src.tts import create_tts_engine, SpeakerManager

def test_openai_tts(text: str, voice: str = None, output_dir: str = None):
    """OpenAI TTSのテスト

    Args:
        text: 音声に変換するテキスト
        voice: 使用する音声モデル（Noneの場合はランダム）
        output_dir: 出力ディレクトリ（Noneの場合はデフォルト）
    """
    try:
        # 出力ディレクトリの設定
        if output_dir is None:
            output_dir = os.path.join(os.getcwd(), "test_output", "tts")
        
        os.makedirs(output_dir, exist_ok=True)
        
        # TTSエンジンを作成
        tts_engine = create_tts_engine(
            "openai",
            api_key=Config.OPENAI_API_KEY,
            output_dir=output_dir
        )
        
        # 話者管理クラスを作成
        speaker_manager = SpeakerManager(tts_engine)
        
        # 利用可能な音声モデルを表示
        available_voices = tts_engine.get_available_voices()
        logger.info(f"Available voices: {available_voices}")
        
        # 音声モデルが指定されていない場合はランダムに選択
        if voice is None:
            voice = speaker_manager.assign_random_voice(exclude_last=False)
        
        # 音声の推定時間を計算
        estimated_duration = tts_engine.estimate_duration(text)
        logger.info(f"Estimated duration: {estimated_duration:.2f} seconds")
        
        # 音声を生成
        logger.info(f"Generating speech with voice: {voice}")
        output_path = tts_engine.generate_speech(
            text,
            voice=voice,
            output_filename=f"test_openai_{voice}.mp3"
        )
        
        logger.info(f"Speech generated successfully: {output_path}")
        
        return output_path
        
    except Exception as e:
        logger.error(f"Error in test_openai_tts: {e}")
        raise

if __name__ == "__main__":
    # テスト用のテキストを指定
    test_text = "これはOpenAI TTSのテストです。音声合成の品質を確認しています。"
    
    # コマンドライン引数からテキストを取得（指定されている場合）
    if len(sys.argv) > 1:
        test_text = sys.argv[1]
    
    # 音声モデルを指定（オプション）
    test_voice = None
    if len(sys.argv) > 2:
        test_voice = sys.argv[2]
    
    # テスト実行
    test_openai_tts(test_text, voice=test_voice)
