"""
Utility functions for the University FAQ Assistant
Contains helper functions for text processing, model initialization, etc.
"""

import os
import re
from typing import List, Dict, Any
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.llms import HuggingFaceHub
from langchain_core.prompts import PromptTemplate
import config


def clean_text(text: str) -> str:
    """
    Clean extracted text from PDFs
    
    Args:
        text: Raw text from PDF
    
    Returns:
        Cleaned text
    """
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s.,!?;:()\-\'"]+', '', text)
    
    # Remove multiple consecutive punctuation
    text = re.sub(r'([.,!?;:]){2,}', r'\1', text)
    
    return text.strip()


def create_text_splitter(chunk_size: int = None, chunk_overlap: int = None):
    """
    Create a text splitter for chunking documents
    
    Args:
        chunk_size: Size of each chunk (default from config)
        chunk_overlap: Overlap between chunks (default from config)
    
    Returns:
        RecursiveCharacterTextSplitter instance
    """
    chunk_size = chunk_size or config.CHUNK_SIZE
    chunk_overlap = chunk_overlap or config.CHUNK_OVERLAP
    
    return RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""]
    )


def initialize_embeddings():
    """
    Initialize embedding model based on configuration
    
    Returns:
        Embeddings instance (OpenAI or HuggingFace)
    """
    embedding_config = config.get_embedding_config()
    
    try:
        if embedding_config["provider"] == "openai":
            if not embedding_config["api_key"]:
                raise ValueError("OpenAI API key not provided")
            
            return OpenAIEmbeddings(
                model=embedding_config["model"],
                openai_api_key=embedding_config["api_key"]
            )
        else:  # huggingface
            print(f"Loading HuggingFace embedding model: {embedding_config['model']}")
            return HuggingFaceEmbeddings(
                model_name=embedding_config["model"],
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': True}
            )
    except Exception as e:
        print(f"Error initializing embeddings: {e}")
        print("Falling back to HuggingFace embeddings...")
        return HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )


def initialize_llm():
    """
    Initialize LLM based on configuration
    
    Returns:
        LLM instance (OpenAI or HuggingFace)
    """
    llm_config = config.get_llm_config()
    
    try:
        if llm_config["provider"] == "openai":
            if not llm_config["api_key"]:
                raise ValueError("OpenAI API key not provided")
            
            return ChatOpenAI(
                model=llm_config["model"],
                openai_api_key=llm_config["api_key"],
                temperature=llm_config["temperature"],
                max_tokens=llm_config["max_tokens"]
            )
        else:  # huggingface
            print(f"Loading HuggingFace model: {llm_config['model']}")
            
            if llm_config["api_key"]:
                return HuggingFaceHub(
                    repo_id=llm_config["model"],
                    huggingfacehub_api_token=llm_config["api_key"],
                    model_kwargs={
                        "temperature": llm_config["temperature"],
                        "max_length": llm_config["max_tokens"]
                    }
                )
            else:
                # Use local HuggingFace model without API
                from langchain_community.llms import HuggingFacePipeline
                from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
                import torch
                
                print(f"Loading model: {llm_config['model']}")
                
                # Load model and tokenizer for T5 (seq2seq model)
                tokenizer = AutoTokenizer.from_pretrained(llm_config["model"])
                model = AutoModelForSeq2SeqLM.from_pretrained(
                    llm_config["model"],
                    torch_dtype=torch.float32,
                    device_map="auto" if torch.cuda.is_available() else None
                )
                
                pipe = pipeline(
                    "text2text-generation",
                    model=model,
                    tokenizer=tokenizer,
                    max_length=256,  # Flan-T5 can handle longer outputs
                    temperature=0.7,
                    do_sample=True,
                    truncation=True
                )
                
                return HuggingFacePipeline(pipeline=pipe)
    except Exception as e:
        print(f"Error initializing LLM: {e}")
        raise


def compress_text(text: str, llm) -> str:
    """
    Compress/summarize text using LLM
    This simulates the ScaleDown compression technique
    
    Args:
        text: Original text to compress
        llm: Language model instance
    
    Returns:
        Compressed/summarized text
    """
    if not config.ENABLE_COMPRESSION:
        return text
    
    # Skip compression for very short texts
    if len(text) < 200:
        return text
    
    try:
        prompt_text = config.COMPRESSION_PROMPT_TEMPLATE.format(text=text)
        
        # Invoke LLM directly
        compressed = llm.invoke(prompt_text)
        
        # Handle different response types
        if hasattr(compressed, 'content'):
            return compressed.content.strip()
        else:
            return str(compressed).strip()
    except Exception as e:
        print(f"Error compressing text: {e}")
        # Fallback: simple truncation if compression fails
        target_length = int(len(text) * config.COMPRESSION_RATIO)
        return text[:target_length] + "..."


def format_source_documents(docs: List[Any]) -> str:
    """
    Format source documents for display
    
    Args:
        docs: List of retrieved documents
    
    Returns:
        Formatted string with source information
    """
    if not docs:
        return ""
    
    sources = []
    for i, doc in enumerate(docs, 1):
        source = doc.metadata.get('source', 'Unknown')
        source_name = os.path.basename(source)
        page = doc.metadata.get('page', 'N/A')
        sources.append(f"{i}. {source_name} (Page {page})")
    
    return "\n".join(sources)


def validate_question(question: str) -> tuple[bool, str]:
    """
    Validate user question
    
    Args:
        question: User input question
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not question or not question.strip():
        return False, "Please enter a question"
    
    if len(question.strip()) < 3:
        return False, "Question is too short. Please provide more details."
    
    if len(question) > 1000:
        return False, "Question is too long. Please keep it under 1000 characters."
    
    return True, ""


def get_vector_store_path() -> str:
    """
    Get the path to the FAISS vector store
    
    Returns:
        Path to vector store directory
    """
    return str(config.VECTOR_DB_DIR / "faiss_index")


def check_vector_store_exists() -> bool:
    """
    Check if vector store has been created
    
    Returns:
        True if vector store exists, False otherwise
    """
    vector_store_path = get_vector_store_path()
    index_file = os.path.join(vector_store_path, "index.faiss")
    pkl_file = os.path.join(vector_store_path, "index.pkl")
    
    return os.path.exists(index_file) and os.path.exists(pkl_file)


def count_pdf_files() -> int:
    """
    Count number of PDF files in the data directory
    
    Returns:
        Number of PDF files
    """
    if not config.PDF_DIR.exists():
        return 0
    
    return len(list(config.PDF_DIR.glob("*.pdf")))
