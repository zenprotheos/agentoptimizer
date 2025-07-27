#!/usr/bin/env python3
"""
Multimodal Processor - Handles detection and processing of multimodal content for agents
"""

from enum import Enum
from pathlib import Path
from typing import Dict, Any, List, Tuple, Union, Optional
from dataclasses import dataclass
import mimetypes
from urllib.parse import urlparse
from app.agent_errors import MultimodalFileError, MultimodalURLError, MultimodalCapabilityError

# Import PydanticAI multimodal classes
try:
    from pydantic_ai import ImageUrl, BinaryContent, DocumentUrl, AudioUrl, VideoUrl
except ImportError:
    # Fallback if not available
    ImageUrl = BinaryContent = DocumentUrl = AudioUrl = VideoUrl = None


class MediaType(Enum):
    IMAGE = "image"
    DOCUMENT = "document" 
    AUDIO = "audio"
    VIDEO = "video"
    TEXT = "text"


@dataclass
class MultimodalResult:
    """Container for processed multimodal content"""
    content_objects: List[Any]
    text_context: Dict[str, Any]
    has_multimodal: bool
    
    def create_message_parts(self, message: str) -> List[Any]:
        """Create PydanticAI message parts combining text and multimodal content"""
        parts = [message]
        parts.extend(self.content_objects)
        return parts


class MediaTypeDetector:
    """Handles file type detection and validation"""
    
    # Basic supported formats - keep it simple
    SUPPORTED_FORMATS = {
        MediaType.IMAGE: {'.jpg', '.jpeg', '.png', '.gif', '.webp'},
        MediaType.DOCUMENT: {'.pdf'},  # Only PDF for binary document processing
        MediaType.AUDIO: {'.mp3', '.wav', '.m4a'},
        MediaType.VIDEO: {'.mp4', '.mov', '.avi'}
    }
    
    @classmethod
    def detect_file_type(cls, filepath: Path) -> MediaType:
        """Detect media type from file extension"""
        suffix = filepath.suffix.lower()
        
        for media_type, extensions in cls.SUPPORTED_FORMATS.items():
            if suffix in extensions:
                return media_type
        
        return MediaType.TEXT
    
    @classmethod
    def is_supported_media(cls, filepath: Path) -> bool:
        """Check if file is a supported media type (not text)"""
        return cls.detect_file_type(filepath) != MediaType.TEXT
    
    @classmethod
    def get_mime_type(cls, filepath: Path) -> str:
        """Get MIME type for file"""
        mime_type, _ = mimetypes.guess_type(str(filepath))
        return mime_type or 'application/octet-stream'


