# 🚀 Deployment Guide

## Deploying to Streamlit Community Cloud (FREE)

### Step 1: Prepare GitHub Repository

1. **Create a new GitHub repository**
   - Go to https://github.com/new
   - Repository name: `university-faq-assistant`
   - Make it **Public**
   - Don't initialize with README (you already have one)

2. **Push your code to GitHub**
   ```bash
   cd "d:\Intell Unnati\university_faq_assistant"
   git init
   git add .
   git commit -m "Initial commit: University FAQ Assistant"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/university-faq-assistant.git
   git push -u origin main
   ```

### Step 2: Deploy on Streamlit Cloud

1. **Sign up for Streamlit Cloud**
   - Go to https://share.streamlit.io/
   - Sign in with your GitHub account
   - It's completely FREE!

2. **Create New App**
   - Click "New app"
   - Repository: `YOUR_USERNAME/university-faq-assistant`
   - Branch: `main`
   - Main file path: `frontend/app.py`
   - Click "Deploy"

3. **Add API Key (Secret)**
   - Click on "⚙️ Settings" → "Secrets"
   - Add this content:
   ```toml
   OPENAI_API_KEY = "dCwhMCtyGn7PdlnYGoaTI9X0oITDMDyO9vMZMgJ8"
   LLM_PROVIDER = "openai"
   OPENAI_MODEL = "gpt-3.5-turbo"
   OPENAI_EMBEDDING_MODEL = "text-embedding-ada-002"
   ```
   - Save

4. **Wait for Deployment**
   - Streamlit will automatically install dependencies from `requirements.txt`
   - First deployment takes 3-5 minutes
   - You'll get a public URL like: `https://your-app.streamlit.app/`

### Step 3: First Time Setup on Streamlit Cloud

After deployment, your app will start. You need to:

1. **Initialize the system** (one-time setup):
   - The app will detect no documents
   - Run the document ingestion process
   - This creates the vector database

2. **Share your app**:
   - Copy the Streamlit app URL
   - Share it in your LinkedIn post
   - Add it to your challenge submission form

---

## Alternative: Deploy on Other Platforms

### Option 1: Heroku
- Free tier available
- More control over deployment
- Requires Procfile

### Option 2: Azure App Service
- Microsoft platform
- Good for enterprise
- Requires Azure account

### Option 3: AWS EC2
- Full control
- Requires AWS account
- More complex setup

---

## Important Notes

✅ **Streamlit Cloud is RECOMMENDED because:**
- ✅ Completely FREE
- ✅ No credit card required
- ✅ Direct GitHub integration
- ✅ Automatic deployments on git push
- ✅ Built-in secrets management
- ✅ Perfect for student projects

⚠️ **Before deploying:**
- Ensure `.env` is in `.gitignore` (already done ✅)
- Never commit API keys to GitHub
- Use Streamlit secrets for API keys
- Test locally first

---

## Troubleshooting

### App fails to start
- Check `requirements.txt` has all dependencies
- Verify `frontend/app.py` path is correct
- Check Streamlit Cloud logs

### Vector database not found
- Run document ingestion on first launch
- Or commit pre-built `data/vector_db/` to GitHub

### API Key issues
- Verify secret is added in Streamlit Cloud settings
- Format must be exact (see Step 2.3)

---

## Your Deployed App URL

After deployment, add your URL here:
```
https://YOUR-APP-NAME.streamlit.app/
```

🎉 **You're ready to deploy!**
