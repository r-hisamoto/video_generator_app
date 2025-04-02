import os
import json
import time
import re
from datetime import datetime
from google import genai
from lumaai import LumaAI
import requests
from moviepy.editor import VideoFileClip, concatenate_videoclips, AudioFileClip, CompositeVideoClip
from img_bucket import GCPImageUploader
import cv2
from elevenlabs import ElevenLabs
import argparse
import ast
import eleven_labs_tts
from eleven_labs_tts import generate_speech
import shutil
# Load environment variables
from dotenv import load_dotenv
load_dotenv()
from ltx_video_generation import generate_ltx_video
# Import scan_directory module
from scan_directory import scan_directory, get_remaining_scenes, get_completed_scene_videos, get_sound_effect_files

# Initialize clients
gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")

# Add video duration configuration
LUMA_VIDEO_GENERATION_DURATION_OPTIONS = [5, 10, 15]  # Duration in seconds

luma_client = LumaAI(auth_token=os.getenv("LUMAAI_API_KEY"))

# Get current timestamp
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# Define video directory path (but don't create it yet)
video_dir = f"generated_videos/video_{timestamp}"

def generate_physical_environments(num_scenes, script, max_environments=3, model="gemini", custom_prompt=None, custom_environments=None):
    # If custom environments are provided, use them directly
    if custom_environments is not None:
        print("Using provided custom environment descriptions")
        json_path = os.path.join(video_dir, f'scene_physical_environment_{timestamp}.json')
        with open(json_path, 'w') as f:
            json.dump(custom_environments, f, indent=2)
        return custom_environments, json_path

    print(f"There are {num_scenes} scenes in the script.")
    
    # Use custom prompt if provided, otherwise use default
    base_prompt = f"""
    Create a JSON array of a bunch of detailed physical environment descriptions based on the movie script.
    Each environment should be detailed and include:
    - Setting details
    - Lighting conditions
    - Weather and atmospheric conditions
    - Time of day
    - Key objects and elements in the scene 
    - The number of physical environments should be {max_environments}
    
    Some scenes will reuse the same physical environment. Across multiple scenes, the physical environment should maintain the same physical environment across two or more scenes.
    Focus on creating a cohesive visual narrative with the physical environment descriptions.
    """
    
    prompt = custom_prompt if custom_prompt else base_prompt
    prompt += """
    Return: array of objects with format:
    {
        "scene_physical_environment": "detailed string description"
    }
    """
    
    try:
        if model == "gemini":
            response = gemini_client.models.generate_content(
                model="gemini-2.0-flash-001",
                contents=[script, prompt],
                config={
                    'response_mime_type': 'application/json',
                    'temperature': 0.7,
                    'top_p': 0.8,
                    'top_k': 40,
                    'response_schema': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'scene_physical_environment': {'type': 'string'}
                            },
                            'required': ['scene_physical_environment']
                        }
                    }
                }
            )
            environments = response.parsed
        
        elif model == "claude":
            import anthropic
            client = anthropic.Anthropic(api_key=anthropic_api_key)
            
            system_prompt = """You are an expert at describing physical environments for video scenes."""

            claude_environments_format = """
            {
                "environments": [
                    {
                        "scene_physical_environment": "detailed string description"
                    },
                    ...
                ]
            }
            """
            
            response = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=8192,
                temperature=0.7,
                system=system_prompt,
                messages=[{"role": "user", "content": f"""
                {script}\n\n{prompt}
                Output JSON format like this:
                {claude_environments_format}
                """}]
            )
            
            try:
                response_text = response.content[0].text
                environments = ast.literal_eval(response_text)
                environments = environments["environments"]
                print(f"There are {len(environments)} scene physical environments in the script.")
            except Exception as e:
                print("Raw response content:", response_text)
                raise RuntimeError(f"Failed to parse Claude's response: {e}")
        
        else:
            raise ValueError(f"Unsupported model: {model}")
        
        os.makedirs(video_dir, exist_ok=True)
        json_path = os.path.join(video_dir, f'scene_physical_environment_{timestamp}.json')
        with open(json_path, 'w') as f:
            json.dump(environments, f, indent=2)
        
        return environments, json_path
        
    except Exception as e:
        raise e

