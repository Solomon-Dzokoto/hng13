# Quick Setup Guide

## 🚀 Get Started in 5 Minutes

### Step 1: Install Dependencies
```bash
cd stage-3
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Step 2: Configure Environment
```bash
cp .env.example .env
# Edit .env with your API key
```

Add your Google Gemini API key:
```env
GEMINI_API_KEY=your-gemini-key-here
GEMINI_MODEL=gemini-1.5-flash
```

Get your API key from: https://aistudio.google.com/app/apikey

### Step 3: Run the Agent
```bash
chmod +x start.sh
./start.sh
```

Or:
```bash
python main.py
```

### Step 4: Test It
Open another terminal:
```bash
python test_agent.py
```

Or visit: http://localhost:8000/docs

### Step 5: Deploy

**Option A: Render (Recommended)**
1. Push to GitHub
2. Go to [render.com](https://render.com)
3. New Web Service → Connect repository
4. Build Command: `pip install -r requirements.txt`
5. Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
6. Add environment variables
7. Deploy!

**Option B: Railway**
```bash
railway login
railway init
railway add
railway up
```

**Option C: Docker**
```bash
docker build -t code-review-agent .
docker run -p 8000:8000 --env-file .env code-review-agent
```

### Step 6: Configure Telex.im
1. Update `workflow.json` with your deployment URL
2. Upload to Telex.im
3. Test in Telex chat!

## 📝 Quick Test

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{
      "role": "user",
      "content": [{"type": "text", "text": "Review: def add(a,b): return a+b"}]
    }]
  }'
```

## 🎯 What to Submit

1. **Repository URL**: Your GitHub repo
2. **Live Demo URL**: Your deployed endpoint
3. **Blog Post**: Link to your blog
4. **Tweet**: Screenshot or link
5. **Workflow JSON**: Updated with your URL

## 📞 Need Help?

- Check `/docs` for API documentation
- Run `python test_agent.py` for diagnostics
- Check logs for errors
- Verify API key is valid

## ✅ Pre-Submission Checklist

- [ ] Agent runs locally
- [ ] All tests pass
- [ ] Deployed to public URL
- [ ] workflow.json updated with URL
- [ ] README.md reviewed
- [ ] Blog post written
- [ ] Tweet posted
- [ ] All endpoints working

Good luck! 🚀
