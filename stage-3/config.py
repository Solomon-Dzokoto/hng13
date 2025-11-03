from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # API Keys
    gemini_api_key: str = ""
    
    # AI Provider Configuration
    gemini_model: str = "models/gemini-2.5-flash"
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Agent Configuration
    agent_name: str = "CodeReviewAssistant"
    agent_version: str = "1.0.0"
    ai_provider: str = "gemini"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
