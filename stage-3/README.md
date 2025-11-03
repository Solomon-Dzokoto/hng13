# Code Review Assistant - Telex.im AI Agent

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

An intelligent AI-powered code review assistant built for Telex.im using FastAPI. This agent helps developers improve their code quality by providing detailed reviews, bug detection, best practices suggestions, and code explanations.

## 🚀 Features

- **Intelligent Code Review**: Analyzes code snippets and provides constructive feedback
- **Bug Detection**: Identifies potential bugs, security issues, and edge cases
- **Best Practices**: Suggests improvements following industry standards
- **Code Explanation**: Explains complex code in simple terms
- **Performance Optimization**: Recommends performance improvements
- **Multi-Language Support**: Supports Python, JavaScript, TypeScript, Java, Go, Rust, C++, C#, Ruby, PHP, Swift, Kotlin, and more
- **A2A Protocol Integration**: Seamlessly integrates with Telex.im using Agent-to-Agent protocol
- **Powered by Google Gemini**: Uses Google's latest Gemini AI model

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Agent](#running-the-agent)
- [API Endpoints](#api-endpoints)
- [Telex.im Integration](#telexim-integration)
- [Deployment](#deployment)
- [Usage Examples](#usage-examples)
- [Testing](#testing)
- [Architecture](#architecture)
- [Contributing](#contributing)

## 🔧 Prerequisites

- Python 3.11 or higher
- pip (Python package manager)
- A Google Gemini API key
- Access to Telex.im organization (run `/telex-invite your-email@example.com`)

## 📦 Installation

1. **Clone the repository or navigate to the stage-3 directory**:
```bash
cd stage-3
```

2. **Create a virtual environment** (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

## ⚙️ Configuration

1. **Copy the example environment file**:
```bash
cp .env.example .env
```

2. **Edit the `.env` file with your configuration**:

```env
# Required: Google Gemini API key
GEMINI_API_KEY=your-gemini-api-key-here

# Gemini model (optional, defaults to gemini-1.5-flash)
GEMINI_MODEL=gemini-1.5-flash

# Server Configuration (optional)
HOST=0.0.0.0
PORT=8000
```

### Getting Your Gemini API Key:

1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Get API Key"
4. Create a new API key or use an existing one
5. Copy the API key and add it to your `.env` file

## 🏃 Running the Agent

### Development Mode

```bash
# Using the start script
chmod +x start.sh
./start.sh

# Or directly with uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### Production Mode

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Using Docker

```bash
# Build the image
docker build -t code-review-assistant .

# Run the container
docker run -p 8000:8000 --env-file .env code-review-assistant
```

## 📡 API Endpoints

### Health Check
```
GET /
GET /health
```
Returns the agent's health status and configuration.

**Response:**
```json
{
  "status": "healthy",
  "agent": "CodeReviewAssistant",
  "version": "1.0.0",
  "timestamp": "2025-11-01T15:30:00.000Z",
  "ai_provider": "gemini"
}
```

### Agent Information
```
GET /info
```
Returns detailed information about the agent's capabilities.

### Main A2A Endpoint (Telex.im Integration)
```
POST /a2a/agent/codeReviewAssistant
```

**Request Body:**
```json
{
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": "Review this Python code:\n\ndef calculate_average(numbers):\n    return sum(numbers) / len(numbers)"
        }
      ]
    }
  ]
}
```

**Response:**
```json
{
  "role": "assistant",
  "content": [
    {
      "type": "text",
      "text": "Here's my review of your Python code:\n\n**Identified Issues:**\n1. **ZeroDivisionError Risk**: The function will crash if an empty list is passed...\n\n**Suggestions:**\n```python\ndef calculate_average(numbers):\n    if not numbers:\n        return 0\n    return sum(numbers) / len(numbers)\n```"
    }
  ],
  "metadata": {
    "agent": "CodeReviewAssistant",
    "version": "1.0.0",
    "timestamp": "2025-11-01T15:30:00.000Z"
  }
}
```

### Alternative Chat Endpoint
```
POST /chat
```
Same functionality as the A2A endpoint, useful for testing.

## 🔗 Telex.im Integration

### Step 1: Deploy Your Agent

Deploy your agent to a public URL. Options include:
- **Render**: [render.com](https://render.com)
- **Railway**: [railway.app](https://railway.app)
- **Heroku**: [heroku.com](https://heroku.com)
- **AWS/GCP/Azure**: Cloud platforms
- **ngrok**: For local testing

### Step 2: Update workflow.json

Edit `workflow.json` and replace `YOUR_DEPLOYMENT_URL` with your actual deployment URL:

```json
{
  "url": "https://your-agent.render.com/a2a/agent/codeReviewAssistant"
}
```

### Step 3: Register with Telex.im

1. Log in to [telex.im](https://telex.im)
2. Navigate to the agent configuration page
3. Upload your `workflow.json` file
4. Test the integration

### Step 4: Monitor Agent Logs

View your agent's interactions:
```
https://api.telex.im/agent-logs/{channel-id}.txt
```

Get your `channel-id` from the Telex.im URL bar.

## 🚀 Deployment

### Deploy to Render

1. Create a new Web Service on [Render](https://render.com)
2. Connect your GitHub repository
3. Configure:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Add environment variables from your `.env` file
5. Deploy!

### Deploy to Railway

1. Install Railway CLI or use the web dashboard
2. Run `railway init`
3. Add environment variables
4. Run `railway up`

### Deploy with Docker

```bash
# Build
docker build -t code-review-assistant .

# Run
docker run -d -p 8000:8000 \
  -e GEMINI_API_KEY=your-key \
  code-review-assistant
```

## 💡 Usage Examples

### Example 1: Code Review

**User**: "Can you review this code?"
```python
def process_data(data):
    result = []
    for item in data:
        if item > 0:
            result.append(item * 2)
    return result
```

**Agent Response**: Provides detailed analysis including:
- Use of list comprehension for better performance
- Edge case handling
- Type hints suggestion
- Documentation recommendations

### Example 2: Bug Detection

**User**: "Find bugs in this JavaScript code"
```javascript
function getUserById(id) {
  const user = users.find(u => u.id = id);
  return user.name;
}
```

**Agent Response**: Identifies:
- Assignment operator (`=`) instead of comparison (`===`)
- Potential null/undefined error
- Suggests null checking

### Example 3: Code Explanation

**User**: "Explain what this does"
```python
result = [x**2 for x in range(10) if x % 2 == 0]
```

**Agent Response**: Clear explanation of list comprehension, filtering, and squaring even numbers.

## 🧪 Testing

### Test with curl

```bash
# Health check
curl http://localhost:8000/health

# Test agent endpoint
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "role": "user",
        "content": [{"type": "text", "text": "Review this: def add(a,b): return a+b"}]
      }
    ]
  }'
```

### Test with Python

```python
import requests

response = requests.post(
    "http://localhost:8000/chat",
    json={
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Review this Python function: def divide(a, b): return a / b"
                    }
                ]
            }
        ]
    }
)

