# Multimodal Input Capability - Product Requirements Document

## Executive Summary

This PRD outlines the implementation of multimodal input capabilities for the oneshot agent system, enabling agents to process images, audio, video, and documents in addition to text. This enhancement leverages PydanticAI's existing multimodal support to provide a seamless experience for users working with diverse media types.

## Background & Context

### Current State
The oneshot system currently supports file inputs through the `--files` parameter, but only processes them as text content. Files are read using `tool_services.read()` and injected into the agent's system prompt as text strings.

### Opportunity
PydanticAI provides robust multimodal support through specialized content classes:
- `ImageUrl` and `BinaryContent` for images (PNG, JPEG, GIF, WebP)
- `DocumentUrl` and `BinaryContent` for documents (PDF, text files)
- `AudioUrl` and `BinaryContent` for audio files
- `VideoUrl` and `BinaryContent` for video files

### Business Value
- **Enhanced User Experience**: Users can directly provide images, documents, audio, and video to agents
- **Expanded Use Cases**: Enables document analysis, image recognition, audio transcription, and video processing workflows
- **Competitive Advantage**: Positions oneshot as a comprehensive multimodal AI orchestration platform

## Goals & Success Metrics

### Primary Goals
1. Enable seamless processing of image, audio, video, and document files
2. Maintain backward compatibility with existing text file processing
3. Provide intuitive CLI interface for multimodal inputs
4. Support both local files and URLs

### Success Metrics
- 100% backward compatibility with existing text file workflows
- Support for at least 10 common media file formats
- Sub-2-second processing time for typical media files (<10MB)
- Zero breaking changes to existing agent configurations

## User Stories & Use Cases

### Core User Stories

**US1: Image Analysis**
- As a user, I want to pass an image file to an agent so that it can analyze and describe the image content
- Acceptance: `./oneshot vision_agent "What's in this image?" --files image.jpg`

**US2: Document Processing** 
- As a user, I want to upload a PDF document so that an agent can summarize its contents
- Acceptance: `./oneshot research_agent "Summarize this paper" --files research.pdf`

**US3: Audio Transcription**
- As a user, I want to provide an audio file so that an agent can transcribe and analyze the speech
- Acceptance: `./oneshot writing_agent "Transcribe this meeting" --files meeting.mp3`

**US4: Video Analysis**
- As a user, I want to upload a video file so that an agent can describe what happens in the video
- Acceptance: `./oneshot video_agent "Describe this video" --files demo.mp4`

**US5: Mixed Media Processing**
- As a user, I want to provide multiple file types in a single request
- Acceptance: `./oneshot analysis_agent "Compare these" --files report.pdf,chart.png,notes.txt`

**US6: URL-based Media**
- As a user, I want to reference media files by URL instead of uploading local files
- Acceptance: `./oneshot web_agent "Analyze this image" --urls https://example.com/image.jpg`

### Advanced Use Cases

**UC1: Multimodal Conversation Context**
- Maintain multimodal content across conversation turns in run continuations
- Support referencing previously provided media in follow-up questions

**UC2: Large File Handling**
- Graceful handling of large media files (>50MB) with appropriate user feedback
- Automatic compression/optimization for oversized files where possible

**UC3: Format Validation**
- Validate file formats before processing and provide helpful error messages
- Support format conversion where appropriate (e.g., HEIC to JPEG)

## Technical Requirements

### Architecture Overview

The implementation will extend the existing file processing pipeline with multimodal content detection and handling:

```
User Input (--files) 
    ↓
File Type Detection
    ↓
┌─────────────────┬─────────────────┐
│   Text Files    │   Media Files   │
│   (existing)    │    (new)        │
└─────────────────┴─────────────────┘
    ↓                       ↓
Text Content            Binary Content
Injection               Objects
    ↓                       ↓
    System Prompt ←→ Agent Message List
                        ↓
                   PydanticAI Agent
```

### Core Components

#### 1. Media Type Detection (`MediaTypeDetector`)
```python
class MediaTypeDetector:
    @staticmethod
    def detect_file_type(filepath: Path) -> MediaType
    @staticmethod
    def get_mime_type(filepath: Path) -> str
    @staticmethod
    def is_supported_format(filepath: Path) -> bool
```

#### 2. Multimodal Content Processor (`MultimodalContentProcessor`)
```python
class MultimodalContentProcessor:
    def process_files(self, files: List[str]) -> Tuple[List[Any], Dict[str, Any]]
    def create_binary_content(self, filepath: Path) -> BinaryContent
    def create_url_content(self, url: str) -> Union[ImageUrl, DocumentUrl, AudioUrl, VideoUrl]
    def validate_file_size(self, filepath: Path) -> bool
```

