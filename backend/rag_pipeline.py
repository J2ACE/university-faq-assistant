"""
RAG Pipeline Module
Handles question answering using Retrieval-Augmented Generation
"""

from typing import Dict, List, Optional
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain_core.documents import Document

import config
import utils


class RAGPipeline:
    """
    Implements the complete RAG pipeline:
    1. Load vector store
    2. Accept user query
    3. Retrieve relevant chunks
    4. Generate answer using LLM with context
    """
    
    def __init__(self):
        """Initialize the RAG pipeline"""
        self.embeddings = None
        self.llm = None
        self.vector_store = None
        self.retriever = None
        
    def load_vector_store(self):
        """
        Load the FAISS vector store from disk
        
        Raises:
            FileNotFoundError: If vector store doesn't exist
        """
        if not utils.check_vector_store_exists():
            raise FileNotFoundError(
                "Vector store not found. Please run document ingestion first:\n"
                "python backend/ingest.py"
            )
        
        print("📂 Loading vector store...")
        
        try:
            # Initialize embeddings
            self.embeddings = utils.initialize_embeddings()
            
            # Load FAISS index
            vector_store_path = utils.get_vector_store_path()
            self.vector_store = FAISS.load_local(
                vector_store_path,
                self.embeddings,
                allow_dangerous_deserialization=True  # Required for FAISS
            )
            
            print("✅ Vector store loaded successfully")
        except Exception as e:
            print(f"❌ Error loading vector store: {e}")
            raise
    
    def initialize_llm(self):
        """Initialize the language model"""
        print("🤖 Initializing language model...")
        try:
            self.llm = utils.initialize_llm()
            print("✅ Language model ready")
        except Exception as e:
            print(f"❌ Error initializing LLM: {e}")
            raise
    
    def create_qa_chain(self):
        """
        Create the retriever for document search
        """
        # Create retriever from vector store
        self.retriever = self.vector_store.as_retriever(
            search_kwargs={"k": config.TOP_K_RETRIEVAL}
        )
    
    def setup(self):
        """
        Setup the complete RAG pipeline
        Call this once before processing queries
        """
        print("\n" + "="*60)
        print("🔧 INITIALIZING RAG PIPELINE")
        print("="*60 + "\n")
        
        self.load_vector_store()
        self.initialize_llm()
        self.create_qa_chain()
        
        print("\n✅ RAG Pipeline ready to answer questions!\n")
    
    def retrieve_relevant_chunks(self, question: str) -> List[Document]:
        """
        Retrieve relevant document chunks for a question
        
        Args:
            question: User question
        
        Returns:
            List of relevant Document chunks
        """
        if self.vector_store is None:
            raise ValueError("Vector store not loaded. Call setup() first.")
        
        # Perform similarity search
        relevant_docs = self.vector_store.similarity_search(
            question,
            k=config.TOP_K_RETRIEVAL
        )
        
        return relevant_docs
    
    def answer_question(self, question: str) -> Dict[str, any]:
        """
        Answer a question using RAG pipeline
        
        Args:
            question: User question
        
        Returns:
            Dictionary containing:
                - answer: Generated answer
                - source_documents: List of source documents
                - success: Boolean indicating success
                - error: Error message if failed
        """
        # Validate question
        is_valid, error_msg = utils.validate_question(question)
        if not is_valid:
            return {
                "answer": "",
                "source_documents": [],
                "success": False,
                "error": error_msg
            }
        
        try:
            # Retrieve relevant documents
            source_docs = self.vector_store.similarity_search(
                question,
                k=config.TOP_K_RETRIEVAL
            )
            
            # Process source documents to get original content
            processed_sources = []
            context_parts = []
            
            for doc in source_docs:
                # Use original content if available, otherwise use compressed
                if 'original_content' in doc.metadata:
                    content = doc.metadata['original_content']
                    # Truncate to avoid token limit issues
                    content = content[:400]  # Limit each chunk
                    processed_doc = Document(
                        page_content=content,
                        metadata=doc.metadata
                    )
                    processed_sources.append(processed_doc)
                    context_parts.append(content)
                else:
                    # Truncate doc content
                    content = doc.page_content[:400]
                    processed_sources.append(doc)
                    context_parts.append(content)
            
            # Build context with reasonable limit for Flan-T5
            context = "\n\n".join(context_parts)
            context = context[:1500]  # Flan-T5 handles more context
            
            # Create instruction-style prompt for Flan-T5
            prompt_text = f"""Answer the question based on the context below.

Context: {context}

Question: {question}

Provide a clear and concise answer:"""
            
            # Ensure total prompt length is manageable
            if len(prompt_text) > 3000:  # Character limit as proxy for tokens
                prompt_text = prompt_text[:3000]
            
            # Generate answer using LLM
            llm_response = self.llm.invoke(prompt_text)
            
            # Handle different response types
            if hasattr(llm_response, 'content'):
                answer = llm_response.content
            else:
                answer = str(llm_response)
            
            # Clean up the response to remove prompt repetition
            if answer.startswith(prompt_text):
                answer = answer[len(prompt_text):].strip()
            
            # Extract just the answer part if the prompt is repeated
            if "Answer:" in answer:
                parts = answer.split("Answer:")
                if len(parts) > 1:
                    answer = parts[-1].strip()
            
            return {
                "answer": answer.strip(),
                "source_documents": processed_sources,
                "success": True,
                "error": None
            }
            
        except Exception as e:
            print(f"❌ Error answering question: {e}")
            return {
                "answer": "",
                "source_documents": [],
                "success": False,
                "error": f"An error occurred: {str(e)}"
            }
    
    def get_stats(self) -> Dict[str, any]:
        """
        Get statistics about the vector store
        
        Returns:
            Dictionary with statistics
        """
        if self.vector_store is None:
            return {
                "total_chunks": 0,
                "embedding_dimension": 0,
                "ready": False
            }
        
        # Get index stats
        index = self.vector_store.index
        
        return {
            "total_chunks": index.ntotal,
            "embedding_dimension": index.d,
            "ready": True
        }


