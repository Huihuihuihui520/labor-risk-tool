import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    api_key: str = os.getenv("API_KEY", "YOUR_API_KEY")
    api_base: str = os.getenv("API_BASE", "https://dashscope.aliyuncs.com/compatible-mode/v1")
    model_name: str = os.getenv("MODEL_NAME", "deepseek-chat")
    
    class Config:
        env_file = ".env"

settings = Settings()