#### 3. Enhanced Agent Template Processor
Extend existing `AgentTemplateProcessor` to handle multimodal content alongside text processing.

#### 4. Enhanced Agent Runner
Modify `AgentRunner` to construct agent messages with multimodal content objects.

### File Format Support

#### Phase 1 (MVP)
- **Images**: JPEG, PNG, GIF, WebP
- **Documents**: PDF, TXT, MD
- **Audio**: MP3, WAV, M4A
- **Video**: MP4, MOV, AVI

#### Phase 2 (Extended)
- **Images**: TIFF, BMP, SVG, HEIC
- **Documents**: DOCX, RTF, HTML
- **Audio**: FLAC, OGG, AAC
- **Video**: MKV, WMV, WebM

### API Design

#### CLI Interface Extensions

**Current**: `./oneshot agent_name "message" --files file1.txt,file2.md`

**Enhanced**: 
```bash
# Mixed file types
./oneshot agent_name "message" --files image.jpg,document.pdf,audio.mp3

# URL support
./oneshot agent_name "message" --urls https://example.com/image.jpg

# Combined local and URL
./oneshot agent_name "message" --files local.pdf --urls https://example.com/remote.jpg

# Force download for URLs (override model-specific handling)
./oneshot agent_name "message" --urls https://example.com/image.jpg --force-download
```

#### MCP Server Extensions

```python
# Enhanced call_agent function
def call_agent(
    agent_name: str, 
    message: str, 
    files: str = "", 
    urls: str = "",
    force_download: bool = False,
    run_id: str = "", 
    debug: bool = False
) -> str
```

#### Configuration Extensions

Agent configuration will support multimodal preferences:

```yaml
---
name: vision_agent
description: "Analyzes images and visual content"
model: "openai/gpt-4o"  # Multimodal-capable model
multimodal:
  max_file_size_mb: 20
  supported_formats: ["jpg", "png", "gif", "webp", "pdf"]
  auto_resize_images: true
  force_download_urls: false
tools:
  - image_analysis
  - web_search
---
```

### Implementation Plan

#### Phase 1: Core Infrastructure (Week 1-2)
1. **Media Type Detection System**
   - Implement `MediaTypeDetector` class
   - Add MIME type detection and validation
   - Create file format registry

2. **Multimodal Content Processing**
   - Implement `MultimodalContentProcessor` class
   - Add `BinaryContent` object creation
   - Implement file size validation and limits

3. **Enhanced Template Processing**
   - Extend `AgentTemplateProcessor` to handle multimodal content
   - Add new template variables for media content
   - Maintain backward compatibility with text processing

#### Phase 2: Agent Integration (Week 3)
1. **Agent Runner Enhancement**
   - Modify message construction to include multimodal content
   - Update agent invocation to pass content objects to PydanticAI
   - Add error handling for unsupported models/formats

2. **CLI Interface Updates**
   - Add `--urls` parameter support
   - Add `--force-download` flag
   - Enhanced error messages and validation

3. **MCP Server Updates**
   - Extend `call_agent` function with new parameters
   - Update parameter validation and documentation

#### Phase 3: Advanced Features (Week 4)
1. **URL Content Support**
   - Implement URL-based media processing
   - Add support for `ImageUrl`, `DocumentUrl`, etc.
   - Handle model-specific URL processing preferences

2. **Configuration & Validation**
   - Add multimodal configuration options to agent YAML
   - Implement format and size validation
   - Add configuration validation to `AgentConfigValidator`

3. **Testing & Documentation**
   - Comprehensive test suite for all media types
   - Update documentation and examples
   - Performance testing and optimization

### Error Handling & Edge Cases

#### File Processing Errors
- **Unsupported Format**: Clear error message with supported formats list
- **File Too Large**: Size limit notification with current limits
- **File Not Found**: Standard file not found error with path verification
- **Corrupted File**: Binary validation error with suggested solutions

#### Model Compatibility
- **Non-multimodal Model**: Clear error when agent uses text-only model with media files
- **Format Restrictions**: Model-specific format limitations (e.g., Claude PDF handling)
- **Size Limits**: Model-specific file size restrictions

#### Network & URL Handling
- **Invalid URL**: URL validation and accessibility checking
- **Download Failures**: Retry logic with exponential backoff
- **Large Remote Files**: Progress indication and timeout handling

### Security Considerations

#### File Validation
- **MIME Type Verification**: Validate actual file content matches extension
- **Malicious File Detection**: Basic checks for suspicious file patterns
- **Size Limits**: Configurable limits to prevent resource exhaustion

#### URL Processing
- **URL Validation**: Restrict to HTTPS for security
- **Domain Allowlisting**: Optional domain restrictions for enterprise use
- **Download Limits**: Size and timeout limits for remote content

