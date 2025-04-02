"""
WEBインターフェースのメインアプリケーション
"""
import os
import uuid
import logging
from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List, Dict, Optional

# 設定の読み込み
from src.config import Config

# 各モジュールのインポート
from src.comment_extractor import create_extractor, detect_platform
from src.tts import create_tts_engine, SpeakerManager
from src.image_search import create_image_search_engine, ImageManager
from src.video_generator import create_video_generator

# ロギングの設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# FastAPIアプリケーションの作成
app = FastAPI(title="5ch/X コメント抽出・動画生成アプリ")

# 静的ファイルとテンプレートの設定
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# セッション管理用の辞書
sessions = {}

# リクエスト/レスポンスモデル
class CommentExtractionRequest(BaseModel):
    url: str
    max_comments: Optional[int] = None
    shorten_intro: bool = True

class CommentExtractionResponse(BaseModel):
    session_id: str
    title: str
    intro_text: str
    comments: List[Dict]

class TTSRequest(BaseModel):
    session_id: str
    engine: str = "openai"  # "openai" または "fish_audio"
    intro_voice: Optional[str] = None
    comments: List[Dict]

class TTSResponse(BaseModel):
    session_id: str
    intro_audio_path: str
    comment_audio_paths: List[Dict]

class ImageSearchRequest(BaseModel):
    session_id: str
    query: str
    max_images: int = 10

class ImageSearchResponse(BaseModel):
    session_id: str
    image_paths: List[str]

class VideoGenerationRequest(BaseModel):
    session_id: str
    image_paths: List[str]
    audio_paths: List[Dict]
    intro_audio_path: Optional[str] = None
    bgm_path: Optional[str] = None
    slide_duration: float = 5.0

class VideoGenerationResponse(BaseModel):
    session_id: str
    video_path: str

# ルート
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """トップページを表示する"""
    return templates.TemplateResponse("index.html", {"request": request})

