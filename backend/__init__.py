"""
University FAQ Assistant - Backend Package
Handles document ingestion, RAG pipeline, and configuration
"""

__version__ = "1.0.0"
__author__ = "Intel Unnati Project"

from . import config
from . import utils
from .ingest import DocumentIngester
from .rag_pipeline import RAGPipeline, ChatSession

__all__ = [
    "config",
    "utils",
    "DocumentIngester",
    "RAGPipeline",
    "ChatSession"
]
