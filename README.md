# 🔍 Real-Time Job Board

A powerful, real-time job board application that continuously fetches and displays the latest job postings from LinkedIn and other job sources. Built with modern web scraping, AI-powered job ranking, and a responsive Streamlit interface.

## ✨ Features

- **Real-time Job Fetching**: Continuously monitors LinkedIn and other job boards for new postings
- **AI-Powered Ranking**: Uses OpenRouter's GPT models to summarize and rank jobs by relevance
- **Multi-Source Search**: Falls back to Google Search when primary sources are unavailable
- **Smart Caching**: Reduces redundant requests with intelligent caching
- **Auto-Refresh**: Real-time updates every 60 seconds
- **Responsive UI**: Clean, modern interface built with Streamlit
- **Error Handling**: Graceful degradation when data sources are unavailable
- **Deployment-Ready**: Works out-of-the-box on multiple platforms

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- pip package manager

### Installation

1. **Clone or download the project**
   ```bash
   git clone <repository-url>
   cd job-board
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables (optional)**
   ```bash
   cp .env.example .env
   # Edit .env file with your API keys
   ```

4. **Run the application**
   ```bash
   streamlit run app.py
   ```

5. **Open your browser**
   - Navigate to `http://localhost:8501`
   - Start searching for jobs!

## 🔧 Configuration

### API Keys (Optional but Recommended)

The application works without API keys but provides enhanced features when configured:

