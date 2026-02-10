"""
Document Ingestion Module
Handles PDF loading, text extraction, chunking, compression, and FAISS indexing
"""

import os
from typing import List, Dict
from pathlib import Path
from tqdm import tqdm

from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

import config
import utils


class DocumentIngester:
    """
    Handles the complete document ingestion pipeline:
    1. Load PDFs
    2. Extract and clean text
    3. Split into chunks
    4. Compress chunks (optional)
    5. Create embeddings
    6. Store in FAISS vector database
    """
    
    def __init__(self):
        """Initialize the document ingester"""
        self.embeddings = utils.initialize_embeddings()
        self.llm = None  # Initialize lazily for compression
        self.text_splitter = utils.create_text_splitter()
        
    def load_pdf_files(self) -> List[str]:
        """
        Load all PDF files from the data directory
        
        Returns:
            List of PDF file paths
        """
        pdf_files = list(config.PDF_DIR.glob("*.pdf"))
        
        if not pdf_files:
            raise FileNotFoundError(
                f"No PDF files found in {config.PDF_DIR}. "
                "Please add university documents (handbook, catalog, etc.) to the data/pdfs directory."
            )
        
        print(f"📁 Found {len(pdf_files)} PDF file(s) to process")
        return [str(pdf) for pdf in pdf_files]
    
    def extract_text_from_pdf(self, pdf_path: str) -> List[Document]:
        """
        Extract text from a single PDF file
        
        Args:
            pdf_path: Path to PDF file
        
        Returns:
            List of Document objects with extracted text
        """
        try:
            loader = PyPDFLoader(pdf_path)
            documents = loader.load()
            
            # Clean text in each document
            for doc in documents:
                doc.page_content = utils.clean_text(doc.page_content)
                # Add source filename to metadata
                doc.metadata['source'] = os.path.basename(pdf_path)
            
            return documents
        except Exception as e:
            print(f"⚠️ Error loading {pdf_path}: {e}")
            return []
    
    def chunk_documents(self, documents: List[Document]) -> List[Document]:
        """
        Split documents into smaller chunks
        
        Args:
            documents: List of Document objects
        
        Returns:
            List of chunked Document objects
        """
        print("✂️ Chunking documents...")
        chunks = self.text_splitter.split_documents(documents)
        print(f"   Created {len(chunks)} chunks from {len(documents)} pages")
        return chunks
    
    def compress_chunks(self, chunks: List[Document]) -> List[Document]:
        """
        Compress/summarize chunks before embedding
        This implements the document compression requirement
        
        Args:
            chunks: List of Document chunks
        
        Returns:
            List of Document chunks with compressed content and original in metadata
        """
        if not config.ENABLE_COMPRESSION:
            print("ℹ️ Compression disabled, using original chunks")
            return chunks
        
        print("🗜️ Compressing chunks (this may take a while)...")
        
        # Initialize LLM for compression if not already done
        if self.llm is None:
            self.llm = utils.initialize_llm()
        
        compressed_chunks = []
        
        for chunk in tqdm(chunks, desc="Compressing"):
            try:
                # Store original content in metadata
                original_content = chunk.page_content
                
                # Compress the content
                compressed_content = utils.compress_text(original_content, self.llm)
                
                # Create new document with compressed content
                compressed_doc = Document(
                    page_content=compressed_content,
                    metadata={
                        **chunk.metadata,
                        'original_content': original_content,
                        'compressed': True,
                        'compression_ratio': len(compressed_content) / len(original_content)
                    }
                )
                
                compressed_chunks.append(compressed_doc)
            except Exception as e:
                print(f"⚠️ Error compressing chunk: {e}")
                # Keep original chunk if compression fails
                compressed_chunks.append(chunk)
        
        # Calculate average compression ratio
        ratios = [c.metadata.get('compression_ratio', 1.0) for c in compressed_chunks if 'compression_ratio' in c.metadata]
        avg_ratio = sum(ratios) / len(ratios) if ratios else 1.0
        print(f"   Average compression ratio: {avg_ratio:.2f}")
        
        return compressed_chunks
    
    def create_vector_store(self, chunks: List[Document]) -> FAISS:
        """
        Create FAISS vector store from document chunks
        
        Args:
            chunks: List of Document chunks
        
        Returns:
            FAISS vector store
        """
        print("🔢 Creating embeddings and building FAISS index...")
        
        try:
            vector_store = FAISS.from_documents(
                documents=chunks,
                embedding=self.embeddings
            )
            print(f"✅ Successfully created vector store with {len(chunks)} chunks")
            return vector_store
        except Exception as e:
            print(f"❌ Error creating vector store: {e}")
            raise
    
    def save_vector_store(self, vector_store: FAISS):
        """
        Save FAISS vector store to disk
        
        Args:
            vector_store: FAISS vector store to save
        """
        save_path = utils.get_vector_store_path()
        
        try:
            vector_store.save_local(save_path)
            print(f"💾 Vector store saved to: {save_path}")
        except Exception as e:
            print(f"❌ Error saving vector store: {e}")
            raise
    
    def ingest_documents(self):
        """
        Main ingestion pipeline - orchestrates the entire process
        """
        print("\n" + "="*60)
        print("🚀 STARTING DOCUMENT INGESTION PIPELINE")
        print("="*60 + "\n")
        
        try:
            # Step 1: Load PDF files
            pdf_files = self.load_pdf_files()
            
            # Step 2: Extract text from all PDFs
            all_documents = []
            print("\n📄 Extracting text from PDFs...")
            for pdf_file in pdf_files:
                print(f"   Processing: {os.path.basename(pdf_file)}")
                documents = self.extract_text_from_pdf(pdf_file)
                all_documents.extend(documents)
            
            print(f"✅ Extracted text from {len(all_documents)} pages")
            
            if not all_documents:
                raise ValueError("No documents were successfully loaded")
            
            # Step 3: Chunk documents
            chunks = self.chunk_documents(all_documents)
            
            # Step 4: Compress chunks (implements ScaleDown requirement)
            compressed_chunks = self.compress_chunks(chunks)
            
            # Step 5: Create vector store
            vector_store = self.create_vector_store(compressed_chunks)
            
            # Step 6: Save vector store
            self.save_vector_store(vector_store)
            
            print("\n" + "="*60)
            print("✅ INGESTION COMPLETE!")
            print("="*60)
            print(f"📊 Summary:")
            print(f"   - PDF files processed: {len(pdf_files)}")
            print(f"   - Total pages: {len(all_documents)}")
            print(f"   - Chunks created: {len(compressed_chunks)}")
            print(f"   - Compression enabled: {config.ENABLE_COMPRESSION}")
            print(f"   - Vector store location: {utils.get_vector_store_path()}")
            print("\n✨ You can now run the chatbot application!\n")
            
        except Exception as e:
            print(f"\n❌ INGESTION FAILED: {e}")
            raise


def main():
    """
    Main function to run document ingestion
    Can be run standalone: python ingest.py
    """
    # Validate configuration
    warnings = config.validate_config()
    if warnings:
        print("\n⚠️ Configuration Warnings:")
        for warning in warnings:
            print(f"   {warning}")
        print()
    
    # Run ingestion
    ingester = DocumentIngester()
    ingester.ingest_documents()


if __name__ == "__main__":
    main()
