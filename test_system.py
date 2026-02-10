"""
System Test Script
Verifies that the University FAQ Assistant is properly configured and working
"""

import sys
from pathlib import Path
import os

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))


def print_header(text):
    """Print a formatted header"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60 + "\n")


def print_status(item, status, message=""):
    """Print a status line"""
    icon = "✅" if status else "❌"
    print(f"{icon} {item}", end="")
    if message:
        print(f": {message}")
    else:
        print()


def test_python_version():
    """Test Python version"""
    print_header("1. Python Environment")
    
    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"
    
    is_ok = version.major == 3 and version.minor >= 8
    print_status("Python Version", is_ok, version_str)
    
    if not is_ok:
        print("   ⚠️  Python 3.8 or higher required")
    
    return is_ok


def test_dependencies():
    """Test required dependencies"""
    print_header("2. Dependencies")
    
    dependencies = [
        ("langchain", "langchain"),
        ("langchain_community", "langchain-community"),
        ("langchain_openai", "langchain-openai"),
        ("FAISS", "faiss"),
        ("Streamlit", "streamlit"),
        ("pypdf", "pypdf"),
        ("python-dotenv", "dotenv"),
        ("transformers", "transformers"),
        ("sentence-transformers", "sentence_transformers"),
    ]
    
    all_ok = True
    for name, import_name in dependencies:
        try:
            __import__(import_name)
            print_status(name, True)
        except ImportError:
            print_status(name, False, "NOT INSTALLED")
            all_ok = False
    
    if not all_ok:
        print("\n   ⚠️  Install missing dependencies: pip install -r requirements.txt")
    
    return all_ok


def test_configuration():
    """Test configuration"""
    print_header("3. Configuration")
    
    try:
        import config
        print_status("Config module loaded", True)
        
        # Check .env file
        env_exists = Path(".env").exists()
        print_status(".env file exists", env_exists)
        
        if not env_exists:
            print("   ⚠️  Copy .env.example to .env and configure")
        
        # Check LLM provider
        provider = config.LLM_PROVIDER
        print_status("LLM Provider", True, provider)
        
        # Check API keys
        if provider == "openai":
            has_key = bool(config.OPENAI_API_KEY and config.OPENAI_API_KEY != "")
            print_status("OpenAI API Key", has_key)
            if not has_key:
                print("   ⚠️  Set OPENAI_API_KEY in .env file")
        
        # Check directories
        pdfs_exist = config.PDF_DIR.exists()
        print_status("PDF directory exists", pdfs_exist, str(config.PDF_DIR))
        
        vector_db_dir = config.VECTOR_DB_DIR.exists()
        print_status("Vector DB directory exists", vector_db_dir, str(config.VECTOR_DB_DIR))
        
        return True
    except Exception as e:
        print_status("Configuration", False, str(e))
        return False


def test_documents():
    """Test document availability"""
    print_header("4. Documents")
    
    try:
        import config
        import utils
        
        pdf_count = utils.count_pdf_files()
        has_pdfs = pdf_count > 0
        print_status(f"PDF files found ({pdf_count})", has_pdfs)
        
        if not has_pdfs:
            print("   ℹ️  Add PDFs to data/pdfs/ or run: python create_sample_docs.py")
        
        # List PDFs
        if has_pdfs:
            print("\n   📄 PDF files:")
            for pdf in config.PDF_DIR.glob("*.pdf"):
                print(f"      - {pdf.name}")
        
        return has_pdfs
    except Exception as e:
        print_status("Document check", False, str(e))
        return False


def test_vector_store():
    """Test vector store"""
    print_header("5. Vector Store")
    
    try:
        import utils
        
        exists = utils.check_vector_store_exists()
        print_status("Vector store exists", exists)
        
        if exists:
            vector_path = utils.get_vector_store_path()
            print(f"   📍 Location: {vector_path}")
            
            # Try to load it
            try:
                from langchain_community.vectorstores import FAISS
                embeddings = utils.initialize_embeddings()
                vector_store = FAISS.load_local(
                    vector_path,
                    embeddings,
                    allow_dangerous_deserialization=True
                )
                chunk_count = vector_store.index.ntotal
                print_status("Vector store loadable", True, f"{chunk_count} chunks")
            except Exception as e:
                print_status("Vector store loadable", False, str(e))
                return False
        else:
            print("   ℹ️  Run document ingestion: python backend/ingest.py")
        
        return exists
    except Exception as e:
        print_status("Vector store check", False, str(e))
        return False


def test_rag_pipeline():
    """Test RAG pipeline"""
    print_header("6. RAG Pipeline")
    
    try:
        from rag_pipeline import RAGPipeline
        
        # Check if vector store exists first
        import utils
        if not utils.check_vector_store_exists():
            print_status("RAG Pipeline", False, "Vector store not found")
            print("   ℹ️  Run: python backend/ingest.py")
            return False
        
        print("   Initializing RAG pipeline...")
        rag = RAGPipeline()
        rag.setup()
        
        print_status("RAG Pipeline initialized", True)
        
        # Test a simple query
        print("\n   Testing query...")
        result = rag.answer_question("What are the admission requirements?")
        
        if result["success"]:
            print_status("Query test", True)
            print(f"\n   📝 Answer preview: {result['answer'][:150]}...")
            print(f"   📚 Sources found: {len(result['source_documents'])}")
        else:
            print_status("Query test", False, result['error'])
            return False
        
        return True
    except Exception as e:
        print_status("RAG Pipeline", False, str(e))
        return False


def generate_report():
    """Generate full test report"""
    print("\n" + "🔍 UNIVERSITY FAQ ASSISTANT - SYSTEM TEST" + "\n")
    
    results = {
        "Python Version": test_python_version(),
        "Dependencies": test_dependencies(),
        "Configuration": test_configuration(),
        "Documents": test_documents(),
        "Vector Store": test_vector_store(),
    }
    
    # Only test RAG if previous tests pass
    if all(results.values()):
        results["RAG Pipeline"] = test_rag_pipeline()
    else:
        print_header("6. RAG Pipeline")
        print("   ⏭️  Skipped (fix previous issues first)")
    
    # Summary
    print_header("TEST SUMMARY")
    
    total = len(results)
    passed = sum(results.values())
    
    print(f"Tests Passed: {passed}/{total}\n")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED!")
        print("\n✨ Your system is ready!")
        print("   Run: streamlit run frontend/app.py")
    else:
        print("⚠️  SOME TESTS FAILED")
        print("\nFailed components:")
        for name, status in results.items():
            if not status:
                print(f"   ❌ {name}")
        
        print("\n📚 Next steps:")
        if not results.get("Dependencies"):
            print("   1. Install dependencies: pip install -r requirements.txt")
        if not results.get("Configuration"):
            print("   2. Configure .env file")
        if not results.get("Documents"):
            print("   3. Add PDFs or run: python create_sample_docs.py")
        if not results.get("Vector Store"):
            print("   4. Run ingestion: python backend/ingest.py")
    
    print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    generate_report()
