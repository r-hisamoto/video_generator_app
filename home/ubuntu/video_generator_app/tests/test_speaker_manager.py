"""
話者管理機能のテスト用スクリプト
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

def test_speaker_manager(comments: list, engine_type: str = "openai", output_dir: str = None):
    """話者管理機能のテスト

    Args:
        comments: コメントのリスト
        engine_type: TTSエンジンタイプ ('openai' または 'fish_audio')
        output_dir: 出力ディレクトリ（Noneの場合はデフォルト）
    """
    try:
        # 出力ディレクトリの設定
        if output_dir is None:
            output_dir = os.path.join(os.getcwd(), "test_output", "tts")
        
        os.makedirs(output_dir, exist_ok=True)
        
        # TTSエンジンを作成
        if engine_type == "openai":
            tts_engine = create_tts_engine(
                "openai",
                api_key=Config.OPENAI_API_KEY,
                output_dir=output_dir
            )
        else:
            tts_engine = create_tts_engine(
                "fish_audio",
                api_key=Config.FISH_AUDIO_API_KEY,
                output_dir=output_dir
            )
        
        # 話者管理クラスを作成
        speaker_manager = SpeakerManager(tts_engine)
        
        # 利用可能な音声モデルを表示
        available_voices = tts_engine.get_available_voices()
        logger.info(f"Available voices: {available_voices}")
        
        # イントロ用の話者を割り当て
        intro_voice = speaker_manager.assign_random_voice(exclude_last=False)
        logger.info(f"Assigned intro voice: {intro_voice}")
        
        # コメントに話者を割り当て
        comments_with_voices = speaker_manager.assign_voices_to_comments(comments, intro_voice)
        
        # 結果を表示
        for i, comment in enumerate(comments_with_voices):
            logger.info(f"Comment {i+1}: Voice = {comment['voice']}")
        
        # 連続して同じ話者が使われていないことを確認
        has_consecutive_voices = False
        for i in range(1, len(comments_with_voices)):
            if comments_with_voices[i]['voice'] == comments_with_voices[i-1]['voice']:
                logger.warning(f"Consecutive voices detected at positions {i-1} and {i}")
                has_consecutive_voices = True
        
        if not has_consecutive_voices:
            logger.info("No consecutive voices detected - Test PASSED")
        else:
            logger.warning("Consecutive voices detected - Test FAILED")
        
        # 結果をJSONファイルに保存
        output_file = f"speaker_assignment_{engine_type}.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(comments_with_voices, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Results saved to: {output_file}")
        
        return comments_with_voices
        
    except Exception as e:
        logger.error(f"Error in test_speaker_manager: {e}")
        raise

if __name__ == "__main__":
    # テスト用のコメントを作成
    test_comments = [
        {"text": "これは1つ目のコメントです。", "user": "ユーザー1"},
        {"text": "これは2つ目のコメントです。", "user": "ユーザー2"},
        {"text": "これは3つ目のコメントです。", "user": "ユーザー3"},
        {"text": "これは4つ目のコメントです。", "user": "ユーザー4"},
        {"text": "これは5つ目のコメントです。", "user": "ユーザー5"},
    ]
    
    # エンジンタイプを指定（デフォルトはOpenAI）
    engine = "openai"
    if len(sys.argv) > 1:
        engine = sys.argv[1]
    
    # テスト実行
    test_speaker_manager(test_comments, engine_type=engine)
