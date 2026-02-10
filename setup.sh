#!/bin/bash

# Setup script for University FAQ Assistant (Linux/Mac)
# Automates the initial setup process

echo ""
echo "============================================================"
echo "   UNIVERSITY FAQ ASSISTANT - AUTOMATED SETUP"
echo "============================================================"
echo ""

# Check Python installation
echo "[1/7] Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python3 not found! Please install Python 3.8 or higher."
    exit 1
fi
echo "[OK] Python found: $(python3 --version)"
echo ""

# Create virtual environment
echo "[2/7] Creating virtual environment..."
if [ -d "venv" ]; then
    echo "[INFO] Virtual environment already exists"
else
    python3 -m venv venv
    echo "[OK] Virtual environment created"
fi
echo ""

# Activate virtual environment
echo "[3/7] Activating virtual environment..."
source venv/bin/activate
echo "[OK] Virtual environment activated"
echo ""

# Install dependencies
echo "[4/7] Installing dependencies (this may take 5-10 minutes)..."
echo "[INFO] Installing core packages..."
pip install --upgrade pip
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to install dependencies"
    exit 1
fi
echo "[OK] Dependencies installed"
echo ""

# Install optional reportlab for sample docs
echo "[5/7] Installing optional packages..."
pip install reportlab
echo "[OK] Optional packages installed"
echo ""

# Setup environment file
echo "[6/7] Setting up environment configuration..."
if [ -f ".env" ]; then
    echo "[INFO] .env file already exists"
else
    cp .env.example .env
    echo "[OK] Created .env file from template"
    echo "[INFO] Please edit .env file to add your API keys if using OpenAI"
fi
echo ""

# Create necessary directories
echo "[7/7] Creating directories..."
mkdir -p data/pdfs
mkdir -p data/vector_db
echo "[OK] Directories created"
echo ""

echo "============================================================"
echo "   SETUP COMPLETE!"
echo "============================================================"
echo ""
echo "Next steps:"
echo ""
echo "1. Activate virtual environment:"
echo "   source venv/bin/activate"
echo ""
echo "2. Configure your API keys (if using OpenAI):"
echo "   - Edit .env file"
echo "   - Set OPENAI_API_KEY=your-key-here"
echo ""
echo "3. Add PDF documents:"
echo "   - Option A: Place your PDFs in data/pdfs/"
echo "   - Option B: Generate samples: python create_sample_docs.py"
echo ""
echo "4. Run document ingestion:"
echo "   python backend/ingest.py"
echo ""
echo "5. Launch the application:"
echo "   streamlit run frontend/app.py"
echo ""
echo "Run test_system.py to verify installation:"
echo "   python test_system.py"
echo ""
echo "============================================================"
echo ""
