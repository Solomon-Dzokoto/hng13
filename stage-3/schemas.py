from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime





class MessagePart(BaseModel):
    """A part of a message (text, data, or file)"""
    kind: Literal["text", "data", "file"] = "text"
    text: Optional[str] = None
    data: Optional[Any] = None
    file_url: Optional[str] = None


class A2AMessage(BaseModel):
    """Message in A2A protocol format"""
    kind: Literal["message"] = "message"
    role: Literal["user", "agent", "system"]
    parts: List[MessagePart]
    messageId: Optional[str] = None
    taskId: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class PushNotificationConfig(BaseModel):
    """Configuration for push notifications"""
    url: str
    token: str
    authentication: Optional[Dict[str, Any]] = None


class Configuration(BaseModel):
    """Configuration for agent execution"""
    acceptedOutputModes: Optional[List[str]] = Field(default_factory=lambda: ["text/plain"])
    historyLength: Optional[int] = 0
    pushNotificationConfig: Optional[PushNotificationConfig] = None
    blocking: Optional[bool] = True


class MessageSendParams(BaseModel):
    """Parameters for message/send method"""
    message: A2AMessage
    configuration: Optional[Configuration] = Field(default_factory=Configuration)


class JSONRPCRequest(BaseModel):
    """JSON-RPC 2.0 request"""
    jsonrpc: Literal["2.0"] = "2.0"
    id: Optional[str] = ""
    method: Optional[str] = None
    params: Optional[MessageSendParams] = None


class StatusMessage(BaseModel):
    """Status message in response"""
    kind: Literal["message"] = "message"
    role: Literal["agent"] = "agent"
    parts: List[MessagePart]
    messageId: str
    taskId: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class Status(BaseModel):
    """Task status"""
    state: Literal["completed", "failed", "processing"] = "completed"
    timestamp: str
    message: StatusMessage


class Artifact(BaseModel):
    """Output artifact"""
    artifactId: str
    name: str
    parts: List[MessagePart]


class TaskResult(BaseModel):
    """Result of a task execution"""
    id: str  # task ID
    contextId: str  # conversation/session ID
    status: Status
    artifacts: List[Artifact] = Field(default_factory=list)
    history: List[A2AMessage] = Field(default_factory=list)
    kind: Literal["task"] = "task"


class JSONRPCResponse(BaseModel):
    """JSON-RPC 2.0 response"""
    jsonrpc: Literal["2.0"] = "2.0"
    id: str
    result: TaskResult



class MessageContent(BaseModel):
    """Content of a message (simple format)"""
    type: str = "text"
    text: str


class Message(BaseModel):
    """Message from Telex.im (simple format)"""
    role: str
    content: List[MessageContent]


class AgentRequest(BaseModel):
    """Request payload (simple format)"""
    messages: List[Message]
    agent_id: Optional[str] = None
    conversation_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class AgentResponse(BaseModel):
    """Response payload (simple format)"""
    role: str = "assistant"
    content: List[MessageContent]
    metadata: Optional[Dict[str, Any]] = None


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    agent: str
    version: str
    timestamp: str
    ai_provider: Optional[str] = None


class ErrorResponse(BaseModel):
    """Error response"""
    error: str
    detail: Optional[str] = None
    timestamp: str
