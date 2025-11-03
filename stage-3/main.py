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
    ErrorResponse
)
from agent import get_agent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
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
    allow_origins=["*"],  # Configure appropriately for production
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


@app.post("/a2a/agent/codeReviewAssistant", response_model=AgentResponse)
async def agent_endpoint(request: AgentRequest):
    """
    Main A2A protocol endpoint for Telex.im integration
    
    This endpoint receives messages from Telex.im, processes them through
    the AI agent, and returns a response in the A2A format.
    """
    try:
        logger.info(f"Received request with {len(request.messages)} messages")
        
        # Validate request
        if not request.messages:
            raise HTTPException(
                status_code=400,
                detail="No messages provided in request"
            )
        
        # Get agent instance (may initialize on first call)
        logger.info("Getting agent instance...")
        code_agent = get_agent()
        logger.info("Agent ready, processing message...")
        
        # Process message through AI agent with timeout
        try:
            response_text = await asyncio.wait_for(
                code_agent.process_message(request.messages),
                timeout=60.0  # 60 second timeout
            )
        except asyncio.TimeoutError:
            logger.error("Agent message processing timed out after 60 seconds")
            raise HTTPException(
                status_code=504,
                detail="Agent processing timed out. Please try again."
            )
        
        # Format response according to A2A protocol
        response = AgentResponse(
            role="assistant",
            content=[
                MessageContent(
                    type="text",
                    text=response_text
                )
            ],
            metadata={
                "agent": settings.agent_name,
                "version": settings.agent_version,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        
        logger.info(f"Sending response: {len(response_text)} characters")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error processing request: {str(e)}"
        )


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
            "a2a": "/a2a/agent/codeReviewAssistant",
            "chat": "/chat",
            "health": "/health",
            "info": "/info"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=True
    )
