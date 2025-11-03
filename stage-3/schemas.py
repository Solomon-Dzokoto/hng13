from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class MessageContent(BaseModel):
    """Content of a message"""
    type: str = "text"
    text: str


class Message(BaseModel):
    """Message from Telex.im"""
    role: str
    content: List[MessageContent]


class AgentRequest(BaseModel):
    """Request payload from Telex.im"""
    messages: List[Message]
    agent_id: Optional[str] = None
    conversation_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class AgentResponse(BaseModel):
    """Response payload to Telex.im"""
    role: str = "assistant"
    content: List[MessageContent]
    metadata: Optional[Dict[str, Any]] = None


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    agent: str
    version: str
    timestamp: str
    ai_provider: str


class ErrorResponse(BaseModel):
    """Error response"""
    error: str
    detail: Optional[str] = None
    timestamp: str
