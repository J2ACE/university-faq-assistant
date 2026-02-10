"""
University FAQ Assistant - Streamlit Web Interface
A chatbot interface for answering student questions using RAG
"""

import streamlit as st
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

import config
import utils
from rag_pipeline import RAGPipeline, ChatSession


# Page configuration
st.set_page_config(
    page_title="University FAQ Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        text-align: center;
        color: #1f77b4;
        padding: 1rem 0;
        font-size: 2.5rem;
        font-weight: bold;
    }
    .chat-message {
        padding: 1.5rem;
        border-radius: 0.8rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        font-size: 1.1rem;
        line-height: 1.6;
    }
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-left: 5px solid #4c51bf;
        margin-left: 20%;
    }
    .assistant-message {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        border-left: 5px solid #ed64a6;
        margin-right: 20%;
    }
    .message-label {
        font-size: 0.9rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
        opacity: 0.9;
    }
    .message-content {
        font-size: 1.05rem;
        line-height: 1.7;
    }
    .source-doc {
        font-size: 0.9rem;
        color: #2d3748;
        padding: 1rem;
        background-color: #fff;
        border-radius: 0.5rem;
        margin-top: 0.75rem;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .stButton>button {
        width: 100%;
        font-size: 1.1rem;
        padding: 0.75rem;
        font-weight: bold;
    }
    /* Improve text input visibility */
    .stTextInput>div>div>input {
        font-size: 1.1rem;
        padding: 0.75rem;
    }
    /* Chat container styling */
    .chat-container {
        padding: 1rem 0;
        min-height: 200px;
        max-height: 500px;
        overflow-y: auto;
        margin-bottom: 1rem;
    }
    /* Remove extra padding from main container */
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    /* Scrollbar styling */
    .chat-container::-webkit-scrollbar {
        width: 8px;
    }
    .chat-container::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 10px;
    }
    .chat-container::-webkit-scrollbar-thumb {
        background: #888;
        border-radius: 10px;
    }
    .chat-container::-webkit-scrollbar-thumb:hover {
        background: #555;
    }
    /* Better spacing for sections */
    h3 {
        color: #2d3748;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }
    /* Welcome message */
    .stInfo {
        font-size: 1.1rem;
    }
    </style>
    """, unsafe_allow_html=True)


@st.cache_resource
def run_document_ingestion():
    """
    Run document ingestion to create vector database
    This runs automatically on first launch if vector store doesn't exist
    """
    try:
        from ingest import DocumentIngester
        ingester = DocumentIngester()
        ingester.ingest_documents()
        return True, None
    except Exception as e:
        return False, str(e)


@st.cache_resource
def initialize_rag_pipeline():
    """
    Initialize and cache the RAG pipeline
    This runs only once and is cached for performance
    """
    try:
        # Check if vector store exists, if not, create it
        if not utils.check_vector_store_exists():
            success, error = run_document_ingestion()
            if not success:
                return None, f"Failed to create vector database: {error}"
        
        rag = RAGPipeline()
        rag.setup()
        return rag, None
    except Exception as e:
        return None, str(e)


def display_chat_message(role: str, message: str, sources=None):
    """
    Display a chat message with styling
    
    Args:
        role: 'user' or 'assistant'
        message: Message text
        sources: Optional list of source documents
    """
    css_class = "user-message" if role == "user" else "assistant-message"
    icon = "👤 User" if role == "user" else "🤖 Assistant"
    
    st.markdown(f"""
        <div class="chat-message {css_class}">
            <div class="message-label">{icon}</div>
            <div class="message-content">{message}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Display sources if available
    if sources and role == "assistant":
        with st.expander("📚 View Sources", expanded=False):
            for i, doc in enumerate(sources, 1):
                source_name = doc.metadata.get('source', 'Unknown')
                page = doc.metadata.get('page', 'N/A')
                snippet = doc.page_content[:250] + "..." if len(doc.page_content) > 250 else doc.page_content
                
                st.markdown(f"""
                    <div class="source-doc">
                        <strong style="color: #2c5282; font-size: 1rem;">📄 Source {i}: {source_name}</strong> 
                        <span style="color: #718096;">(Page {page})</span><br/><br/>
                        <em style="color: #4a5568; line-height: 1.6;">{snippet}</em>
                    </div>
                    """, unsafe_allow_html=True)


def sidebar():
    """Render the sidebar with information and controls"""
    st.sidebar.title("ℹ️ About")
    
    st.sidebar.info("""
    **University FAQ Assistant** is an AI-powered chatbot that answers 
    student questions using official university documents.
    
    **How it works:**
    1. Documents are processed and compressed
    2. Your question is analyzed
    3. Relevant information is retrieved
    4. An answer is generated from the documents
    """)
    
    st.sidebar.title("📊 System Info")
    
    # Check if vector store exists
    if utils.check_vector_store_exists():
        st.sidebar.success("✅ Vector store loaded")
        
        # Get stats from session state
        if 'rag_pipeline' in st.session_state and st.session_state.rag_pipeline:
            stats = st.session_state.rag_pipeline.get_stats()
            st.sidebar.metric("Document Chunks", stats['total_chunks'])
            st.sidebar.metric("Embedding Dimension", stats['embedding_dimension'])
    else:
        st.sidebar.info("⏳ Vector database will be created automatically on first run...")

    
    # PDF count
    pdf_count = utils.count_pdf_files()
    st.sidebar.metric("PDF Documents", pdf_count)
    
    # Configuration info
    st.sidebar.title("⚙️ Configuration")
    st.sidebar.text(f"LLM Provider: {config.LLM_PROVIDER}")
    st.sidebar.text(f"Compression: {'Enabled' if config.ENABLE_COMPRESSION else 'Disabled'}")
    st.sidebar.text(f"Top-K Retrieval: {config.TOP_K_RETRIEVAL}")
    
    # Clear history button
    st.sidebar.title("🔧 Actions")
    if st.sidebar.button("🗑️ Clear Chat History"):
        if 'chat_session' in st.session_state:
            st.session_state.chat_session.clear_history()
            st.session_state.messages = []
            st.rerun()
    
    # Example questions
    st.sidebar.title("💡 Example Questions")
    example_questions = [
        "What are the admission requirements?",
        "When does the fall semester start?",
        "What is the refund policy?",
        "How do I register for courses?",
        "What are the graduation requirements?",
        "Tell me about academic probation"
    ]
    
    for question in example_questions:
        if st.sidebar.button(question, key=f"example_{question}"):
            st.session_state.example_question = question
            st.rerun()


def main():
    """Main application function"""
    
    # Header
    st.markdown('<h1 class="main-header">🎓 University FAQ Assistant</h1>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Initialize session state
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    if 'rag_pipeline' not in st.session_state:
        # Show initialization in sidebar instead of main area
        with st.sidebar:
            st.info("🔧 Initializing AI system...")
            
        # Initialize RAG pipeline
        with st.spinner("🔧 Initializing AI system... This may take a few minutes on first run."):
            rag_pipeline, error = initialize_rag_pipeline()
            
            if error:
                st.error(f"❌ Failed to initialize: {error}")
                with st.expander("🔧 Troubleshooting", expanded=False):
                    st.info("""
                    **Troubleshooting:**
                    1. Check that PDF files exist in `data/pdfs/` directory
                    2. Verify your API keys in Streamlit Secrets (Settings → Secrets)  
                    3. Make sure you have: LLM_PROVIDER, HUGGINGFACE_MODEL, HUGGINGFACE_EMBEDDING_MODEL
                    4. Check the app logs for detailed error messages
                    
                    **Manual initialization (if needed):**
                    Run: `python backend/ingest.py` locally, then commit the `data/vector_db/` folder
                    """)
                st.stop()
            
            st.session_state.rag_pipeline = rag_pipeline
            st.session_state.chat_session = ChatSession(rag_pipeline)
            
        # Clear the sidebar message
        with st.sidebar:
            st.success("✅ AI system ready!")
    
    # Render sidebar
    sidebar()
    
    # Main chat interface
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Input area at the top
        st.markdown("### ✍️ Ask a Question")
        
        # Check for example question from sidebar
        if 'example_question' in st.session_state:
            question = st.session_state.example_question
            del st.session_state.example_question
        else:
            question = None
        
        # Chat input with improved styling
        user_input = st.text_input(
            "Type your question here:",
            value=question or "",
            placeholder="e.g., What are the admission requirements?",
            key="user_input",
            label_visibility="visible"
        )
        
        col_send, col_clear = st.columns([1, 5])
        with col_send:
            send_button = st.button("📤 Send", type="primary", use_container_width=True)
        
        # Display chat history below input
        st.markdown("---")
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        
        if not st.session_state.messages:
            st.info("👋 Welcome! Ask me anything about university policies, procedures, courses, or calendar.")
        
        for message in st.session_state.messages:
            display_chat_message(
                message["role"],
                message["content"],
                message.get("sources")
            )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Process user input
        if send_button and user_input:
            # Add user message to history
            st.session_state.messages.append({
                "role": "user",
                "content": user_input,
                "sources": None
            })
            
            # Get response from RAG pipeline
            with st.spinner("🤔 Thinking..."):
                response = st.session_state.chat_session.ask(user_input)
            
            # Add assistant message to history
            if response["success"]:
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response["answer"],
                    "sources": response["source_documents"]
                })
            else:
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"❌ Error: {response['error']}",
                    "sources": None
                })
            
            # Rerun to update display
            st.rerun()
    
    with col2:
        st.subheader("📋 Quick Tips")
        st.markdown("""
        **For best results:**
        - Ask specific questions
        - Use keywords from university documents
        - Be clear and concise
        
        **Topics covered:**
        - Admissions
        - Registration
        - Academic policies
        - Calendar & deadlines
        - Graduation requirements
        - Student services
        """)
        
        # Display current stats
        if st.session_state.rag_pipeline:
            stats = st.session_state.rag_pipeline.get_stats()
            st.metric("Questions Asked", len([m for m in st.session_state.messages if m["role"] == "user"]))


if __name__ == "__main__":
    main()
