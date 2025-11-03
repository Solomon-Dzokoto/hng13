from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
import logging
from typing import Optional
import asyncio

from config import settings
from schemas import (
    AgentRequest, 
    AgentResponse, 
    MessageContent, 
    HealthResponse,
    ErrorResponse,
    JSONRPCRequest,
    JSONRPCResponse,
    TaskResult,
    Status,
    StatusMessage,
    Artifact,
    MessagePart,
    A2AMessage
)
from agent import get_agent
import uuid

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


app = FastAPI(
    title="Code Review Assistant - Telex.im AI Agent",
    description="An AI-powered code review assistant that helps developers improve their code",
    version=settings.agent_version,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal Server Error",
            detail=str(exc),
            timestamp=datetime.utcnow().isoformat()
        ).model_dump()
    )


@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint - Health check"""
    return HealthResponse(
        status="healthy",
        agent=settings.agent_name,
        version=settings.agent_version,
        timestamp=datetime.utcnow().isoformat()
    )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        agent=settings.agent_name,
        version=settings.agent_version,
        timestamp=datetime.utcnow().isoformat()
    )


# @app.post("/a2a/agent/codeReviewAssistant", response_model=AgentResponse)
# async def agent_endpoint(request: AgentRequest):
#     """
#     Main A2A protocol endpoint for Telex.im integration
    
#     This endpoint receives messages from Telex.im, processes them through
#     the AI agent, and returns a response in the A2A format.
#     """
#     try:
#         logger.info(f"Received request with {len(request.messages)} messages")
        
#         # Validate request
#         if not request.messages:
#             raise HTTPException(
#                 status_code=400,
#                 detail="No messages provided in request"
#             )
        
#         # Get agent instance (may initialize on first call)
#         logger.info("Getting agent instance...")
#         code_agent = get_agent()
#         logger.info("Agent ready, processing message...")
        
#         # Process message through AI agent with timeout
#         try:
#             response_text = await asyncio.wait_for(
#                 code_agent.process_message(request.messages),
#                 timeout=60.0  # 60 second timeout
#             )
#         except asyncio.TimeoutError:
#             logger.error("Agent message processing timed out after 60 seconds")
#             raise HTTPException(
#                 status_code=504,
#                 detail="Agent processing timed out. Please try again."
#             )
        
#         # Format response according to A2A protocol
#         response = AgentResponse(
#             role="assistant",
#             content=[
#                 MessageContent(
#                     type="text",
#                     text=response_text
#                 )
#             ],
#             metadata={
#                 "agent": settings.agent_name,
#                 "version": settings.agent_version,
#                 "timestamp": datetime.utcnow().isoformat()
#             }
#         )
        
#         logger.info(f"Sending response: {len(response_text)} characters")
#         return response
        
#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"Error processing request: {str(e)}", exc_info=True)
#         raise HTTPException(
#             status_code=500,
#             detail=f"Error processing request: {str(e)}"
#         )


@app.post("/chat", response_model=AgentResponse)
async def chat_endpoint(request: AgentRequest):
    """
    Alternative chat endpoint for testing
    Same functionality as the A2A endpoint
    """
    return await agent_endpoint(request)


@app.get("/info")
async def agent_info():
    """Get information about the agent"""
    return {
        "name": settings.agent_name,
        "version": settings.agent_version,
        "description": "AI-powered code review assistant that helps developers improve their code quality",
        "capabilities": [
            "Code review and analysis",
            "Bug detection",
            "Best practices suggestions",
            "Code explanation",
            "Performance optimization tips",
            "Multi-language support"
        ],
        "supported_languages": [
            "Python", "JavaScript", "TypeScript", "Java", "Go", 
            "Rust", "C++", "C#", "Ruby", "PHP", "Swift", "Kotlin"
        ],
        "endpoints": {
            "a2a_jsonrpc": "/a2a/lingflow",
            "a2a": "/a2a/agent/codeReviewAssistant",
            "chat": "/chat",
            "health": "/health",
            "info": "/info"
        }
    }