class MultimodalContentProcessor:
    """Processes files and URLs into multimodal content objects"""
    
    def __init__(self, config: Dict[str, Any], debug: bool = False):
        self.config = config
        self.debug = debug
        self.max_file_size_mb = config.get('multimodal', {}).get('max_file_size_mb', 20)
    
    def create_binary_content(self, filepath: Path) -> Optional[BinaryContent]:
        """Create BinaryContent object from local file"""
        if not BinaryContent:
            raise MultimodalCapabilityError("missing_pydantic_ai_support")
            
        try:
            # Check if file exists
            if not filepath.exists():
                raise MultimodalFileError(str(filepath), "not_found")
            
            # Check file size
            file_size_mb = filepath.stat().st_size / (1024 * 1024)
            if file_size_mb > self.max_file_size_mb:
                raise MultimodalFileError(
                    str(filepath), 
                    "too_large", 
                    f"{file_size_mb:.1f}MB > {self.max_file_size_mb}MB"
                )
            
            # Check if format is supported
            if not MediaTypeDetector.is_supported_media(filepath):
                raise MultimodalFileError(str(filepath), "unsupported_format")
            
            # Read file and create BinaryContent
            data = filepath.read_bytes()
            media_type = MediaTypeDetector.get_mime_type(filepath)
            
            if self.debug:
                print(f"Created BinaryContent for {filepath}: {media_type}, {len(data)} bytes")
            
            return BinaryContent(data=data, media_type=media_type)
            
        except MultimodalFileError:
            # Re-raise our specific errors
            raise
        except PermissionError as e:
            raise MultimodalFileError(str(filepath), "read_error", f"Permission denied: {e}")
        except OSError as e:
            raise MultimodalFileError(str(filepath), "read_error", f"OS error: {e}")
        except Exception as e:
            raise MultimodalFileError(str(filepath), "read_error", str(e))
    
    def create_url_content(self, url: str) -> Optional[Union[ImageUrl, DocumentUrl, AudioUrl, VideoUrl]]:
        """Create appropriate URL content object based on URL"""
        if not any([ImageUrl, DocumentUrl, AudioUrl, VideoUrl]):
            raise MultimodalCapabilityError("missing_pydantic_ai_support")
        
        try:
            # Basic URL validation
            if not url.startswith(('http://', 'https://')):
                raise MultimodalURLError(url, "invalid_url", "URL must start with http:// or https://")
            
            # Parse URL to get file extension
            parsed = urlparse(url)
            if not parsed.netloc:
                raise MultimodalURLError(url, "invalid_url", "Invalid URL format")
            
            path = Path(parsed.path)
            media_type = MediaTypeDetector.detect_file_type(path)
            
            if media_type == MediaType.IMAGE and ImageUrl:
                return ImageUrl(url=url)
            elif media_type == MediaType.DOCUMENT and DocumentUrl:
                return DocumentUrl(url=url)
            elif media_type == MediaType.AUDIO and AudioUrl:
                return AudioUrl(url=url)
            elif media_type == MediaType.VIDEO and VideoUrl:
                return VideoUrl(url=url)
            else:
                raise MultimodalURLError(url, "unsupported_format", f"Media type {media_type.value} not supported")
                
        except MultimodalURLError:
            # Re-raise our specific errors
            raise
        except Exception as e:
            raise MultimodalURLError(url, "network_error", str(e))
    
    def process_files(self, files: List[str]) -> List[Any]:
        """Process local files into content objects"""
        content_objects = []
        errors = []
        
        for file_path in files:
            filepath = Path(file_path)
            
            # Skip text files - they're handled separately
            if not MediaTypeDetector.is_supported_media(filepath):
                if self.debug:
                    print(f"Skipping text file for multimodal processing: {filepath}")
                continue
            
            try:
                content_obj = self.create_binary_content(filepath)
                if content_obj:
                    content_objects.append(content_obj)
            except MultimodalFileError as e:
                # Collect errors but continue processing other files
                errors.append(e)
                if self.debug:
                    print(f"Multimodal file error: {e}")
        
        # If we have errors but no successful content, raise the first error
        if errors and not content_objects:
            raise errors[0]
        
        return content_objects
    
    def process_urls(self, urls: List[str]) -> List[Any]:
        """Process URLs into content objects"""
        content_objects = []
        errors = []
        
        for url in urls:
            try:
                content_obj = self.create_url_content(url)
                if content_obj:
                    content_objects.append(content_obj)
            except MultimodalURLError as e:
                # Collect errors but continue processing other URLs
                errors.append(e)
                if self.debug:
                    print(f"Multimodal URL error: {e}")
        
        # If we have errors but no successful content, raise the first error
        if errors and not content_objects:
            raise errors[0]
        
        return content_objects


class MultimodalProcessor:
    """Main multimodal processor - coordinates detection and processing"""
    
    def __init__(self, config: Dict[str, Any], debug: bool = False):
        self.config = config
        self.debug = debug
        self.content_processor = MultimodalContentProcessor(config, debug)
    
    def should_use_multimodal(self, files: List[str] = None, urls: List[str] = None) -> bool:
        """Determine if multimodal processing is needed"""
        if not files and not urls:
            return False
        
        # Check if any files are media files
        if files:
            for file_path in files:
                filepath = Path(file_path)
                if filepath.exists() and MediaTypeDetector.is_supported_media(filepath):
                    return True
        
        # URLs are assumed to potentially be media
        if urls:
            return True
        
        return False
    
    def process_inputs(self, files: List[str] = None, urls: List[str] = None) -> MultimodalResult:
        """Main entry point - process all inputs and return structured result"""
        content_objects = []
        text_context = {}
        
        # Process local files
        if files:
            file_objects = self.content_processor.process_files(files)
            content_objects.extend(file_objects)
            
            # Also collect text files for context (existing behavior)
            text_files = {}
            for file_path in files:
                filepath = Path(file_path)
                if filepath.exists() and not MediaTypeDetector.is_supported_media(filepath):
                    try:
                        text_files[file_path] = filepath.read_text(encoding='utf-8')
                    except Exception as e:
                        text_files[file_path] = f"[ERROR READING FILE: {e}]"
            
            if text_files:
                text_context['provided_files'] = text_files
        
        # Process URLs
        if urls:
            url_objects = self.content_processor.process_urls(urls)
            content_objects.extend(url_objects)
        
        has_multimodal = len(content_objects) > 0
        
        if self.debug:
            print(f"Multimodal processing result: {len(content_objects)} media objects, "
                  f"{len(text_context.get('provided_files', {}))} text files")
        
        return MultimodalResult(
            content_objects=content_objects,
            text_context=text_context,
            has_multimodal=has_multimodal
        )
    
    def create_agent_messages(self, message: str, multimodal_result: MultimodalResult) -> List[Any]:
        """Create PydanticAI message list with multimodal content"""
        if not multimodal_result.has_multimodal:
            return [message]
        
        return multimodal_result.create_message_parts(message) 