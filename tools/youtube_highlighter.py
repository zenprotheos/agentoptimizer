import os
import re
import json
import requests
import tempfile
from pathlib import Path
from datetime import datetime
import yt_dlp
import httpx
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv

from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider

load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

TOOL_METADATA = {
    "type": "function",
    "function": {
        "name": "youtube_highlighter",
        "description": "Generates a YouTube video description with timestamps and extracts key highlights from a YouTube video URL.",
        "parameters": {
            "type": "object",
            "properties": {
                "youtube_url": {
                    "type": "string",
                    "description": "The full URL of the YouTube video to process."
                }
            },
            "required": ["youtube_url"]
        }
    }
}

# =======================================
# CONFIGURATION
# =======================================
# Models for transcript cleaning and description generation
CLEANING_MODEL = "google/gemini-2.5-flash-lite"
DESCRIPTION_MODEL = "openai/gpt-4.1-mini"
HTTP_REFERER = "https://github.com/chrisboden/oneshot" # Optional: Change to your project's URL
X_TITLE = "YouTube Highlighter Tool" # Optional: Change to your tool's name


# =======================================
# PYDANTIC MODELS FOR STRUCTURED OUTPUT
# =======================================

class CleanedTranscript(BaseModel):
    """Model for the cleaned transcript text."""
    cleaned_text: str = Field(..., description="The full transcript, cleaned of timestamps, filler words, and errors, with proper paragraph breaks.")

class YouTubeDescription(BaseModel):
    """Model for a comprehensive YouTube video description."""
    engaging_opening: str = Field(..., description="An engaging 2-3 sentence hook that captures the video's value proposition.")
    key_takeaways: List[str] = Field(..., description="A list of 4-6 bullet points with emojis, focusing on practical insights.")
    timestamps: List[str] = Field(..., description="A list of 8-12 major sections with descriptive titles in MM:SS or H:MM:SS format.")
    hashtags: List[str] = Field(..., description="A list of 8-12 relevant hashtags for discoverability.")

class VideoHighlight(BaseModel):
    """Model for a single video highlight segment."""
    start_time: str = Field(..., description="The EXACT start time from the transcript (e.g., '00:42:50').")
    end_time: str = Field(..., description="The estimated end time of the segment (e.g., '00:45:30').")
    key_quote: str = Field(..., description="The most impactful 1-2 sentences from the segment.")
    rationale: str = Field(..., description="A brief explanation of why this segment would work as a standalone clip.")

class VideoHighlights(BaseModel):
    """Model for a collection of video highlights."""
    highlights: List[VideoHighlight] = Field(..., description="A list of 10 video segments that would make excellent standalone clips.")


# =======================================
# YOUTUBE PROCESSING CLASS
# =======================================