@app.post("/a2a/agent/codeReviewAssistant", response_model=JSONRPCResponse)
async def jsonrpc_a2a_endpoint(raw_request: Request):
    """
    JSON-RPC 2.0 A2A protocol endpoint (Telex.im spec compliant)
   
    
    Returns proper JSON-RPC response with task, status, artifacts, and history
    """
    try:
        # Parse JSON body
        try:
            body = await raw_request.json()
        except Exception:
            body = {}
        
        # Parse as JSON-RPC request
        try:
            rpc_request = JSONRPCRequest(**body)
        except Exception:
            rpc_request = JSONRPCRequest(id="", method=None, params=None)
        
        request_id = rpc_request.id or ""
        task_id = str(uuid.uuid4())
        context_id = str(uuid.uuid4())
        message_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat() + "Z"
        
        # Handle unknown/missing method
        if not rpc_request.method or rpc_request.method not in ["message/send", "help"]:
            error_text = "Unknown method. Use 'message/send' or 'help'."
            return JSONRPCResponse(
                id=request_id,
                result=TaskResult(
                    id=task_id,
                    contextId=context_id,
                    status=Status(
                        state="failed",
                        timestamp=timestamp,
                        message=StatusMessage(
                            messageId=message_id,
                            parts=[MessagePart(kind="text", text=error_text)]
                        )
                    ),
                    artifacts=[
                        Artifact(
                            artifactId=str(uuid.uuid4()),
                            name="assistantResponse",
                            parts=[MessagePart(kind="text", text=error_text)]
                        )
                    ],
                    history=[]
                )
            )
        
        # Handle help method
        if rpc_request.method == "help":
            help_text = f"{settings.agent_name}: AI-powered code review assistant. Send code via 'message/send' method."
            return JSONRPCResponse(
                id=request_id,
                result=TaskResult(
                    id=task_id,
                    contextId=context_id,
                    status=Status(
                        state="completed",
                        timestamp=timestamp,
                        message=StatusMessage(
                            messageId=message_id,
                            taskId=task_id,
                            parts=[MessagePart(kind="text", text=help_text)]
                        )
                    ),
                    artifacts=[
                        Artifact(
                            artifactId=str(uuid.uuid4()),
                            name="assistantResponse",
                            parts=[MessagePart(kind="text", text=help_text)]
                        )
                    ],
                    history=[]
                )
            )
        
        # Handle message/send
        if not rpc_request.params or not rpc_request.params.message:
            error_text = "Missing message in params."
            return JSONRPCResponse(
                id=request_id,
                result=TaskResult(
                    id=task_id,
                    contextId=context_id,
                    status=Status(
                        state="failed",
                        timestamp=timestamp,
                        message=StatusMessage(
                            messageId=message_id,
                            parts=[MessagePart(kind="text", text=error_text)]
                        )
                    ),
                    artifacts=[
                        Artifact(
                            artifactId=str(uuid.uuid4()),
                            name="assistantResponse",
                            parts=[MessagePart(kind="text", text=error_text)]
                        )
                    ],
                    history=[]
                )
            )
        
        user_message = rpc_request.params.message
        
        # Extract text from parts
        user_text = " ".join([
            part.text for part in user_message.parts 
            if part.kind == "text" and part.text
        ])
        
        if not user_text:
            user_text = "No text provided"
        
        logger.info(f"JSON-RPC message/send: {user_text[:100]}...")
        
        # Get agent and process
        code_agent = get_agent()
        
        # Convert to simple Message format for agent processing
        from schemas import Message, MessageContent as SimpleContent
        simple_messages = [Message(role="user", content=[SimpleContent(type="text", text=user_text)])]
        
        # Process with timeout
        try:
            response_text = await asyncio.wait_for(
                code_agent.process_message(simple_messages),
                timeout=60.0
            )
        except asyncio.TimeoutError:
            response_text = "Agent processing timed out. Please try again with a smaller request."
            state = "failed"
        else:
            state = "completed"
        
        # Build response
        response_message_id = str(uuid.uuid4())
        
        return JSONRPCResponse(
            id=request_id,
            result=TaskResult(
                id=task_id,
                contextId=context_id,
                status=Status(
                    state=state,
                    timestamp=datetime.utcnow().isoformat() + "Z",
                    message=StatusMessage(
                        messageId=response_message_id,
                        taskId=task_id,
                        parts=[MessagePart(kind="text", text=response_text)]
                    )
                ),
                artifacts=[
                    Artifact(
                        artifactId=str(uuid.uuid4()),
                        name="codeReview",
                        parts=[MessagePart(kind="text", text=response_text)]
                    )
                ],
                history=[
                    user_message,
                    A2AMessage(
                        role="agent",
                        parts=[MessagePart(kind="text", text=response_text)],
                        messageId=response_message_id,
                        taskId=task_id
                    )
                ]
            )
        )
        
    except Exception as e:
        logger.error(f"Error in JSON-RPC endpoint: {str(e)}", exc_info=True)
        # Return 200 with error in result (per spec)
        return JSONRPCResponse(
            id=request_id if 'request_id' in locals() else "",
            result=TaskResult(
                id=str(uuid.uuid4()),
                contextId=str(uuid.uuid4()),
                status=Status(
                    state="failed",
                    timestamp=datetime.utcnow().isoformat() + "Z",
                    message=StatusMessage(
                        messageId=str(uuid.uuid4()),
                        parts=[MessagePart(kind="text", text=f"Internal error: {str(e)}")]
                    )
                ),
                artifacts=[],
                history=[]
            )
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=True
    )