#### Data Privacy
- **Local File Handling**: Ensure files are not unnecessarily cached or logged
- **Remote Content**: Clear user notification when files are downloaded
- **Model Provider Data**: Transparency about what content is sent to LLM providers

### Performance Considerations

#### File Processing
- **Lazy Loading**: Only load file content when needed
- **Streaming**: Support for large file streaming where possible
- **Compression**: Automatic image compression for oversized files

#### Memory Management
- **Content Lifecycle**: Proper cleanup of binary content objects
- **Batch Processing**: Efficient handling of multiple files
- **Resource Limits**: Configurable memory limits for file processing

#### Caching
- **URL Content**: Optional caching of downloaded remote content
- **Processed Content**: Cache expensive operations like image resizing
- **Cache Invalidation**: Proper cleanup of cached content

### Backward Compatibility

#### Existing Workflows
- **Text File Processing**: 100% backward compatibility maintained
- **Agent Configurations**: Existing agents work without modification
- **CLI Interface**: Existing `--files` parameter behavior unchanged
- **MCP Server**: Existing `call_agent` calls work without modification

#### Migration Path
- **Gradual Adoption**: Users can adopt multimodal features incrementally
- **Feature Detection**: Agents can detect and handle both text and multimodal content
- **Fallback Behavior**: Graceful degradation for unsupported scenarios

### Testing Strategy

#### Unit Tests
- Media type detection accuracy
- File processing for all supported formats
- Error handling for edge cases
- Configuration validation

#### Integration Tests
- End-to-end workflows with various file types
- CLI interface with multimodal inputs
- MCP server multimodal functionality
- Agent execution with mixed content types

#### Performance Tests
- Large file processing benchmarks
- Memory usage monitoring
- Concurrent file processing
- Network download performance

#### Compatibility Tests
- Backward compatibility verification
- Multiple model provider testing
- Cross-platform file handling
- Various file format edge cases

### Documentation Requirements

#### User Documentation
- **Getting Started Guide**: Simple examples for each media type
- **CLI Reference**: Complete parameter documentation
- **Agent Configuration**: Multimodal configuration options
- **Troubleshooting**: Common issues and solutions

#### Developer Documentation
- **API Reference**: Complete API documentation for new classes
- **Architecture Guide**: System design and component interaction
- **Extension Guide**: How to add support for new media types
- **Testing Guide**: How to test multimodal functionality

#### Examples & Tutorials
- **Image Analysis Workflows**: Vision and OCR use cases
- **Document Processing**: PDF analysis and summarization
- **Audio Processing**: Transcription and analysis workflows
- **Video Analysis**: Content description and extraction

### Success Criteria & Acceptance

#### Functional Requirements
- ✅ Process images, documents, audio, and video files
- ✅ Support both local files and URLs
- ✅ Maintain 100% backward compatibility
- ✅ Handle mixed text and media file inputs
- ✅ Provide clear error messages for unsupported scenarios

#### Performance Requirements
- ✅ Process typical media files (<10MB) in under 2 seconds
- ✅ Handle up to 10 concurrent file operations
- ✅ Memory usage stays within 500MB for typical workloads
- ✅ Support files up to 50MB with appropriate user feedback

#### Quality Requirements
- ✅ 95% test coverage for new multimodal functionality
- ✅ Zero regression in existing text file processing
- ✅ Comprehensive error handling and user feedback
- ✅ Complete documentation and examples

### Future Enhancements

#### Advanced Media Processing
- **Image Preprocessing**: Automatic image enhancement and optimization
- **Audio Preprocessing**: Noise reduction and format optimization
- **Video Preprocessing**: Frame extraction and thumbnail generation
- **Document OCR**: Text extraction from image-based documents

#### Workflow Integration
- **Batch Processing**: Process multiple files in parallel
- **Pipeline Operations**: Chain multiple agents for complex media workflows
- **Content Transformation**: Convert between media formats as needed
- **Metadata Extraction**: Extract and utilize file metadata

#### Enterprise Features
- **Content Filtering**: Advanced security scanning for enterprise deployments
- **Audit Logging**: Detailed logging of all media processing operations
- **Access Controls**: Role-based permissions for media processing
- **Integration APIs**: REST APIs for external system integration

## Conclusion

This PRD outlines a comprehensive approach to adding multimodal input capabilities to the oneshot system. The implementation leverages PydanticAI's existing multimodal support while maintaining the system's simplicity and reliability. The phased approach ensures minimal risk while delivering significant value to users.

The multimodal capabilities will transform oneshot from a text-focused agent orchestration system into a comprehensive multimodal AI platform, enabling new use cases and workflows that were previously impossible. 