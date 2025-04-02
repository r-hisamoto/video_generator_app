from dotenv import load_dotenv
import os

# 環境変数の読み込み
load_dotenv()

# アプリケーション設定
class Config:
    # 基本設定
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    SECRET_KEY = os.getenv('SECRET_KEY', 'default-secret-key')
    
    # ディレクトリパス
    STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static')
    IMAGES_DIR = os.path.join(STATIC_DIR, 'images')
    AUDIO_DIR = os.path.join(STATIC_DIR, 'audio')
    VIDEOS_DIR = os.path.join(STATIC_DIR, 'videos')
    TEMP_DIR = os.path.join(STATIC_DIR, 'temp')
    
    # API設定
    TWITTER_API_KEY = os.getenv('TWITTER_API_KEY', '')
    TWITTER_API_SECRET = os.getenv('TWITTER_API_SECRET', '')
    TWITTER_ACCESS_TOKEN = os.getenv('TWITTER_ACCESS_TOKEN', '')
    TWITTER_ACCESS_SECRET = os.getenv('TWITTER_ACCESS_SECRET', '')
    
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    FISH_AUDIO_API_KEY = os.getenv('FISH_AUDIO_API_KEY', '')
    
    APIFY_API_KEY = os.getenv('APIFY_API_KEY', '')
    TWITTER_COOKIES = os.getenv('TWITTER_COOKIES', '{}')
    
    # Twitter抽出方法の設定
    USE_APIFY_FOR_TWITTER = os.getenv('USE_APIFY_FOR_TWITTER', 'True').lower() == 'true'
    
    # 動画生成設定
    DEFAULT_SLIDE_DURATION = int(os.getenv('DEFAULT_SLIDE_DURATION', '5'))  # 秒
    MAX_INTRO_DURATION = int(os.getenv('MAX_INTRO_DURATION', '25'))  # 秒
    DEFAULT_FONT = os.getenv('DEFAULT_FONT', 'Arial')
    DEFAULT_FONT_SIZE = int(os.getenv('DEFAULT_FONT_SIZE', '36'))
    
    # データ保持期間（日数）
    DATA_RETENTION_DAYS = int(os.getenv('DATA_RETENTION_DAYS', '7'))
    
    # 同時処理数制限
    MAX_CONCURRENT_JOBS = int(os.getenv('MAX_CONCURRENT_JOBS', '3'))