class YouTubeHighlighter:
    """Generates YouTube descriptions and highlights from video URLs."""

    def __init__(self, api_key: str, base_url: str = "https://openrouter.ai/api/v1"):
        # Create HTTP client with custom headers for OpenRouter
        http_client = httpx.AsyncClient(
            headers={
                "HTTP-Referer": HTTP_REFERER,
                "X-Title": X_TITLE
            }
        )
        self.provider = OpenAIProvider(
            api_key=api_key,
            base_url=base_url,
            http_client=http_client
        )
        self.temp_dir = Path(tempfile.mkdtemp())
        print(f"📁 Working directory: {self.temp_dir}")

    def _create_agent(self, model_name: str, system_prompt: str, output_model: Any = None) -> Agent:
        """Create an agent for a specific task."""
        model = OpenAIModel(model_name=model_name, provider=self.provider)
        return Agent(
            model=model,
            system_prompt=system_prompt,
            result_type=output_model
        )

    def get_video_metadata(self, url: str) -> Dict[str, Any]:
        """Extract metadata from YouTube video."""
        print("🔍 Getting video metadata...")
        try:
            # Enhanced yt-dlp config to avoid bot detection
            config = {
                'quiet': True,
                'no_warnings': False,
                'extract_flat': False,
                'cookies_from_browser': ('chrome',),
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'extractor_retries': 3,
            }
            with yt_dlp.YoutubeDL(config) as ydl:
                info = ydl.extract_info(url, download=False)
        except Exception as e:
            print(f"⚠️ Metadata (first attempt) failed: {e}. Trying fallback...")
            # Fallback: try without cookies
            try:
                fallback_config = {
                    'quiet': True,
                    'no_warnings': False,
                    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                    'extractor_retries': 5,
                }
                with yt_dlp.YoutubeDL(fallback_config) as ydl:
                    info = ydl.extract_info(url, download=False)
            except Exception as fallback_error:
                print(f"❌ Error getting metadata (fallback also failed): {fallback_error}")
                return {}

        duration = info.get('duration', 0)
        duration_str = f"{duration // 3600:02d}:{(duration % 3600) // 60:02d}:{duration % 60:02d}" if duration else "Unknown"

        return {
            'id': info.get('id'),
            'title': info.get('title'),
            'description': info.get('description', ''),
            'channel': info.get('channel', info.get('uploader')),
            'duration': duration,
            'duration_str': duration_str,
            'view_count': info.get('view_count'),
            'upload_date': info.get('upload_date'),
            'categories': info.get('categories', []),
            'tags': info.get('tags', [])
        }

    def download_captions(self, url: str) -> tuple[Optional[str], Optional[str]]:
        """Download captions and return clean and timestamped versions."""
        print("📥 Downloading captions...")
        try:
            config = {
                'writeautomaticsub': True,
                'writesubtitles': False,
                'subtitleslangs': ['en-orig', 'en'],
                'subtitlesformat': 'vtt',
                'skip_download': True,
                'outtmpl': str(self.temp_dir / '%(id)s.%(ext)s'),
                'quiet': True,
                'no_warnings': True,
                'cookies_from_browser': ('chrome',),
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            }
            with yt_dlp.YoutubeDL(config) as ydl:
                ydl.download([url])
        except Exception as e:
            print(f"⚠️ Caption download (first attempt) failed: {e}. Trying fallback...")
            try:
                fallback_config = {
                    'writeautomaticsub': True,
                    'writesubtitles': False,
                    'subtitleslangs': ['en-orig', 'en'],
                    'subtitlesformat': 'vtt',
                    'skip_download': True,
                    'outtmpl': str(self.temp_dir / '%(id)s.%(ext)s'),
                    'quiet': True,
                    'no_warnings': True,
                }
                with yt_dlp.YoutubeDL(fallback_config) as ydl:
                    ydl.download([url])
            except Exception as fallback_error:
                print(f"❌ Error downloading captions (fallback also failed): {fallback_error}")
                return None, None

        vtt_files = list(self.temp_dir.glob("*.vtt"))
        if not vtt_files:
            print("❌ No caption files found.")
            return None, None

        print(f"✅ Found caption file: {vtt_files[0].name}")
        with open(vtt_files[0], 'r', encoding='utf-8') as f:
            vtt_content = f.read()

        clean_text = self._extract_text_from_vtt(vtt_content)
        timestamped_text = self._extract_timestamped_text_from_vtt(vtt_content)
        return clean_text, timestamped_text

    def _extract_text_from_vtt(self, vtt_content: str) -> str:
        """Extract plain text from VTT content."""
        lines = [
            re.sub(r'<[^>]+>', '', line).strip()
            for line in vtt_content.split('\n')
            if line.strip() and '-->' not in line and not re.match(r'^[\d:]+$', line)
        ]
        return ' '.join(filter(None, lines))

    def _extract_timestamped_text_from_vtt(self, vtt_content: str) -> str:
        """Extract text with timestamps preserved."""
        # This logic is complex and retained from the notebook for accuracy
        lines = vtt_content.split('\n')
        timestamped_segments = []
        current_timestamp = None
        current_text = []

        for line in lines:
            line = line.strip()
            if '-->' in line:
                if current_timestamp and current_text:
                    clean_text = ' '.join(current_text)
                    clean_text = re.sub(r'<[^>]+>', '', clean_text)
                    clean_text = re.sub(r'\s+', ' ', clean_text).strip()
                    if clean_text:
                        timestamped_segments.append(f"[{current_timestamp}] {clean_text}")
                
                start_time = line.split(' --> ')[0].strip()
                current_timestamp = self._convert_vtt_timestamp(start_time)
                current_text = []
            elif line and not line.startswith(('WEBVTT', 'NOTE', 'STYLE', '::cue')) and not re.match(r'^\d+$', line):
                current_text.append(line)

        if current_timestamp and current_text:
            clean_text = ' '.join(current_text)
            clean_text = re.sub(r'<[^>]+>', '', clean_text)
            clean_text = re.sub(r'\s+', ' ', clean_text).strip()
            if clean_text:
                timestamped_segments.append(f"[{current_timestamp}] {clean_text}")

        return '\n'.join(timestamped_segments)

    def _convert_vtt_timestamp(self, vtt_time: str) -> str:
        """Convert VTT timestamp to YouTube format."""
        try:
            time_parts = vtt_time.split('.')[0].split(':')
            if len(time_parts) == 3:
                h, m, s = [int(p) for p in time_parts]
                return f"{h}:{m:02d}:{s:02d}" if h > 0 else f"{m:02d}:{s:02d}"
            return vtt_time
        except:
            return vtt_time

    def clean_transcript(self, transcript: str, metadata: Dict[str, Any]) -> str:
        """Clean raw transcript using LLM."""
        print("🧹 Cleaning transcript...")
        try:
            system_prompt = "You are a transcript cleaner. Your job is to take raw YouTube captions and clean them into a readable format. Remove timestamps, filler words, fix transcription errors, combine fragmented sentences, and add paragraph breaks. Preserve the original meaning and tone. Return ONLY the cleaned transcript text."
            
            agent = self._create_agent(CLEANING_MODEL, system_prompt, CleanedTranscript)
            user_prompt = f"Video Title: {metadata.get('title', 'N/A')}\n\nRaw Transcript:\n{transcript}"
            
            import asyncio
            result = asyncio.run(agent.run(user_prompt))
            cleaned = result.data.cleaned_text
            print(f"✅ Transcript cleaned ({len(cleaned)} characters)")
            return cleaned
        except Exception as e:
            print(f"⚠️ Error cleaning transcript: {e}")
            return transcript

    def generate_description(self, transcript: str, metadata: Dict[str, Any]) -> str:
        """Generate YouTube description with timestamps."""
        print("📝 Generating description...")
        try:
            system_prompt = "You are an expert YouTube content strategist. Create a comprehensive YouTube description under 4800 characters including an engaging opening, 4-6 key takeaways with emojis, 8-12 timestamps, and 8-12 hashtags. Use markdown-style formatting that works on YouTube."
            
            agent = self._create_agent(DESCRIPTION_MODEL, system_prompt, YouTubeDescription)
            user_prompt = f"Video Title: {metadata.get('title', 'N/A')}\nDuration: {metadata.get('duration_str', 'N/A')}\n\nFull Transcript:\n{transcript}"
            
            import asyncio
            result = asyncio.run(agent.run(user_prompt))
            response = result.data
            
            description = (
                f"{response.engaging_opening}\n\n"
                f"Key Takeaways\n" +
                '\n'.join(f"🔹 {item}" for item in response.key_takeaways) + "\n\n"
                f"Timestamps\n" +
                '\n'.join(response.timestamps) + "\n\n"
                f"Hashtags\n" +
                ' '.join(f"#{tag}" for tag in response.hashtags)
            )
            
            print(f"✅ Description generated ({len(description)} characters)")
            return description
        except Exception as e:
            print(f"❌ Error generating description: {e}")
            return "Error generating description"

    def extract_highlights(self, timestamped_transcript: str, metadata: Dict[str, Any]) -> str:
        """Extract video highlights with accurate timestamps."""
        print("🎬 Extracting video highlights...")
        try:
            system_prompt = "You are a world-class video editor. Analyze the timestamped transcript and identify 10 segments (30s to 3m) that would make excellent standalone clips. Focus on practical advice, actionable insights, and clear explanations. For each, provide the EXACT start time from the transcript, an estimated end time, a key quote, and rationale. Do NOT hallucinate timestamps."

            agent = self._create_agent(DESCRIPTION_MODEL, system_prompt, VideoHighlights)
            user_prompt = f"Video Title: {metadata.get('title', 'N/A')}\nDuration: {metadata.get('duration_str', 'N/A')}\n\nTranscript with Accurate Timestamps:\n{timestamped_transcript}"
            
            import asyncio
            result = asyncio.run(agent.run(user_prompt))
            response = result.data

            highlights_str = "\n\n".join([
                f"{i+1}.\nStart time: {h.start_time}\nEnd time: {h.end_time}\nKey quote: \"{h.key_quote}\"\nRationale: {h.rationale}"
                for i, h in enumerate(response.highlights)
            ])
            print("✅ Highlights extracted successfully.")
            return highlights_str
        except Exception as e:
            print(f"❌ Error extracting highlights: {e}")
            return "Error extracting highlights"

    def run(self, url: str) -> Dict[str, Any]:
        """Complete pipeline to process a video and return all generated content."""
        print(f"🎬 Processing video: {url}\n{'='*50}")

        metadata = self.get_video_metadata(url)
        if not metadata:
            return {"error": "Failed to get video metadata"}
        print(f"📹 Title: {metadata.get('title')}")

        clean_transcript, timestamped_transcript = self.download_captions(url)
        if not clean_transcript or not timestamped_transcript:
            return {"error": "Failed to download captions"}
        print(f"📝 Raw transcript: {len(clean_transcript)} characters")

        cleaned_transcript = self.clean_transcript(clean_transcript, metadata)
        description = self.generate_description(cleaned_transcript, metadata)
        highlights = self.extract_highlights(timestamped_transcript, metadata)

        print(f"\n{'='*50}\n🎉 SUCCESS! Video processed successfully.")
        
        return {
            "metadata": metadata,
            "cleaned_transcript": cleaned_transcript,
            "description": description,
            "highlights": highlights,
            "timestamped_transcript": timestamped_transcript,
        }

def run(youtube_url: str) -> Dict[str, Any]:
    """
    A tool to download a YouTube video's transcript, clean it, generate a description,
    and extract key highlights for social media clips.

    Args:
        youtube_url: The full URL of the YouTube video to process.

    Returns:
        A dictionary containing the video metadata, cleaned transcript,
        generated description, and extracted highlights.
    """
    if not youtube_url or not isinstance(youtube_url, str):
        return {"error": "YouTube URL must be provided as a string."}
    if not OPENROUTER_API_KEY:
        return {"error": "OPENROUTER_API_KEY environment variable not set."}

    try:
        highlighter = YouTubeHighlighter(api_key=OPENROUTER_API_KEY)
        result = highlighter.run(url=youtube_url)
        # Clean up the temporary directory
        for item in highlighter.temp_dir.iterdir():
            item.unlink()
        highlighter.temp_dir.rmdir()
        return result
    except Exception as e:
        import traceback
        return {"error": f"An unexpected error occurred: {e}", "trace": traceback.format_exc()}