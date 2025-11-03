import logging
from typing import List, Optional
import google.generativeai as genai
from config import settings
from schemas import Message, MessageContent
import asyncio
from concurrent.futures import ThreadPoolExecutor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Thread pool for running blocking Gemini API calls
thread_pool = ThreadPoolExecutor(max_workers=10)


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
        
        logger.info(f"Initializing agent with model: {settings.gemini_model}")
        genai.configure(api_key=settings.gemini_api_key)
        
       
        try:
            # Try with system_instruction (newer API versions)
            try:
                logger.info("Attempting to create GenerativeModel with system_instruction...")
                self.model = genai.GenerativeModel(
                    model_name=settings.gemini_model,
                    system_instruction=self.SYSTEM_PROMPT,
                )
                self.use_system_instruction = True
                logger.info("✅ Model created with system_instruction support")
            except TypeError as te:
                # Fall back to model without system_instruction (older API)
                logger.info(f"system_instruction not supported ({te}), will prepend to messages")
                self.model = genai.GenerativeModel(model_name=settings.gemini_model)
                self.use_system_instruction = False
                logger.info("✅ Model created without system_instruction")
        except Exception as e:
            logger.warning(
                f"Configured Gemini model '{settings.gemini_model}' not available: {e}. Listing available models to find a compatible fallback."
            )
            fallback = None
            try:
                logger.info("Listing available Gemini models (this may take a moment)...")
                for m in genai.list_models():
                    methods = getattr(m, "supported_generation_methods", [])
                    if "generateContent" in methods:
                        # m.name is of the form 'models/{model-id}'
                        fallback = m.name
                        logger.info(f"Found compatible fallback model: {fallback}")
                        break
            except Exception as e2:
                logger.error(f"Failed to list Gemini models: {e2}")

            if fallback:
                logger.info(f"Using fallback model: {fallback}")
                try:
                    self.model = genai.GenerativeModel(model_name=fallback, system_instruction=self.SYSTEM_PROMPT)
                    self.use_system_instruction = True
                except TypeError:
                    self.model = genai.GenerativeModel(model_name=fallback)
                    self.use_system_instruction = False
                logger.info(f"✅ Fallback model initialized successfully")
            else:
                raise ValueError("No compatible Gemini model found for this account")
        
        self.chat = None
        logger.info(f"Agent initialization complete. Model: {settings.gemini_model}, system_instruction_support: {self.use_system_instruction}")
    
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
            
            
            loop = asyncio.get_event_loop()
            
          
            self.chat = await loop.run_in_executor(
                thread_pool,
                lambda: self.model.start_chat(history=history)
            )
            
            # Send message in thread pool with generation config
            response = await loop.run_in_executor(
                thread_pool,
                lambda: self.chat.send_message(
                    user_input,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.7,
                        max_output_tokens=2000,
                    )
                )
            )
            
            result = response.text
            logger.info(f"Received response from Gemini: {len(result)} characters")
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}", exc_info=True)
            return f"I encountered an error while processing your request: {str(e)}. Please try again."


# Global agent instance
agent = None


def get_agent() -> CodeReviewAgent:
    """Get or create the global agent instance"""
    global agent
    if agent is None:
        agent = CodeReviewAgent()
    return agent
