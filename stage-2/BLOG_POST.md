# Building a Code Review AI Agent for Telex.im with FastAPI

## Introduction

In this blog post, I'll walk you through my journey of building an intelligent Code Review Assistant AI agent for Telex.im as part of the HNG13 Stage 3 Backend Task. This agent leverages the power of large language models to help developers improve their code quality in real-time.

## The Challenge

The task was to build an AI agent that:
- Performs a useful function
- Integrates with Telex.im using the A2A (Agent-to-Agent) protocol
- Is well-architected and documented
- Handles errors gracefully

## Why a Code Review Assistant?

I chose to build a code review assistant because:

1. **High Value**: Code reviews are crucial but time-consuming. An AI assistant can provide instant feedback.
2. **Universal Need**: Every developer needs code reviewed, regardless of their language or framework.
3. **Complex Problem**: It showcases AI capabilities in understanding context, identifying bugs, and providing constructive feedback.
4. **Practical Application**: It solves a real problem that developers face daily.

## Technical Stack

- **Framework**: FastAPI (Python)
- **AI Provider**: Google Gemini 1.5 Flash
- **Protocol**: A2A (Agent-to-Agent) for Telex.im integration
- **Deployment**: Docker-ready with Procfile for easy deployment

## Architecture Overview

The agent consists of several key components:

### 1. Configuration Management (`config.py`)
I used `pydantic-settings` to manage configuration with Google Gemini:

```python
class Settings(BaseSettings):
    gemini_api_key: str = ""
    gemini_model: str = "gemini-1.5-flash"
    # ... other settings
```

### 2. Request/Response Schemas (`schemas.py`)
Defined Pydantic models ensuring type safety and validation:

```python
class AgentRequest(BaseModel):
    messages: List[Message]
    agent_id: Optional[str] = None
    conversation_id: Optional[str] = None
```

### 3. AI Agent Core (`agent.py`)
The heart of the application - a `CodeReviewAgent` class that:
- Processes messages from Telex.im
- Interfaces with Google Gemini
- Provides intelligent code analysis

Key features of the agent:
- **System Prompt Engineering**: Carefully crafted to ensure constructive, helpful reviews
- **Multi-language Support**: Works with Python, JavaScript, Java, Go, and more
- **Google Gemini Integration**: Leverages Gemini's powerful code understanding capabilities

### 4. FastAPI Application (`main.py`)
RESTful API with multiple endpoints:
- `/health` - Health check
- `/info` - Agent capabilities
- `/a2a/agent/codeReviewAssistant` - Main A2A endpoint for Telex.im
- `/chat` - Alternative endpoint for testing

## Implementation Highlights

### Prompt Engineering

The system prompt is crucial. I designed it to:
- Be constructive and encouraging
- Provide specific, actionable suggestions
- Explain the "why" behind recommendations
- Format responses with markdown for readability

```python
SYSTEM_PROMPT = """You are an expert Code Review Assistant...

When reviewing code:
- Be constructive and encouraging
- Provide specific examples and suggestions
- Explain WHY something should be changed
- Consider readability, maintainability, and performance
..."""
```

### Error Handling

Implemented comprehensive error handling:
- Global exception handler
- Input validation with Pydantic
- Graceful fallbacks when AI services fail
- Detailed logging for debugging

### A2A Protocol Compliance

The agent properly implements the A2A protocol expected by Telex.im:

```python
@app.post("/a2a/agent/codeReviewAssistant")
async def agent_endpoint(request: AgentRequest):
    response_text = await code_agent.process_message(request.messages)
    
    return AgentResponse(
        role="assistant",
        content=[MessageContent(type="text", text=response_text)],
        metadata={...}
    )
```

## Challenges and Solutions

### Challenge 1: Integrating Google Gemini
**Solution**: Utilized the google-generativeai library with proper conversation history management for context-aware responses.

### Challenge 2: Prompt Consistency
**Solution**: Careful prompt engineering with clear guidelines for the AI on how to format and structure responses.

### Challenge 3: Error Recovery
**Solution**: Implemented try-catch blocks at every integration point with meaningful error messages.

## Testing

Created a comprehensive test suite (`test_agent.py`) that validates:
- Health checks
- Agent info endpoints
- Code review functionality
- Bug detection capabilities
- A2A protocol compliance

Run tests with:
```bash
python test_agent.py
```

## Deployment

The agent is deployment-ready with:
- **Docker**: Containerized for consistent deployment
- **Procfile**: Heroku/Render compatible
- **Environment Variables**: Secure configuration management

Deploy to Render in 3 steps:
1. Push to GitHub
2. Connect to Render
3. Add environment variables

## Results and Capabilities

The final agent can:
- ✅ Review code in 12+ programming languages
- ✅ Identify bugs and security issues
- ✅ Suggest best practices and optimizations
- ✅ Explain complex code snippets
- ✅ Provide formatted, readable responses
- ✅ Integrate seamlessly with Telex.im

## Usage Example

**Input:**
```python
def calculate_average(numbers):
    return sum(numbers) / len(numbers)
```

**Agent Response:**
```
Here's my review of your Python code:

**Identified Issues:**
1. **ZeroDivisionError Risk**: The function will crash if an empty list is passed
2. **No Type Hints**: Missing type annotations
3. **No Documentation**: Missing docstring

**Suggestions:**
[detailed improvements with code examples]
```

## Lessons Learned

1. **Prompt Engineering is Critical**: The quality of AI responses heavily depends on prompt design
2. **Error Handling is Non-Negotiable**: AI services can fail; plan for it
3. **Documentation Matters**: Good docs make integration painless
4. **Test Early, Test Often**: Automated tests catch issues before deployment

## What's Next?

Future enhancements could include:
- Context awareness (remember previous conversations)
- Language-specific rule customization
- Integration with GitHub/GitLab for PR reviews
- Support for code diffs and suggestions
- Performance metrics and analytics

## Conclusion

Building this Code Review Assistant was an excellent exercise in:
- AI integration and prompt engineering
- RESTful API design with FastAPI
- Protocol implementation (A2A)
- Production-ready deployment practices

The agent is now live and helping developers improve their code quality on Telex.im!

## Resources

- **Repository**: [Link to your repo]
- **Live Demo**: [Your deployment URL]
- **Telex.im**: https://telex.im
- **HNG Internship**: https://hng.tech
- **Google AI Studio**: https://aistudio.google.com

## Tags

#AI #MachineLearning #FastAPI #Python #CodeReview #HNG13 #TelexIM #GoogleGemini #Automation

---

**Built for HNG13 Stage 3 Backend Task**

Connect with me: [Your social links]