# コメント抽出API
@app.post("/api/extract-comments", response_model=CommentExtractionResponse)
async def extract_comments(request: CommentExtractionRequest):
    """URLからコメントを抽出する"""
    try:
        # セッションIDを生成
        session_id = str(uuid.uuid4())
        
        # プラットフォームを検出
        platform = detect_platform(request.url)
        
        # エクストラクタを作成
        if platform == 'twitter':
            extractor = create_extractor(
                platform,
                api_key=Config.TWITTER_API_KEY,
                api_secret=Config.TWITTER_API_SECRET,
                access_token=Config.TWITTER_ACCESS_TOKEN,
                access_secret=Config.TWITTER_ACCESS_SECRET
            )
        else:
            extractor = create_extractor(platform)
        
        # コメントを抽出
        result = extractor.extract_comments(
            request.url,
            max_comments=request.max_comments,
            shorten_intro=request.shorten_intro
        )
        
        # セッションに保存
        sessions[session_id] = {
            "comments": result,
            "url": request.url,
            "platform": platform
        }
        
        return {
            "session_id": session_id,
            "title": result["title"],
            "intro_text": result["intro_text"],
            "comments": result["comments"]
        }
        
    except Exception as e:
        logger.error(f"Error extracting comments: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

# 音声合成API
@app.post("/api/generate-speech", response_model=TTSResponse)
async def generate_speech(request: TTSRequest):
    """コメントから音声を生成する"""
    try:
        session_id = request.session_id
        
        if session_id not in sessions:
            return JSONResponse(
                status_code=404,
                content={"error": "Session not found"}
            )
        
        # TTSエンジンを作成
        if request.engine == "openai":
            tts_engine = create_tts_engine(
                "openai",
                api_key=Config.OPENAI_API_KEY,
                output_dir=os.path.join(Config.AUDIO_DIR, session_id)
            )
        else:
            tts_engine = create_tts_engine(
                "fish_audio",
                api_key=Config.FISH_AUDIO_API_KEY,
                output_dir=os.path.join(Config.AUDIO_DIR, session_id)
            )
        
        # 話者管理クラスを作成
        speaker_manager = SpeakerManager(tts_engine)
        
        # イントロ音声を生成
        intro_text = sessions[session_id]["comments"]["intro_text"]
        intro_voice = request.intro_voice or speaker_manager.assign_random_voice(exclude_last=False)
        
        intro_audio_path = tts_engine.generate_speech(
            intro_text,
            voice=intro_voice,
            output_filename=f"intro_{session_id}.mp3"
        )
        
        # コメント音声を生成
        comment_audio_paths = []
        
        for i, comment in enumerate(request.comments):
            voice = comment.get("voice") or speaker_manager.assign_random_voice(exclude_last=True)
            
            audio_path = tts_engine.generate_speech(
                comment["text"],
                voice=voice,
                output_filename=f"comment_{i:03d}_{session_id}.mp3"
            )
            
            comment_audio_paths.append({
                "path": audio_path,
                "text": comment["text"],
                "voice": voice
            })
        
        # セッションに保存
        sessions[session_id]["audio"] = {
            "intro_audio_path": intro_audio_path,
            "comment_audio_paths": comment_audio_paths
        }
        
        return {
            "session_id": session_id,
            "intro_audio_path": intro_audio_path,
            "comment_audio_paths": comment_audio_paths
        }
        
    except Exception as e:
        logger.error(f"Error generating speech: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

# 画像検索API
@app.post("/api/search-images", response_model=ImageSearchResponse)
async def search_images(request: ImageSearchRequest):
    """キーワードで画像を検索する"""
    try:
        session_id = request.session_id
        
        if session_id not in sessions:
            return JSONResponse(
                status_code=404,
                content={"error": "Session not found"}
            )
        
        # 画像検索エンジンを作成
        image_search_engine = create_image_search_engine(
            "google",
            apify_api_key=Config.APIFY_API_KEY,
            output_dir=Config.IMAGES_DIR
        )
        
        # 画像管理クラスを作成
        image_manager = ImageManager(image_search_engine)
        
        # 画像を検索してダウンロード
        image_paths = image_manager.search_and_download(
            request.query,
            session_id,
            max_images=request.max_images
        )
        
        # セッションに保存
        sessions[session_id]["images"] = {
            "query": request.query,
            "image_paths": image_paths
        }
        
        return {
            "session_id": session_id,
            "image_paths": image_paths
        }
        
    except Exception as e:
        logger.error(f"Error searching images: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

# 画像フィルタAPI
@app.post("/api/apply-filter")
async def apply_filter(session_id: str = Form(...), filter_type: str = Form(...)):
    """画像にフィルタを適用する"""
    try:
        if session_id not in sessions or "images" not in sessions[session_id]:
            return JSONResponse(
                status_code=404,
                content={"error": "Session or images not found"}
            )
        
        # 画像検索エンジンを作成
        image_search_engine = create_image_search_engine(
            "google",
            apify_api_key=Config.APIFY_API_KEY,
            output_dir=Config.IMAGES_DIR
        )
        
        # 画像管理クラスを作成
        image_manager = ImageManager(image_search_engine)
        
        # フィルタを適用
        image_paths = sessions[session_id]["images"]["image_paths"]
        filtered_paths = image_manager.apply_filter(image_paths, filter_type)
        
        # セッションを更新
        sessions[session_id]["images"]["image_paths"] = filtered_paths
        
        return {
            "session_id": session_id,
            "image_paths": filtered_paths
        }
        
    except Exception as e:
        logger.error(f"Error applying filter: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

# 動画生成API
@app.post("/api/generate-video", response_model=VideoGenerationResponse)
async def generate_video(request: VideoGenerationRequest):
    """画像と音声から動画を生成する"""
    try:
        session_id = request.session_id
        
        if session_id not in sessions:
            return JSONResponse(
                status_code=404,
                content={"error": "Session not found"}
            )
        
        # 動画生成エンジンを作成
        video_generator = create_video_generator(
            "diffusionstudio",
            output_dir=Config.VIDEOS_DIR,
            temp_dir=Config.TEMP_DIR
        )
        
        # 動画を生成
        video_path = video_generator.generate_video(
            image_paths=request.image_paths,
            audio_paths=request.audio_paths,
            intro_audio_path=request.intro_audio_path,
            bgm_path=request.bgm_path,
            slide_duration=request.slide_duration,
            output_filename=f"video_{session_id}.mp4"
        )
        
        # セッションに保存
        sessions[session_id]["video"] = {
            "video_path": video_path
        }
        
        return {
            "session_id": session_id,
            "video_path": video_path
        }
        
    except Exception as e:
        logger.error(f"Error generating video: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

# 動画ダウンロードAPI
@app.get("/api/download-video/{session_id}")
async def download_video(session_id: str):
    """生成された動画をダウンロードする"""
    try:
        if session_id not in sessions or "video" not in sessions[session_id]:
            return JSONResponse(
                status_code=404,
                content={"error": "Session or video not found"}
            )
        
        video_path = sessions[session_id]["video"]["video_path"]
        
        return FileResponse(
            path=video_path,
            filename=os.path.basename(video_path),
            media_type="video/mp4"
        )
        
    except Exception as e:
        logger.error(f"Error downloading video: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

# BGMアップロードAPI
@app.post("/api/upload-bgm")
async def upload_bgm(session_id: str = Form(...), bgm_file: UploadFile = File(...)):
    """BGMファイルをアップロードする"""
    try:
        if session_id not in sessions:
            return JSONResponse(
                status_code=404,
                content={"error": "Session not found"}
            )
        
        # BGM保存ディレクトリを作成
        bgm_dir = os.path.join(Config.AUDIO_DIR, session_id, "bgm")
        os.makedirs(bgm_dir, exist_ok=True)
        
        # ファイル名を生成
        filename = f"bgm_{session_id}.mp3"
        file_path = os.path.join(bgm_dir, filename)
        
        # ファイルを保存
        with open(file_path, "wb") as f:
            content = await bgm_file.read()
            f.write(content)
        
        # セッションに保存
        if "bgm" not in sessions[session_id]:
            sessions[session_id]["bgm"] = {}
        
        sessions[session_id]["bgm"]["path"] = file_path
        
        return {
            "session_id": session_id,
            "bgm_path": file_path
        }
        
    except Exception as e:
        logger.error(f"Error uploading BGM: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

# アプリケーション起動
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
