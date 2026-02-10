"""
Configuration module for University FAQ Assistant
Handles all settings, API keys, and model configurations
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ============================================
# PROJECT PATHS
# ============================================
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
PDF_DIR = DATA_DIR / "pdfs"
VECTOR_DB_DIR = DATA_DIR / "vector_db"

# Create directories if they don't exist
PDF_DIR.mkdir(parents=True, exist_ok=True)
VECTOR_DB_DIR.mkdir(parents=True, exist_ok=True)

# ============================================
# LLM CONFIGURATION
# ============================================
# Choose LLM provider: "openai" or "huggingface"
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-ada-002")

# HuggingFace Configuration (fallback for free option)
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY", "")
HUGGINGFACE_MODEL = os.getenv("HUGGINGFACE_MODEL", "gpt2")
HUGGINGFACE_EMBEDDING_MODEL = os.getenv("HUGGINGFACE_EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

# ============================================
# DOCUMENT PROCESSING CONFIGURATION
# ============================================
# Text chunking parameters
CHUNK_SIZE = 500  # Characters per chunk (reduced for GPT-2)
CHUNK_OVERLAP = 100  # Overlap between chunks

# Compression parameters
ENABLE_COMPRESSION = False  # Enable document compression (summarization) - Disabled for faster initial setup
COMPRESSION_RATIO = 0.5  # Target compression ratio for summaries

# ============================================
# RAG CONFIGURATION
# ============================================
# Number of relevant chunks to retrieve
TOP_K_RETRIEVAL = 2  # Reduced for GPT-2's 1024 token limit

# Temperature for LLM generation (0.0 = deterministic, 1.0 = creative)
GENERATION_TEMPERATURE = 0.3

# Maximum output tokens
MAX_OUTPUT_TOKENS = 500

# ============================================
# SYSTEM PROMPTS
# ============================================
COMPRESSION_PROMPT_TEMPLATE = """You are a text summarization expert. Summarize the following text concisely while preserving all key information, facts, dates, and important details.

Text to summarize:
{text}

Summary:"""

RAG_SYSTEM_PROMPT = """You are a helpful university FAQ assistant. Your role is to answer student questions based ONLY on the provided university documents.

Rules:
1. Answer based ONLY on the context provided
2. If the answer is not in the context, say: "I don't have that information in the provided documents. Please contact the university office for assistance."
3. Be concise and accurate
4. If you mention dates, policies, or specific information, cite it from the context
5. Be friendly and helpful in tone

Context:
{context}

Question: {question}

Answer:"""

# ============================================
# VALIDATION
# ============================================
def validate_config():
    """Validate configuration and check for required API keys"""
    warnings = []
    
    if LLM_PROVIDER == "openai" and not OPENAI_API_KEY:
        warnings.append("⚠️ OpenAI API key not found. Set OPENAI_API_KEY in .env file or use HUGGINGFACE provider.")
    
    if LLM_PROVIDER == "huggingface" and not HUGGINGFACE_API_KEY:
        warnings.append("ℹ️ HuggingFace API key not set. Local models will be used (requires more resources).")
    
    if not PDF_DIR.exists():
        warnings.append(f"⚠️ PDF directory not found: {PDF_DIR}")
    
    return warnings

# ============================================
# MODEL CONFIGURATION
# ============================================
def get_llm_config():
    """Return LLM configuration based on selected provider"""
    if LLM_PROVIDER == "openai":
        return {
            "provider": "openai",
            "model": OPENAI_MODEL,
            "api_key": OPENAI_API_KEY,
            "temperature": GENERATION_TEMPERATURE,
            "max_tokens": MAX_OUTPUT_TOKENS
        }
    else:  # huggingface
        return {
            "provider": "huggingface",
            "model": HUGGINGFACE_MODEL,
            "api_key": HUGGINGFACE_API_KEY,
            "temperature": GENERATION_TEMPERATURE,
            "max_tokens": MAX_OUTPUT_TOKENS
        }

def get_embedding_config():
    """Return embedding configuration based on selected provider"""
    if LLM_PROVIDER == "openai":
        return {
            "provider": "openai",
            "model": OPENAI_EMBEDDING_MODEL,
            "api_key": OPENAI_API_KEY
        }
    else:  # huggingface
        return {
            "provider": "huggingface",
            "model": HUGGINGFACE_EMBEDDING_MODEL
        }
