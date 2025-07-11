import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('config/.env_llm')

class LLMConfig:
    """Configuration settings for the LLM Decision Engine"""
    
    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    MODEL_NAME = os.getenv('MODEL_NAME', 'gpt-4o-mini')
    MAX_TOKENS = int(os.getenv('MAX_TOKENS', '800'))
    CONFIDENCE_THRESHOLD = float(os.getenv('CONFIDENCE_THRESHOLD', '0.75'))
    
    # Temperature Settings - Different for different functions
    EXTRACTION_TEMPERATURE = float(os.getenv('EXTRACTION_TEMPERATURE', '0.5'))
    NAVIGATION_TEMPERATURE = float(os.getenv('NAVIGATION_TEMPERATURE', '0.0'))
    QUESTION_TEMPERATURE = float(os.getenv('QUESTION_TEMPERATURE', '0.3'))
    
    # Conversation Settings
    MAX_CONVERSATION_TURNS = int(os.getenv('MAX_CONVERSATION_TURNS', '10'))
    
    # System Settings
    DEBUG_MODE = os.getenv('DEBUG_MODE', 'True').lower() == 'true'
    
    @classmethod
    def validate_config(cls):
        """Validate that required configuration is present"""
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is required")
        
        if cls.CONFIDENCE_THRESHOLD < 0 or cls.CONFIDENCE_THRESHOLD > 1:
            raise ValueError("CONFIDENCE_THRESHOLD must be between 0 and 1")

class Paths:
    """File and directory paths"""
    
    # Base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Data files
    DATA_DIR = os.path.join(BASE_DIR, 'data')
    CUSTOMER_DATA_FILE = os.path.join(DATA_DIR, 'customer_data.json')
    
    # Log files
    LOGS_DIR = os.path.join(BASE_DIR, 'logs')
    CONVERSATION_LOGS_DIR = os.path.join(LOGS_DIR, 'conversations')
    
    @classmethod
    def ensure_directories(cls):
        """Ensure required directories exist"""
        os.makedirs(cls.DATA_DIR, exist_ok=True)
        os.makedirs(cls.LOGS_DIR, exist_ok=True)
        os.makedirs(cls.CONVERSATION_LOGS_DIR, exist_ok=True)