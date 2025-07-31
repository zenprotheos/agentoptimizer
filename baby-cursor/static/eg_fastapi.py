#!/usr/bin/env python3
"""
FastAPI Chatbot Interface with Real-time Telemetry

Provides a web-based chatbot interface that uses the oneshot orchestrator
with real-time streaming of Logfire telemetry data to show what's happening
during agent execution.
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional, AsyncGenerator
import sys
import os
import json
import asyncio
import uuid
from pathlib import Path
from datetime import datetime
import threading
import queue
import time
import re
import contextlib
from io import StringIO

# Add the app directory to Python path
sys.path.append(str(Path(__file__).parent / "app"))

from app.agent_runner import AgentRunner

app = FastAPI(title="Oneshot Chatbot", description="Interactive chatbot with real-time telemetry")

# Initialize the agent runner with debug enabled to get telemetry
runner = AgentRunner(debug=True)

# Global telemetry queue for streaming updates
telemetry_queues = {}

class ChatRequest(BaseModel):
    message: str
    files: Optional[List[str]] = None
    urls: Optional[List[str]] = None
    run_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    run_id: str
    success: bool
    error: Optional[str] = None

# Real telemetry interceptor that captures actual debug output
class RealTelemetryInterceptor:
    def __init__(self):
        self.active_sessions = {}
        self.output_buffer = StringIO()
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr
    
    def add_session(self, session_id: str, queue_obj: queue.Queue):
        self.active_sessions[session_id] = queue_obj
    
    def remove_session(self, session_id: str):
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
    
    def parse_and_broadcast_output(self, output_text: str, run_id: str = None):
        """Parse debug output and broadcast relevant telemetry events"""
        lines = output_text.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Parse different types of output
            event_type = "info"
            message = line
            
            if "Starting agent execution" in line:
                event_type = "agent_start"
                message = "Starting agent execution"
            elif "Loaded tool:" in line:
                tool_name = line.split("Loaded tool:")[-1].strip()
                event_type = "tool_load"
                message = f"Loaded tool: {tool_name}"
            elif "Creating OpenRouter model" in line:
                event_type = "model_init"
                message = "Initializing language model"
            elif "Agent execution completed" in line:
                event_type = "agent_response"
                message = "Agent execution completed"
            elif "Error" in line or "WARNING" in line:
                event_type = "error"
                message = line
            elif "Tool call:" in line:
                event_type = "tool_call"
                message = line
            elif "MCP server" in line:
                event_type = "mcp_event"
                message = line
            elif line.startswith("Template engine"):
                continue  # Skip template engine messages
            elif line.startswith("Loaded global MCP"):
                continue  # Skip MCP config messages
            elif line.startswith("Warning: Failed to initialize Logfire"):
                continue  # Skip Logfire warnings
            
            self.broadcast_event(event_type, message, run_id)
    
    def broadcast_event(self, event_type: str, message: str, run_id: str = None):
        """Broadcast telemetry event to all active sessions"""
        # Filter out heartbeat events and unwanted messages
        if event_type == "heartbeat" or not message.strip():
            return
            
        event_data = {
            "type": event_type,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "run_id": run_id
        }
        
        for session_id, queue_obj in list(self.active_sessions.items()):
            try:
                queue_obj.put_nowait(event_data)
            except queue.Full:
                # Remove full queues
                self.remove_session(session_id)

    @contextlib.contextmanager
    def capture_output(self, run_id: str = None):
        """Context manager to capture stdout/stderr during agent execution"""
        captured_output = StringIO()
        
        class TeeOutput:
            def __init__(self, original, captured, interceptor, run_id):
                self.original = original
                self.captured = captured
                self.interceptor = interceptor
                self.run_id = run_id
                
            def write(self, text):
                self.original.write(text)
                self.captured.write(text)
                # Parse and broadcast in real-time
                if text.strip():
                    self.interceptor.parse_and_broadcast_output(text, self.run_id)
                    
            def flush(self):
                self.original.flush()
                self.captured.flush()
        
        tee_stdout = TeeOutput(sys.stdout, captured_output, self, run_id)
        tee_stderr = TeeOutput(sys.stderr, captured_output, self, run_id)
        
        try:
            sys.stdout = tee_stdout
            sys.stderr = tee_stderr
            yield captured_output
        finally:
            sys.stdout = self.original_stdout
            sys.stderr = self.original_stderr

telemetry = RealTelemetryInterceptor()

@app.get("/", response_class=HTMLResponse)
async def chatbot_interface():
    """Serve the chatbot web interface"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Oneshot Chatbot</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <script src="https://cdn.tailwindcss.com"></script>
        <script src="https://unpkg.com/alpinejs@3.x.x/dist/cdn.min.js" defer></script>
        <style>
            .message-bubble { animation: fadeIn 0.3s ease-in; }
            @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
            .telemetry-item { animation: slideIn 0.2s ease-out; }
            @keyframes slideIn { from { opacity: 0; transform: translateX(-20px); } to { opacity: 1; transform: translateX(0); } }
            html, body { height: 100vh; margin: 0; padding: 0; overflow: hidden; }
            .chat-container { height: calc(100vh - 120px); }
            .messages-area { height: calc(100% - 80px); }
            .input-area { height: 80px; }
        </style>
    </head>
    <body class="bg-gray-50">
        <div x-data="chatbot()" class="h-screen flex flex-col">
            <!-- Header -->
            <div class="bg-white shadow-sm p-4 flex-shrink-0" style="height: 120px;">
                <div class="max-w-6xl mx-auto flex justify-between items-center h-full">
                    <div>
                        <h1 class="text-2xl font-bold text-gray-800">Oneshot AI Orchestrator</h1>
                        <p class="text-gray-600 text-sm">Powered by specialist AI agents with real-time telemetry</p>
                    </div>
                    <button @click="newChat()" class="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg transition-colors">
                        New Chat
                    </button>
                </div>
            </div>

            <!-- Main Content Area -->
            <div class="flex-1 min-h-0">
                <div class="max-w-6xl mx-auto h-full p-4 grid grid-cols-1 lg:grid-cols-3 gap-4">
                    <!-- Chat Interface -->
                    <div class="lg:col-span-2 flex flex-col h-full">
                        <div class="bg-white rounded-lg shadow-sm h-full flex flex-col">
                            <!-- Messages -->
                            <div class="flex-1 overflow-y-auto p-4 space-y-4 min-h-0" x-ref="messagesContainer">
                                <template x-for="message in messages" :key="message.id">
                                    <div class="message-bubble" :class="message.type === 'user' ? 'text-right' : 'text-left'">
                                        <div :class="message.type === 'user' ? 'bg-blue-500 text-white ml-12' : 'bg-gray-100 text-gray-800 mr-12'" 
                                             class="inline-block p-3 rounded-lg max-w-full">
                                            <div class="text-sm font-medium mb-1" x-show="message.type !== 'user'">
                                                🤖 Oneshot Orchestrator
                                            </div>
                                            <div class="whitespace-pre-wrap" x-html="formatMessage(message.content)"></div>
                                            <div class="text-xs opacity-75 mt-1" x-text="message.timestamp"></div>
                                        </div>
                                    </div>
                                </template>
                                
                                <!-- Loading indicator -->
                                <div x-show="isLoading" class="text-left">
                                    <div class="bg-gray-100 text-gray-800 mr-12 inline-block p-3 rounded-lg">
                                        <div class="flex items-center space-x-2">
                                            <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-500"></div>
                                            <span>Orchestrating agents...</span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            
                            <!-- Input - Always fixed at bottom -->
                            <div class="border-t p-4 flex-shrink-0 bg-white">
                                <form @submit.prevent="sendMessage()" class="flex space-x-2">
                                    <input 
                                        x-model="currentMessage" 
                                        :disabled="isLoading"
                                        placeholder="Ask the orchestrator anything..." 
                                        class="flex-1 border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:border-blue-500 disabled:bg-gray-100"
                                        x-ref="messageInput"
                                    >
                                    <button 
                                        type="submit" 
                                        :disabled="isLoading || !currentMessage.trim()"
                                        class="bg-blue-500 hover:bg-blue-600 disabled:bg-gray-300 text-white px-4 py-2 rounded-lg transition-colors">
                                        Send
                                    </button>
                                </form>
                                <div class="text-xs text-gray-500 mt-2" x-show="runId">
                                    Conversation ID: <code x-text="runId"></code>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Telemetry Panel -->
                    <div class="lg:col-span-1 flex flex-col h-full">
                        <div class="bg-white rounded-lg shadow-sm h-full flex flex-col">
                            <div class="border-b p-3 flex-shrink-0">
                                <h3 class="font-semibold text-gray-800">🔍 Agent Activity</h3>
                                <p class="text-xs text-gray-500">Real-time execution telemetry</p>
                            </div>
                            <div class="flex-1 overflow-y-auto p-3 space-y-2 min-h-0" x-ref="telemetryContainer">
                                <template x-for="event in telemetryEvents" :key="event.id">
                                    <div class="telemetry-item text-xs p-2 rounded" 
                                         :class="getTelemetryClass(event.type)">
                                        <div class="font-medium" x-text="event.type"></div>
                                        <div class="text-gray-600" x-text="event.message"></div>
                                        <div class="text-gray-400 text-xs" x-text="formatTime(event.timestamp)"></div>
                                    </div>
                                </template>
                                <div x-show="telemetryEvents.length === 0" class="text-gray-400 text-center py-8">
                                    No activity yet
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <script>
            function chatbot() {
                return {
                    messages: [],
                    telemetryEvents: [],
                    currentMessage: '',
                    isLoading: false,
                    runId: null,
                    eventSource: null,

                    init() {
                        this.setupTelemetryStream();
                        // Focus input on load
                        this.$nextTick(() => {
                            this.$refs.messageInput.focus();
                        });
                    },

                    setupTelemetryStream() {
                        this.eventSource = new EventSource('/telemetry/stream');
                        this.eventSource.onmessage = (event) => {
                            const data = JSON.parse(event.data);
                            // Filter out heartbeat events
                            if (data.type !== 'heartbeat') {
                                this.addTelemetryEvent(data);
                            }
                        };
                        
                        this.eventSource.onerror = (error) => {
                            console.log('EventSource failed:', error);
                            // Attempt to reconnect after 5 seconds
                            setTimeout(() => {
                                this.setupTelemetryStream();
                            }, 5000);
                        };
                    },

                    addTelemetryEvent(event) {
                        this.telemetryEvents.unshift({
                            ...event,
                            id: Date.now() + Math.random()
                        });
                        // Keep only last 50 events
                        if (this.telemetryEvents.length > 50) {
                            this.telemetryEvents = this.telemetryEvents.slice(0, 50);
                        }
                        this.$nextTick(() => {
                            this.$refs.telemetryContainer.scrollTop = 0;
                        });
                    },

                    async sendMessage() {
                        if (!this.currentMessage.trim() || this.isLoading) return;

                        const userMessage = {
                            id: Date.now(),
                            type: 'user',
                            content: this.currentMessage,
                            timestamp: new Date().toLocaleTimeString()
                        };
                        
                        this.messages.push(userMessage);
                        const messageToSend = this.currentMessage;
                        this.currentMessage = '';
                        this.isLoading = true;

                        this.scrollToBottom();

                        try {
                            const response = await fetch('/chat/clean', {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/json' },
                                body: JSON.stringify({
                                    message: messageToSend,
                                    run_id: this.runId
                                })
                            });

                            const data = await response.json();
                            
                            if (response.ok) {
                                // Extract run_id from response if it contains it
                                const responseText = data.response;
                                const runIdMatch = responseText.match(/\*\*Run ID:\*\* `([^`]+)`/);
                                if (runIdMatch) {
                                    this.runId = runIdMatch[1];
                                }

                                this.messages.push({
                                    id: Date.now() + 1,
                                    type: 'assistant',
                                    content: responseText,
                                    timestamp: new Date().toLocaleTimeString()
                                });
                            } else {
                                throw new Error(data.detail || 'Request failed');
                            }
                        } catch (error) {
                            this.messages.push({
                                id: Date.now() + 1,
                                type: 'assistant',
                                content: `Error: ${error.message}`,
                                timestamp: new Date().toLocaleTimeString()
                            });
                        } finally {
                            this.isLoading = false;
                            this.scrollToBottom();
                            // Refocus input
                            this.$refs.messageInput.focus();
                        }
                    },

                    newChat() {
                        this.messages = [];
                        this.runId = null;
                        this.telemetryEvents = [];
                        this.$refs.messageInput.focus();
                    },

                    scrollToBottom() {
                        this.$nextTick(() => {
                            this.$refs.messagesContainer.scrollTop = this.$refs.messagesContainer.scrollHeight;
                        });
                    },

                    formatMessage(content) {
                        // Simple markdown-like formatting
                        return content
                            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                            .replace(/\*(.*?)\*/g, '<em>$1</em>')
                            .replace(/`([^`]+)`/g, '<code class="bg-gray-200 px-1 rounded">$1</code>');
                    },

                    formatTime(timestamp) {
                        return new Date(timestamp).toLocaleTimeString();
                    },

                    getTelemetryClass(type) {
                        const classes = {
                            'agent_start': 'bg-blue-50 border-l-4 border-blue-400',
                            'tool_call': 'bg-green-50 border-l-4 border-green-400',
                            'tool_load': 'bg-yellow-50 border-l-4 border-yellow-400',
                            'model_init': 'bg-indigo-50 border-l-4 border-indigo-400',
                            'mcp_event': 'bg-cyan-50 border-l-4 border-cyan-400',
                            'agent_response': 'bg-purple-50 border-l-4 border-purple-400',
                            'error': 'bg-red-50 border-l-4 border-red-400',
                            'info': 'bg-gray-50 border-l-4 border-gray-400'
                        };
                        return classes[type] || classes['info'];
                    }
                }
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/telemetry/stream")
async def telemetry_stream(request: Request):
    """Server-Sent Events stream for real-time telemetry"""
    session_id = str(uuid.uuid4())
    telemetry_queue = queue.Queue(maxsize=100)
    telemetry.add_session(session_id, telemetry_queue)
    
    async def event_generator() -> AsyncGenerator[str, None]:
        try:
            while True:
                # Check if client is still connected
                if await request.is_disconnected():
                    break
                
                try:
                    # Non-blocking queue get with timeout
                    event = telemetry_queue.get_nowait()
                    yield f"data: {json.dumps(event)}\n\n"
                except queue.Empty:
                    # Send heartbeat every 30 seconds (but it will be filtered out)
                    yield f"data: {json.dumps({'type': 'heartbeat', 'timestamp': datetime.now().isoformat()})}\n\n"
                    await asyncio.sleep(1)  # Check more frequently for new events
                
        except Exception as e:
            print(f"Telemetry stream error: {e}")
        finally:
            telemetry.remove_session(session_id)
    
    return StreamingResponse(
        event_generator(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream",
        }
    )

@app.post("/chat/clean")
async def chat_clean(request: ChatRequest):
    """
    Send a message to the orchestrator and get a clean text response.
    Includes real telemetry broadcasting from captured debug output.
    """
    try:
        # Broadcast start event immediately
        telemetry.broadcast_event("agent_start", f"Starting orchestration: {request.message[:50]}...", request.run_id)
        
        # Capture all output during agent execution
        with telemetry.capture_output(request.run_id):
            # Use the async version to avoid asyncio.run() issue
            response = await runner.run_agent_async(
                agent_name=None,  # This will default to oneshot_agent
                message=request.message,
                files=request.files,
                urls=request.urls,
                run_id=request.run_id
            )
        
        # Broadcast completion immediately
        telemetry.broadcast_event("agent_response", "Orchestration completed successfully", request.run_id)
        
        # Format the response similar to run_agent_clean
        if response.get("success", False):
            output = response.get("output", "")
            if response.get("run_id"):
                output += f"\n\n---\n**Run ID:** `{response['run_id']}`"
                if "usage" in response:
                    usage = response["usage"]
                    output += f" (new conversation)\n**Usage:** {usage.get('requests', 0)} requests, {usage.get('total_tokens', 0)} tokens"
                    if usage.get("tools_used"):
                        output += f"\n**Tools used:** {', '.join(usage['tools_used'])}"
            return {"response": output}
        else:
            error_output = f"**Error:** {response.get('error', 'Unknown error')}"
            if response.get("run_id"):
                error_output += f"\n**Run ID:** `{response['run_id']}`"
            return {"response": error_output}
        
    except Exception as e:
        telemetry.broadcast_event("error", f"Error during orchestration: {str(e)}", request.run_id)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Full chat endpoint with detailed response data
    """
    try:
        telemetry.broadcast_event("agent_start", f"Processing request: {request.message[:50]}...", request.run_id)
        
        # Capture output during execution
        with telemetry.capture_output(request.run_id):
            # Use async version here too
            result = await runner.run_agent_async(
                agent_name=None,  # This will default to oneshot_agent
                message=request.message,
                files=request.files,
                urls=request.urls,
                run_id=request.run_id
            )
        
        telemetry.broadcast_event("agent_response", "Request processed successfully", result.get("run_id"))
        
        return ChatResponse(
            response=result.get("output", ""),
            run_id=result.get("run_id", ""),
            success=result.get("success", False),
            error=result.get("error")
        )
        
    except Exception as e:
        telemetry.broadcast_event("error", f"Chat error: {str(e)}", request.run_id)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "oneshot-chatbot"}

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Oneshot Chatbot Server...")
    print("📱 Open http://localhost:8001 in your browser")
    uvicorn.run(app, host="0.0.0.0", port=8001) 