#### Firecrawl API (Recommended)
- **Purpose**: Enhanced web scraping capabilities
- **Get it**: [firecrawl.dev](https://firecrawl.dev)
- **Setup**: Add `FIRECRAWL_API_KEY=your_key_here` to `.env`

#### OpenRouter API (Recommended)  
- **Purpose**: AI-powered job summaries and ranking
- **Get it**: [openrouter.ai](https://openrouter.ai)
- **Setup**: Add `OPENROUTER_API_KEY=your_key_here` to `.env`

### Environment Variables

Create a `.env` file in the project root:

```env
# OpenRouter API Configuration
OPENROUTER_API_KEY=your_openrouter_api_key_here

# Firecrawl API Configuration  
FIRECRAWL_API_KEY=your_firecrawl_api_key_here

# Optional: Rate limiting configuration
MAX_REQUESTS_PER_MINUTE=10
CACHE_DURATION_MINUTES=5

# Optional: UI Configuration
AUTO_REFRESH_SECONDS=60
MAX_JOBS_DISPLAY=10
```

## 🌐 Deployment

### Local Development

```bash
streamlit run app.py
```

### Streamlit Cloud

1. **Push code to GitHub**
2. **Visit** [share.streamlit.io](https://share.streamlit.io)
3. **Connect your repository**
4. **Add secrets** in Streamlit Cloud dashboard:
   - `FIRECRAWL_API_KEY`
   - `OPENROUTER_API_KEY`
5. **Deploy!**

### Hugging Face Spaces

1. **Create a new Space** on [huggingface.co/spaces](https://huggingface.co/spaces)
2. **Choose Streamlit** as the SDK
3. **Upload files** or connect GitHub
4. **Add secrets** in Space settings:
   - `FIRECRAWL_API_KEY`
   - `OPENROUTER_API_KEY`
5. **Your app is live!**

### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py"]
```

```bash
docker build -t job-board .
docker run -p 8501:8501 job-board
```

### Heroku Deployment

1. **Create** `setup.sh`:
   ```bash
   mkdir -p ~/.streamlit/
   echo "[server]
   headless = true
   port = $PORT
   enableCORS = false
   " > ~/.streamlit/config.toml
   ```

2. **Create** `Procfile`:
   ```
   web: sh setup.sh && streamlit run app.py
   ```

3. **Deploy**:
   ```bash
   heroku create your-app-name
   git push heroku main
   ```

## 🏗️ Architecture

### System Components

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   UI Agent      │    │ Controller Agent │    │ Crawler Agent   │
│   (Streamlit)   │◄──►│   (Orchestrator) │◄──►│   (LinkedIn)    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                       ┌────────┴────────┐
                       ▼                 ▼
                ┌─────────────────┐ ┌─────────────────┐
                │ Search Agent    │ │ Ranking Agent   │
                │ (Google Search) │ │ (OpenRouter AI) │
                └─────────────────┘ └─────────────────┘
```

### Data Flow

1. **User Input** → Keywords entered in UI
2. **Controller** → Orchestrates parallel search execution
3. **Crawler Agent** → Fetches jobs from LinkedIn (primary)
4. **Search Agent** → Falls back to Google Search + other job sites
5. **Ranking Agent** → AI-powered summarization and relevance scoring
6. **UI Agent** → Displays ranked, summarized job listings
7. **Auto-refresh** → Repeats process every 60 seconds

## 📁 Project Structure

```
job-board/
├── app.py                 # Main Streamlit application
├── controller_agent.py    # Main orchestrator
├── crawler_agent.py       # LinkedIn job scraping
├── search_agent.py        # Google Search fallback
├── ranking_agent.py       # AI-powered job ranking
├── ui_agent.py           # Streamlit UI components
├── requirements.txt       # Python dependencies
├── .env.example          # Environment template
├── README.md             # This file
└── .gitignore           # Git ignore rules
```

## 🔍 Usage

### Basic Search

1. **Enter keywords**: Type your desired job role (e.g., "software engineer")
2. **Set filters**: Choose time range (last hour/day/week/month)
3. **Click Search**: Get real-time job listings
4. **Apply**: Click "Apply Now" to go to the original job posting

### Advanced Features

- **Auto-refresh**: Enable for continuous job monitoring
- **API Keys**: Add for enhanced AI summaries and better scraping
- **Cache Control**: Clear cache for fresh results
- **Health Check**: Monitor system component status
- **Debug Mode**: View detailed system information

### Search Tips

- Use specific job titles: "Senior React Developer" vs "Developer"
- Include location keywords: "Remote Software Engineer"
- Try company names: "Google Software Engineer"
- Use skill keywords: "Python Machine Learning Engineer"

## 🛠️ Development

### Adding New Job Sources

1. **Extend SearchAgent**: Add new site to `build_search_queries()`
2. **Add Parser**: Implement site-specific parsing logic
3. **Update Controller**: Include new source in parallel execution

### Customizing AI Summaries

1. **Modify RankingAgent**: Update prompts in `summarize_job_description()`
2. **Change Model**: Switch OpenRouter model in `ranking_agent.py`
3. **Adjust Scoring**: Modify relevance calculation logic

### UI Customization

1. **Update UIAgent**: Modify Streamlit components
2. **Add Filters**: Extend search controls
3. **Style Changes**: Update CSS in `render_job_card()`

## 🐛 Troubleshooting

### Common Issues

**No jobs found**
- Check internet connection
- Try broader search terms
- Verify API keys if configured
- Check rate limiting messages

**Slow performance**
- Reduce `max_jobs` parameter
- Enable caching
- Check system resources

**API errors**
- Verify API keys are correct
- Check API service status
- Review rate limits

### Error Handling

The application includes comprehensive error handling:
- **Graceful degradation** when APIs are unavailable
- **Fallback mechanisms** for failed web scraping
- **User-friendly error messages** with suggested solutions
- **System health monitoring** for component status

### Debugging

Enable debug mode in the UI to view:
- Session state information
- Job parsing details
- API response data
- System component health

## 📊 Performance

### Optimization Features

- **Parallel Processing**: Multiple agents run simultaneously
- **Smart Caching**: 5-minute cache for repeated searches
- **Rate Limiting**: Prevents overwhelming job sites
- **Request Throttling**: Configurable delays between API calls

### Scalability

- **Stateless Design**: Easy horizontal scaling
- **Caching Layer**: Reduces external API calls
- **Modular Architecture**: Components can be scaled independently
- **Error Isolation**: Failures in one component don't crash others

## 🤝 Contributing

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/new-feature`
3. **Make changes**: Implement your feature
4. **Test thoroughly**: Ensure all components work
5. **Submit pull request**: Describe your changes

### Code Guidelines

- Follow PEP 8 style guidelines
- Add comprehensive error handling
- Include logging for debugging
- Write clear docstrings
- Test edge cases

## 📝 License

This project is open-source and available under the MIT License. See LICENSE file for details.

## 🙏 Acknowledgments

- **Streamlit**: For the amazing web app framework
- **Firecrawl**: For reliable web scraping capabilities
- **OpenRouter**: For accessible AI model APIs
- **Job Board Sites**: For providing job data

## 📞 Support

- **Issues**: Report bugs via GitHub Issues
- **Questions**: Ask in GitHub Discussions
- **Updates**: Watch repository for new releases

---

**Happy Job Hunting! 🎯**