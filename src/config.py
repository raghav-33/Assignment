import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_groq import ChatGroq

# Project root directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env
load_dotenv(BASE_DIR / ".env")

# LLM configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Project directories
DATA_DIR = BASE_DIR / "data"
WORKFLOW_FILE = DATA_DIR / "AI_Agent_Workflow_Assessment.xlsx"

# Routing LLM
def routing_llm():
    """Initializes and returns a Routing llm."""
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    
    if not GROQ_API_KEY:
        raise ValueError( "GROQ_API_KEY is not set. Please provide a valid API key in your .env file.")
    
    llm = ChatGroq(model="openai/gpt-oss-120b",
                   temperature=0.0,
                   api_key=GROQ_API_KEY)
    
    return llm