def generate_metadata_without_environment(num_scenes, script, model="gemini", video_engine="luma"):
    prompt = f"""
    Create a detailed visual storyboard for {num_scenes} scenes based on the movie script. For each scene, describe:

    1. Scene Name: Give each scene a descriptive title that captures its essence and mood.
    
    2. Character Movement and Appearance:
       - Describe natural, fluid movements and actions of characters
       - Include detailed character appearances with ethnicity, gender, age, clothing style
       - Maintain consistent character appearances across scenes
       - Show how characters interact with objects and their environment
    
    3. Emotional Atmosphere:
       - Describe the mood, tone, and emotional feeling of the scene
       - Include visual cues that convey the emotional state (lighting, colors, composition)
       - Specify the atmosphere that surrounds the characters and setting
    
    4. Camera Direction:
       - Choose ONLY from these specific camera movements:
         * Static (no movement)
         * Move Left
         * Move Right
         * Move Up
         * Move Down
         * Push In
         * Pull Out
         * Zoom In
         * Zoom Out
         * Pan Left
         * Pan Right
         * Orbit Left
         * Orbit Right
         * Crane Up
         * Crane Down
       - Also specify shot types (wide shot, medium shot, close-up)
       - Ensure camera movements feel smooth and cinematic
    
    5. Sound Design:
       - Describe environmental sounds that enhance the scene
       - Suggest ambient audio elements that match the mood
       - Include action-related sound effects
       - Recommend musical tone or style that complements the scene
    
    6. Scene Continuity:
       - Each scene should flow naturally from the previous one
       - For the first scene, mark previous elements as "none"
       - For subsequent scenes, consider how they connect to earlier scenes
    
    7. Scene Duration: Choose from these options: {LUMA_VIDEO_GENERATION_DURATION_OPTIONS if video_engine == "luma" else "[5, 10]"} seconds
    
    8. Artistic Style: Suggest a consistent visual style that should be maintained across all scenes

    Focus on creating a cohesive visual narrative without dialogue, using natural, descriptive language.
    
    Return: array of objects with format:
    {{
        "scene_number": integer, # must be sequential starting from 1
        "scene_name": "string value",
        "previous_scene_movement_description": "string value",
        "scene_movement_description": "string value",
        "previous_scene_emotions": "string value",
        "scene_emotions": "string value",
        "previous_scene_camera_movement": "string value",
        "scene_camera_movement": "string value",
        "previous_scene_duration": "integer value", # based on scene duration specified
        "scene_duration": "integer value", # based on scene duration specified
        "previous_scene_sound_effects_prompt": "string value",
        "sound_effects_prompt": "string value",
        "artistic_style": "string value"
    }}
    """
    
    try:
        if model == "gemini":
            response = gemini_client.models.generate_content(
                model="gemini-2.0-flash-001",
                contents=[script, prompt],
                config={
                    'response_mime_type': 'application/json',
                    'temperature': 0.7,
                    'top_p': 0.8,
                    'top_k': 40,
                    'response_schema': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'scene_number': {'type': 'integer'},
                                'scene_name': {'type': 'string'},
                                'scene_movement_description': {'type': 'string'},
                                'scene_emotions': {'type': 'string'},
                                'scene_camera_movement': {'type': 'string'},
                                'scene_duration': {'type': 'integer'},
                                'sound_effects_prompt': {'type': 'string'},
                                'artistic_style': {'type': 'string'}
                            },
                            'required': ['scene_number', 'scene_name', 'scene_movement_description', 
                                       'scene_emotions', 'scene_camera_movement', 'scene_duration', 'sound_effects_prompt', 'artistic_style']
                        }
                    }
                }
            )
            metadata = response.parsed
        
        elif model == "claude":
            import anthropic
            client = anthropic.Anthropic(api_key=anthropic_api_key)
            
            system_prompt = """You are an expert at creating detailed scene descriptions for videos. 
            You are also an expert at creating sound effects prompts for videos.
            You will output all number of scenes needed to tell the story effectively.
            """

            claude_metadata_no_env_format = """
            {
                "scenes": [
                    {
                        "scene_number": "integer value", # must be sequential starting from 1
                        "scene_name": "string value",
                        "previous_scene_movement_description": "string value",
                        "scene_movement_description": "string value",
                        "previous_scene_emotions": "string value",
                        "scene_emotions": "string value",
                        "previous_scene_camera_movement": "string value",
                        "scene_camera_movement": "string value",
                        "previous_scene_duration": "integer value", # based on scene duration specified
                        "scene_duration": "integer value", # based on scene duration specified
                        "previous_scene_sound_effects_prompt": "string value",
                        "sound_effects_prompt": "string value",
                        "artistic_style": "string value"
                    },
                    ...
                ]
            }
            """
            
            response = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=8192,
                temperature=0.7,
                system=system_prompt,
                messages=[{"role": "user", "content": f"""
                {script}\n\n{prompt}
                Output JSON format like this:
                {claude_metadata_no_env_format}
                Output all scenes needed to tell the story effectively. No explanation is needed.
                """}]
            )
            
            try:
                response_text = response.content[0].text
                metadata = ast.literal_eval(response_text)
                metadata = metadata["scenes"]
            except Exception as e:
                print("Raw response content:", response_text)
                raise RuntimeError(f"Failed to parse Claude's response: {e}")
        
        else:
            raise ValueError(f"Unsupported model: {model}")
        
        json_path = os.path.join(video_dir, f'scene_metadata_no_env_{timestamp}.json')
        with open(json_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        return metadata, json_path
        
    except Exception as e:
        raise e

def combine_metadata_with_environment(num_scenes, script, metadata_path, environments_path, model="gemini"):
    # Load both JSON files
    with open(metadata_path, 'r') as f:
        metadata = json.load(f)
    with open(environments_path, 'r') as f:
        environments = json.load(f)
    
    prompt = f"""
    Given a list of {num_scenes} scene metadata and a list of physical environments, select the most appropriate physical environment 
    for each scene to ensure scene continuity in the physical environment of the video.
    
    Return: array of complete scene descriptions, each containing all metadata fields plus the selected physical environment.
    """
    
    try:
        if model == "gemini":
            response = gemini_client.models.generate_content(
                model="gemini-2.0-flash-001",
                contents=[script, json.dumps(metadata), json.dumps(environments), prompt],
                config={
                    'response_mime_type': 'application/json',
                    'temperature': 0.7,
                    'top_p': 0.8,
                    'top_k': 40,
                    'response_schema': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'scene_number': {'type': 'integer'},
                                'scene_name': {'type': 'string'},
                                'scene_physical_environment': {'type': 'string'},
                                'scene_movement_description': {'type': 'string'},
                                'scene_emotions': {'type': 'string'},
                                'scene_camera_movement': {'type': 'string'},
                                'scene_duration': {'type': 'integer'},
                                'sound_effects_prompt': {'type': 'string'},
                                'artistic_style': {'type': 'string'}
                            },
                            'required': ['scene_number', 'scene_name', 'scene_physical_environment',
                                       'scene_movement_description', 'scene_emotions',
                                       'scene_camera_movement', 'scene_duration', 'sound_effects_prompt', 'artistic_style']
                        }
                    }
                }
            )
            final_metadata = response.parsed
        
        elif model == "claude":
            import anthropic
            client = anthropic.Anthropic(api_key=anthropic_api_key)
            
            system_prompt = """You are an expert at combining scene metadata with appropriate physical environments.
            """

            claude_metadata_with_env_format = """
            {
                "scenes": [
                <response clipped><NOTE>To save on context only part of this file has been shown to you. You should retry this tool after you have searched inside the file with `grep -n` in order to find the line numbers of what you are looking for.</NOTE>