class ChatSession:
    """
    Manages a chat session with history
    """
    
    def __init__(self, rag_pipeline: RAGPipeline):
        """
        Initialize chat session
        
        Args:
            rag_pipeline: Initialized RAG pipeline
        """
        self.rag_pipeline = rag_pipeline
        self.history = []
    
    def ask(self, question: str) -> Dict[str, any]:
        """
        Ask a question and maintain history
        
        Args:
            question: User question
        
        Returns:
            Response dictionary from RAG pipeline
        """
        # Get answer from RAG pipeline
        response = self.rag_pipeline.answer_question(question)
        
        # Add to history if successful
        if response["success"]:
            self.history.append({
                "question": question,
                "answer": response["answer"],
                "sources": response["source_documents"]
            })
        
        return response
    
    def get_history(self) -> List[Dict]:
        """
        Get conversation history
        
        Returns:
            List of Q&A pairs
        """
        return self.history
    
    def clear_history(self):
        """Clear conversation history"""
        self.history = []


def main():
    """
    Test the RAG pipeline with sample questions
    Can be run standalone: python rag_pipeline.py
    """
    print("\n🧪 Testing RAG Pipeline\n")
    
    # Initialize pipeline
    rag = RAGPipeline()
    rag.setup()
    
    # Test questions
    test_questions = [
        "What are the admission requirements?",
        "When does the fall semester start?",
        "What is the grading policy?",
        "How do I register for courses?"
    ]
    
    print("="*60)
    print("Testing with sample questions:")
    print("="*60 + "\n")
    
    for question in test_questions:
        print(f"Q: {question}")
        response = rag.answer_question(question)
        
        if response["success"]:
            print(f"A: {response['answer']}\n")
        else:
            print(f"Error: {response['error']}\n")
        
        print("-" * 60 + "\n")


if __name__ == "__main__":
    main()
