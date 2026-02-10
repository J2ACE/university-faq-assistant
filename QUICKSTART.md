# 🚀 QUICK START GUIDE

Get the University FAQ Assistant running in 5 minutes!

## Prerequisites Check
- [ ] Python 3.8+ installed (`python --version`)
- [ ] pip installed (`pip --version`)

## Step 1: Setup (2 minutes)

```bash
# Navigate to project directory
cd "d:\Intell Unnati\university_faq_assistant"

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\activate    # Windows
# source venv/bin/activate  # Mac/Linux

# Install dependencies (this takes a few minutes)
pip install -r requirements.txt
```

## Step 2: Configure (1 minute)

```bash
# Copy environment template
copy .env.example .env

# Edit .env file
notepad .env
```

### Configuration Options:

**Option A: OpenAI (Best quality, requires API key)**
```
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here
```

**Option B: HuggingFace (Free, slower)**
```
LLM_PROVIDER=huggingface
```

## Step 3: Add Documents (30 seconds)

### Option A: Use Sample Documents (Quick Testing)
```bash
# Install reportlab for PDF generation
pip install reportlab

# Generate sample university PDFs
python create_sample_docs.py
```

### Option B: Use Your Own PDFs
- Place your PDF files in `data/pdfs/` directory
- Examples: handbooks, catalogs, policies, calendars

## Step 4: Process Documents (1-5 minutes)

```bash
# Run document ingestion
python backend/ingest.py
```

Wait for completion. You'll see:
- ✅ PDF processing progress
- ✅ Compression statistics  
- ✅ Vector store creation

## Step 5: Launch Application (30 seconds)

```bash
# Start the web interface
streamlit run frontend/app.py
```

Your browser will open to `http://localhost:8501`

## 🎉 You're Ready!

Try these example questions:
- "What are the admission requirements?"
- "When does fall semester start?"
- "What is the refund policy?"
- "How do I register for courses?"

## ⚡ Ultra-Quick Setup (If you have Docker)

```bash
# Coming soon - Docker support
```

## 🐛 Troubleshooting

### "Vector store not found"
**Fix:** Run `python backend/ingest.py` first

### "No PDFs found"  
**Fix:** Add PDFs to `data/pdfs/` or run `python create_sample_docs.py`

### "OpenAI API error"
**Fix:** Check your API key or switch to `LLM_PROVIDER=huggingface`

### "Out of memory"
**Fix:** Use OpenAI instead of local HuggingFace models

## 📚 Next Steps

- Read full [README.md](README.md) for detailed documentation
- Customize settings in `backend/config.py`
- Add more university documents to improve answers
- Adjust compression and retrieval parameters

## 🆘 Need Help?

1. Check the [README.md](README.md) Troubleshooting section
2. Review console error messages
3. Verify all prerequisites are installed
4. Ensure PDFs are readable and not password-protected

---

**Time to first answer: ~5 minutes** ⏱️
