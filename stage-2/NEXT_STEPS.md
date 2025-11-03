# Next Steps - Getting Your Agent Running

## ✅ What's Done

Your Code Review Assistant AI agent is now fully configured to use **Google Gemini**! 

All files have been updated:
- ✅ Dependencies changed to use `google-generativeai`
- ✅ Agent logic updated for Gemini API
- ✅ Configuration files updated
- ✅ Documentation updated (README, QUICKSTART, BLOG_POST)
- ✅ Tweet templates updated
- ✅ Environment example created

## 🔑 Step 1: Get Your Gemini API Key (2 minutes)

1. Visit: **https://aistudio.google.com/app/apikey**
2. Sign in with your Google account
3. Click **"Get API Key"** or **"Create API Key"**
4. Copy your API key

## 📝 Step 2: Add API Key to .env File

Open `stage-3/.env` and add your API key:

```env
GEMINI_API_KEY=your-actual-key-here
```

**Important:** The `.env` file is already created but empty. Just paste your key!

## 🚀 Step 3: Install and Run (5 minutes)

```bash
cd stage-3

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the agent
python main.py
```

Your agent will start at: **http://localhost:8000**

## 🧪 Step 4: Test It

Open a new terminal and run:

```bash
python test_agent.py
```

Or test manually:

```bash
curl http://localhost:8000/health
```

Visit the API docs: **http://localhost:8000/docs**

## 📤 Step 5: Deploy

### Option A: Render (Recommended - Free tier available)

1. Push your code to GitHub
2. Go to https://render.com
3. Create New → Web Service
4. Connect your GitHub repo
5. Configure:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
6. Add Environment Variable:
   - Key: `GEMINI_API_KEY`
   - Value: Your Gemini API key
7. Click **Deploy**

### Option B: Railway

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up

# Add your API key
railway variables set GEMINI_API_KEY=your-key-here
```

### Option C: Local with ngrok (for testing)

```bash
# Install ngrok: https://ngrok.com/download

# In one terminal, run your agent
python main.py

# In another terminal, expose it
ngrok http 8000
```

Copy the ngrok URL (e.g., https://abc123.ngrok.io)

## 🔗 Step 6: Connect to Telex.im

1. Edit `workflow.json` and replace `YOUR_DEPLOYMENT_URL` with your actual URL:
   ```json
   "url": "https://your-app.render.com/a2a/agent/codeReviewAssistant"
   ```

2. Log in to https://telex.im

3. Navigate to agent configuration

4. Upload your `workflow.json`

5. Test by sending a message to your agent!

## 📝 Step 7: Documentation

1. **Write Blog Post**: Use `BLOG_POST.md` as a template
   - Add your deployment URL
   - Add screenshots
   - Share your experience

2. **Post Tweet**: Use templates from `TWEETS.md`
   - Tag @hnginternship
   - Tag @teleximapp
   - Use hashtags: #HNG13 #AI #GoogleGemini

3. **Submit**: Use `/submit` command in stage-3-backend channel

## 📋 Submission Checklist

- [ ] Gemini API key obtained and added to .env
- [ ] Dependencies installed
- [ ] Agent runs locally without errors
- [ ] Tests pass (`python test_agent.py`)
- [ ] Code pushed to GitHub
- [ ] Agent deployed to public URL
- [ ] workflow.json updated with deployment URL
- [ ] Tested on Telex.im
- [ ] Blog post written and published
- [ ] Tweet posted
- [ ] Submitted via `/submit` command

## 🆘 Troubleshooting

### "Import google.generativeai could not be resolved"
```bash
pip install google-generativeai
```

### "Gemini API key not configured"
- Make sure you added the key to `.env` file
- Make sure the key starts with your actual key value
- Restart the application after adding the key

### Agent not responding
- Check if API key is valid
- Check if you have API quota remaining
- Check application logs for errors

### Deployment issues
- Ensure all environment variables are set on the platform
- Check build logs for errors
- Verify the start command is correct

## 💡 Why Gemini?

- **Fast**: Gemini 1.5 Flash provides quick responses
- **Free Tier**: Generous free quota for testing
- **Powerful**: Excellent at code understanding and analysis
- **Easy Setup**: Simple API, no complex authentication

## 📊 Expected Results

Your agent should:
- ✅ Respond to code review requests in <3 seconds
- ✅ Identify bugs and security issues
- ✅ Suggest improvements with explanations
- ✅ Support 12+ programming languages
- ✅ Format responses with markdown
- ✅ Handle errors gracefully

## 🎯 Test Examples

Try these in Telex after connecting:

1. **"Review this code:"**
   ```python
   def calculate_average(numbers):
       return sum(numbers) / len(numbers)
   ```

2. **"Find bugs:"**
   ```javascript
   function getUserById(id) {
       const user = users.find(u => u.id = id);
       return user.name;
   }
   ```

3. **"Explain this:"**
   ```python
   result = [x**2 for x in range(10) if x % 2 == 0]
   ```

## 📞 Support

- Review `README.md` for detailed documentation
- Check `QUICKSTART.md` for step-by-step guide
- Use `DEPLOYMENT_CHECKLIST.md` to track progress
- Test with `/docs` endpoint for API documentation

---

**Deadline: Monday, 3rd Nov 2025 | 11:59pm GMT+1 (WAT)**

You have everything you need. Now go build something amazing! 🚀

**Good luck!** 🎉
