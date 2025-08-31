# 🚀 Quick Start Guide

## Installation & Setup

1. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application**:
   ```bash
   streamlit run app.py
   ```

3. **Open your browser**:
   - Go to: http://localhost:8501
   - Start searching for jobs!

## Optional Configuration

For enhanced features, add API keys to `.env` file:

```bash
cp .env.example .env
# Edit .env with your API keys
```

- **Firecrawl API**: Get from [firecrawl.dev](https://firecrawl.dev) for better web scraping
- **OpenRouter API**: Get from [openrouter.ai](https://openrouter.ai) for AI job summaries

## Testing

Run the test suite to verify installation:
```bash
python test_app.py
```

## Usage

1. Enter job keywords (e.g., "software engineer")
2. Choose time filter (last hour/day/week/month)
3. Click "Search Jobs"
4. Browse AI-ranked job listings
5. Click "Apply Now" to go to job posting

## Features

- ✅ Real-time job scraping from LinkedIn
- ✅ AI-powered job summaries and ranking
- ✅ Auto-refresh every 60 seconds
- ✅ Fallback to Google Search
- ✅ Smart caching to reduce API calls
- ✅ Deployment-ready for Streamlit Cloud

Enjoy your job search! 🎯