# 🚀 Render Deployment Guide - eBay Auto Parts Lister

## 📦 Deployment Files Ready
✅ **render.yaml** - Render service configuration  
✅ **start_render.py** - Production startup script  
✅ **requirements.txt** - All Python dependencies  
✅ **Dockerfile** - Container configuration (backup option)  

## 🎯 Quick Deployment Steps

### Step 1: Push to GitHub
```bash
# Initialize git repository (if not done already)
git init
git add .
git commit -m "Full eBay Auto Parts Lister ready for Render deployment"

# Push to your GitHub repository
git remote add origin https://github.com/yourusername/ebay-auto-parts-lister.git
git branch -M main
git push -u origin main
```

### Step 2: Deploy to Render
1. **Go to [render.com](https://render.com)**
2. **Sign in with GitHub**
3. **Click "New +" → "Web Service"**
4. **Connect your GitHub repository**
5. **Render will auto-detect the render.yaml configuration**

### Step 3: Configure Environment Variables
In Render dashboard, add these environment variables:

**Required:**
- `GEMINI_API_KEY` - Your Google Gemini API key (primary AI service for part identification)
- `EBAY_APP_ID` - eBay Developer App ID
- `EBAY_DEV_ID` - eBay Developer ID  
- `EBAY_CERT_ID` - eBay Certificate ID
- `EBAY_USER_TOKEN` - eBay User Token

**Optional (fallback/enhanced features):**
- `OPENAI_API_KEY` - OpenAI API key (fallback if Gemini unavailable)
- `GOOGLE_VISION_API_KEY` - Google Vision API key

### Step 4: Deploy!
- Click **"Create Web Service"**
- Render will automatically build and deploy your app
- Your app will be available at: `https://your-app-name.onrender.com`

## 🔧 Configuration Details

### Service Configuration (render.yaml)
- **Runtime:** Python 3.11
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `python -m uvicorn main_full:app --host 0.0.0.0 --port $PORT`
- **Plan:** Free tier (can upgrade later)

### Features Included in Full Deployment
- ✅ AI-powered part identification (Google Gemini with OpenAI fallback)
- ✅ Smart image processing and enhancement
- ✅ eBay API integration for listing creation
- ✅ Market pricing suggestions
- ✅ SEO-optimized titles and descriptions
- ✅ Database for tracking parts and listings
- ✅ Web interface for easy uploads

## 🚨 Important Notes

1. **Free Tier Limitations:**
   - Service sleeps after 15 minutes of inactivity
   - 750 hours/month of runtime
   - Consider upgrading for production use

2. **API Keys Security:**
   - Never commit API keys to GitHub
   - Use Render's environment variables feature
   - Keep your .env file in .gitignore

3. **First Deploy:**
   - May take 5-10 minutes for initial build
   - Check logs if deployment fails
   - Ensure all environment variables are set

## 🔍 Testing Your Deployment

Once deployed, test these endpoints:
- `GET /` - Main web interface
- `GET /health` - Health check
- `POST /upload` - Image upload functionality
- `GET /api/parts` - Parts database API

## 🆘 Troubleshooting

**Build Fails:**
- Check requirements.txt for compatibility issues
- Verify Python version (3.11)
- Check Render build logs

**App Won't Start:**
- Verify environment variables are set
- Check start command in render.yaml
- Review application logs in Render dashboard

**Features Not Working:**
- Confirm all API keys are properly configured
- Check API quotas and limits
- Verify eBay sandbox vs production settings