print(response.json())
```

### Interactive Testing

Visit the auto-generated API documentation:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🏗️ Architecture

```
stage-3/
├── main.py              # FastAPI application and endpoints
├── agent.py             # AI agent core logic
├── config.py            # Configuration management
├── schemas.py           # Pydantic models for request/response
├── requirements.txt     # Python dependencies
├── workflow.json        # Telex.im workflow configuration
├── Dockerfile           # Docker container configuration
├── Procfile            # Process file for deployment
├── start.sh            # Startup script
├── .env.example        # Environment variables template
└── README.md           # This file
```

### Key Components:

1. **main.py**: FastAPI application with A2A protocol endpoints
2. **agent.py**: Core AI logic with Google Gemini integration
3. **config.py**: Environment configuration using pydantic-settings
4. **schemas.py**: Request/response models ensuring type safety
5. **workflow.json**: Telex.im integration configuration

## 🔒 Security Considerations

- Store API keys securely in environment variables
- Never commit `.env` files to version control
- Use HTTPS in production
- Implement rate limiting for public deployments
- Validate and sanitize all inputs
- Monitor API usage and costs

## 🐛 Troubleshooting

### Agent not responding
- Check API key is valid and has credits
- Verify network connectivity
- Check logs for error messages

### Deployment issues
- Ensure all environment variables are set
- Check port configuration
- Verify dependencies are installed

### Integration issues
- Confirm workflow.json URL is correct and accessible
- Test A2A endpoint independently
- Check Telex.im agent logs

## 📝 Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GEMINI_API_KEY` | Yes | - | Google Gemini API key |
| `GEMINI_MODEL` | No | gemini-1.5-flash | Gemini model to use |
| `HOST` | No | 0.0.0.0 | Server host |
| `PORT` | No | 8000 | Server port |
| `AGENT_NAME` | No | CodeReviewAssistant | Agent name |
| `AGENT_VERSION` | No | 1.0.0 | Agent version |

## 📄 License

This project is licensed under the MIT License.

## 👥 Author

Built for HNG13 Stage 3 Backend Task

## 🙏 Acknowledgments

- Telex.im for the A2A protocol
- FastAPI for the excellent web framework
- Google for Gemini AI capabilities
- HNG Internship program

## 📞 Support

For issues or questions:
- Check the troubleshooting section
- Review the API documentation at `/docs`
- Test with the provided examples

---

**Built with ❤️ for the HNG13 Internship Program**
