"""
diffusionstudio/coreを使用した動画生成モジュール
"""
import os
import logging
import time
import json
from typing import Dict, List, Optional, Tuple
import subprocess
from moviepy.editor import VideoFileClip, AudioFileClip, ImageClip, concatenate_videoclips, CompositeAudioClip, CompositeVideoClip, TextClip

logger = logging.getLogger(__name__)

class VideoGenerator:
    """diffusionstudio/coreを使用した動画生成クラス"""
    
    def __init__(self, output_dir: str, temp_dir: str, font_path: Optional[str] = None):
        """初期化

        Args:
            output_dir: 動画ファイルの出力ディレクトリ
            temp_dir: 一時ファイルの保存ディレクトリ
            font_path: 字幕用フォントのパス（Noneの場合はデフォルト）
        """
        self.output_dir = output_dir
        self.temp_dir = temp_dir
        self.font_path = font_path
        
        # 出力ディレクトリが存在しない場合は作成
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(temp_dir, exist_ok=True)
    
    def create_slideshow(self, image_paths: List[str], slide_duration: float = 5.0, 
                        output_filename: Optional[str] = None) -> str:
        """画像からスライドショー動画を作成する

        Args:
            image_paths: 画像ファイルのパスリスト
            slide_duration: 1枚あたりの表示時間（秒）
            output_filename: 出力ファイル名（Noneの場合は自動生成）

        Returns:
            str: 生成された動画ファイルのパス
        """
        # 出力ファイル名が指定されていない場合は自動生成
        if output_filename is None:
            timestamp = int(time.time())
            output_filename = f"slideshow_{timestamp}.mp4"
        
        # 拡張子がない場合は追加
        if not output_filename.endswith('.mp4'):
            output_filename += '.mp4'
        
        output_path = os.path.join(self.temp_dir, output_filename)
        
        try:
            # 各画像からクリップを作成
            clips = []
            for img_path in image_paths:
                clip = ImageClip(img_path).set_duration(slide_duration)
                clips.append(clip)
            
            # クリップを連結
            video = concatenate_videoclips(clips, method="compose")
            
            # 動画を保存
            video.write_videofile(output_path, codec='libx264', fps=24)
            
            logger.info(f"Slideshow created successfully: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error creating slideshow: {e}")
            raise
    
    def add_audio_to_video(self, video_path: str, audio_paths: List[str], 
                          bgm_path: Optional[str] = None, bgm_volume: float = 0.3,
                          output_filename: Optional[str] = None) -> str:
        """動画に音声とBGMを追加する

        Args:
            video_path: 元動画のパス
            audio_paths: 音声ファイルのパスリスト
            bgm_path: BGMファイルのパス（Noneの場合はBGMなし）
            bgm_volume: BGMの音量（0.0〜1.0）
            output_filename: 出力ファイル名（Noneの場合は自動生成）

        Returns:
            str: 生成された動画ファイルのパス
        """
        # 出力ファイル名が指定されていない場合は自動生成
        if output_filename is None:
            timestamp = int(time.time())
            output_filename = f"video_with_audio_{timestamp}.mp4"
        
        # 拡張子がない場合は追加
        if not output_filename.endswith('.mp4'):
            output_filename += '.mp4'
        
        output_path = os.path.join(self.temp_dir, output_filename)
        
        try:
            # 元動画を読み込む
            video = VideoFileClip(video_path)
            
            # 音声クリップを読み込む
            audio_clips = []
            current_time = 0
            
            for audio_path in audio_paths:
                audio = AudioFileClip(audio_path)
                audio = audio.set_start(current_time)
                audio_clips.append(audio)
                current_time += audio.duration
            
            # BGMを追加（ある場合）
            if bgm_path:
                bgm = AudioFileClip(bgm_path)
                
                # BGMをループして動画の長さに合わせる
                if bgm.duration < current_time:
                    loops = int(current_time / bgm.duration) + 1
                    bgm = concatenate_videoclips([bgm] * loops).subclip(0, current_time)
                else:
                    bgm = bgm.subclip(0, current_time)
                
                # BGMの音量を調整
                bgm = bgm.volumex(bgm_volume)
                
                audio_clips.append(bgm)
            
            # 音声を合成
            composite_audio = CompositeAudioClip(audio_clips)
            
            # 動画の長さを音声に合わせる
            if video.duration < current_time:
                # 最後のフレームを静止画として延長
                last_frame = video.to_ImageClip(video.duration - 0.001)
                extended_clip = last_frame.set_duration(current_time - video.duration)
                video = concatenate_videoclips([video, extended_clip])
            else:
                video = video.subclip(0, current_time)
            
            # 音声を動画に設定
            video = video.set_audio(composite_audio)
            
            # 動画を保存
            video.write_videofile(output_path, codec='libx264', audio_codec='aac', fps=24)
            
            logger.info(f"Audio added to video successfully: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error adding audio to video: {e}")
            raise
    
    def add_subtitles(self, video_path: str, subtitles: List[Dict], 
                     font_size: int = 36, font_color: str = 'white',
                     output_filename: Optional[str] = None) -> str:
        """動画に字幕を追加する

        Args:
            video_path: 元動画のパス
            subtitles: 字幕情報のリスト
                [
                    {"text": "字幕1", "start": 0, "duration": 5},
                    {"text": "字幕2", "start": 5, "duration": 3},
                    ...
                ]
            font_size: フォントサイズ
            font_color: フォント色
            output_filename: 出力ファイル名（Noneの場合は自動生成）

        Returns:
            str: 生成された動画ファイルのパス
        """
        # 出力ファイル名が指定されていない場合は自動生成
        if output_filename is None:
            timestamp = int(time.time())
            output_filename = f"video_with_subtitles_{timestamp}.mp4"
        
        # 拡張子がない場合は追加
        if not output_filename.endswith('.mp4'):
            output_filename += '.mp4'
        
        output_path = os.path.join(self.output_dir, output_filename)
        
        try:
            # 元動画を読み込む
            video = VideoFileClip(video_path)
            
            # 字幕クリップを作成
            subtitle_clips = []
            
            for subtitle in subtitles:
                text = subtitle["text"]
                start = subtitle["start"]
                duration = subtitle["duration"]
                
                # TextClipを作成
                txt_clip = TextClip(
                    text,
                    fontsize=font_size,
                    color=font_color,
                    font=self.font_path,
                    stroke_color='black',
                    stroke_width=2,
                    method='caption',
                    size=(video.w * 0.9, None)  # 幅を動画の90%に設定
                )
                
                # 位置を設定（下部中央）
                txt_clip = txt_clip.set_position(('center', 'bottom')).set_duration(duration).set_start(start)
                
                subtitle_clips.append(txt_clip)
            
            # 字幕を動画に合成
            final_video = CompositeVideoClip([video] + subtitle_clips)
            
            # 動画を保存
            final_video.write_videofile(output_path, codec='libx264', audio_codec='aac', fps=24)
            
            logger.info(f"Subtitles added to video successfully: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error adding subtitles to video: {e}")
            raise
    
    def generate_video(self, image_paths: List[str], audio_paths: List[Dict], 
                      intro_audio_path: Optional[str] = None,
                      bgm_path: Optional[str] = None,
                      slide_duration: float = 5.0,
                      output_filename: Optional[str] = None) -> str:
        """画像と音声から動画を生成する

        Args:
            image_paths: 画像ファイルのパスリスト
            audio_paths: 音声ファイル情報のリスト
                [
                    {"path": "音声ファイルパス1", "text": "テキスト1"},
                    {"path": "音声ファイルパス2", "text": "テキスト2"},
                    ...
                ]
            intro_audio_path: イントロ音声のパス（Noneの場合はイントロなし）
            bgm_path: BGMファイルのパス（Noneの場合はBGMなし）
            slide_duration: 1枚あたりの表示時間（秒）
            output_filename: 出力ファイル名（Noneの場合は自動生成）

        Returns:
            str: 生成された動画ファイルのパス
        """
        try:
            # スライドショーを作成
            slideshow_path = self.create_slideshow(image_paths, slide_duration)
            
            # 音声パスのリストを作成
            all_audio_paths = []
            subtitles = []
            current_time = 0
            
            # イントロ音声がある場合は先頭に追加
            if intro_audio_path:
                all_audio_paths.append(intro_audio_path)
                
                # イントロ音声の長さを取得
                intro_audio = AudioFileClip(intro_audio_path)
                intro_duration = intro_audio.duration
                
                # イントロ字幕を追加
                if audio_paths and "text" in audio_paths[0]:
                    subtitles.append({
                        "text": audio_paths[0]["text"],
                        "start": current_time,
                        "duration": intro_duration
                    })
                
                current_time += intro_duration
            
            # 各音声ファイルを追加
            for audio_info in audio_paths:
                audio_path = audio_info["path"]
                all_audio_paths.append(audio_path)
                
                # 音声の長さを取得
                audio = AudioFileClip(audio_path)
                audio_duration = audio.duration
                
                # 字幕を追加
                if "text" in audio_info:
                    subtitles.append({
                        "text": audio_info["text"],
                        "start": current_time,
                        "duration": audio_duration
                    })
                
                current_time += audio_duration
            
            # 音声を動画に追加
            video_with_audio_path = self.add_audio_to_video(
                slideshow_path, 
                all_audio_paths, 
                bgm_path
            )
            
            # 字幕を追加
            final_video_path = self.add_subtitles(
                video_with_audio_path, 
                subtitles,
                output_filename=output_filename
            )
            
            return final_video_path
            
        except Exception as e:
            logger.error(f"Error generating video: {e}")
            raise
