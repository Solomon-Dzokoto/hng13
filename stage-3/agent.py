import logging
from typing import List, Optional
import google.generativeai as genai
from config import settings
from schemas import Message, MessageContent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CodeReviewAgent:
    """AI Agent that performs code reviews and provides development assistance"""
    
    SYSTEM_PROMPT = """You are an expert Code Review Assistant helping developers on Telex.im.

Your capabilities:
1. **Code Review**: Analyze code snippets and provide constructive feedback
2. **Bug Detection**: Identify potential bugs, security issues, and edge cases
3. **Best Practices**: Suggest improvements following industry standards
4. **Code Explanation**: Explain what code does in clear, simple terms
5. **Optimization**: Recommend performance improvements
6. **Language Support**: Support multiple programming languages (Python, JavaScript, TypeScript, Java, Go, Rust, C++, etc.)

When reviewing code:
- Be constructive and encouraging
- Provide specific examples and suggestions
- Explain WHY something should be changed
- Consider readability, maintainability, and performance
- Highlight both good practices and areas for improvement
- Format responses clearly with markdown

When users share code:
1. Identify the programming language
2. Analyze for bugs and issues
3. Check best practices
4. Suggest improvements
5. Explain complex parts if needed

If no code is provided, ask what they need help with or wait for code to be shared.
Keep responses concise but thorough."""

    def __init__(self):
        """Initialize the agent with Google Gemini"""
        if not settings.gemini_api_key:
            raise ValueError("Gemini API key not configured")
        
        genai.configure(api_key=settings.gemini_api_key)
        # Try to initialize the configured model. If it's not available for this account,
        # fall back to the first model that supports generateContent and warn in logs.
        try:
            # Try with system_instruction (newer API versions)
            try:
                self.model = genai.GenerativeModel(
                    model_name=settings.gemini_model,
                    system_instruction=self.SYSTEM_PROMPT,
                )
                self.use_system_instruction = True
            except TypeError:
                # Fall back to model without system_instruction (older API)
                logger.info("system_instruction not supported, will prepend to messages")
                self.model = genai.GenerativeModel(model_name=settings.gemini_model)
                self.use_system_instruction = False
        except Exception as e:
            logger.warning(
                f"Configured Gemini model '{settings.gemini_model}' not available: {e}. Listing available models to find a compatible fallback."
            )
            fallback = None
            try:
                for m in genai.list_models():
                    methods = getattr(m, "supported_generation_methods", [])
                    if "generateContent" in methods:
                        # m.name is of the form 'models/{model-id}'
                        fallback = m.name
                        break
            except Exception as e:
                logger.error(f"Failed to list Gemini models: {e}")

            if fallback:
                logger.info(f"Using fallback model: {fallback}")
                try:
                    self.model = genai.GenerativeModel(model_name=fallback, system_instruction=self.SYSTEM_PROMPT)
                    self.use_system_instruction = True
                except TypeError:
                    self.model = genai.GenerativeModel(model_name=fallback)
                    self.use_system_instruction = False
            else:
                raise
        self.chat = None
        logger.info(f"Initialized with Google Gemini model: {settings.gemini_model}")
    
    def _build_conversation_history(self, messages: List[Message]) -> List[dict]:
        """Build conversation history for Gemini"""
        history = []
        
        # If system_instruction not supported, prepend system prompt to first user message
        first_message = True
        
        for msg in messages[:-1]:  # All messages except the last one
            content = " ".join([c.text for c in msg.content if c.type == "text"])
            
            # Prepend system prompt to first user message if needed
            if first_message and msg.role == "user" and not self.use_system_instruction:
                content = f"{self.SYSTEM_PROMPT}\n\nUser: {content}"
                first_message = False
            
            role = "user" if msg.role == "user" else "model"
            history.append({
                "role": role,
                "parts": [content]
            })
        
        return history
    
    async def process_message(self, messages: List[Message]) -> str:
        """
        Process incoming messages and generate a response
        
        Args:
            messages: List of conversation messages
            
        Returns:
            AI-generated response text
        """
        try:
            # Get the conversation history (all messages except the last)
            history = self._build_conversation_history(messages)
            
            # Get the latest user message
            latest_message = messages[-1]
            user_input = " ".join([c.text for c in latest_message.content if c.type == "text"])
            
            # If this is the first message and no system_instruction, prepend system prompt
            if len(messages) == 1 and not self.use_system_instruction:
                user_input = f"{self.SYSTEM_PROMPT}\n\nUser: {user_input}"
            
            logger.info(f"Processing message with {len(messages)} messages in history")
            
            # Start a new chat with history or continue existing chat
            self.chat = self.model.start_chat(history=history)
            
            # Generate response
            response = self.chat.send_message(
                user_input,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=2000,
                )
            )
            
            result = response.text
            logger.info(f"Received response from Gemini: {len(result)} characters")
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return f"I encountered an error while processing your request: {str(e)}. Please try again."


# Global agent instance
agent = None


def get_agent() -> CodeReviewAgent:
    """Get or create the global agent instance"""
    global agent
    if agent is None:
        agent = CodeReviewAgent()
    return agent
