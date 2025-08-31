import streamlit as st
import pandas as pd
from typing import List
from crawler_agent import JobPosting
import time
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UIAgent:
    """Agent responsible for the Streamlit user interface"""
    
    def __init__(self):
        """Initialize the UI agent"""
        self.setup_page_config()
        self.setup_custom_css()
        self.initialize_session_state()
    
    def setup_custom_css(self):
        """Add custom CSS for professional styling"""
        st.markdown("""
        <style>
        /* Import Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        /* Hide Streamlit branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Global font styling */
        .stApp {
            font-family: 'Inter', sans-serif;
        }
        
        /* Main container styling */
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 1200px;
        }
        
        /* Professional header styling */
        .professional-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 3rem 2rem;
            border-radius: 16px;
            color: white;
            text-align: center;
            margin-bottom: 3rem;
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.2);
        }
        
        .professional-header h1 {
            font-size: 3.5rem;
            font-weight: 700;
            margin-bottom: 1rem;
            letter-spacing: -0.02em;
        }
        
        .professional-header p {
            font-size: 1.25rem;
            opacity: 0.9;
            font-weight: 400;
            margin: 0;
        }
        
        /* Search container styling */
        .search-container {
            background: white;
            padding: 2.5rem;
            border-radius: 16px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
            border: 1px solid #e5e7eb;
            margin-bottom: 3rem;
        }
        
        /* Input field styling */
        .stTextInput > div > div > input {
            border: 2px solid #e5e7eb;
            border-radius: 12px;
            padding: 1rem 1.25rem;
            font-size: 1.1rem;
            font-weight: 500;
            transition: all 0.3s ease;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.02);
        }
        
        .stTextInput > div > div > input:focus {
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
            outline: none;
        }
        
        /* Button styling */
        .stButton > button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 12px;
            padding: 1rem 2.5rem;
            font-size: 1.1rem;
            font-weight: 600;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
        }
        
        /* Job card styling */
        .job-card {
            background: white;
            border-radius: 16px;
            padding: 2rem;
            margin: 1.5rem 0;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
            border: 1px solid #f3f4f6;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        
        .job-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 12px 35px rgba(0, 0, 0, 0.15);
            border-color: #e5e7eb;
        }
        
        .job-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 4px;
            height: 100%;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        
        .job-title {
            font-size: 1.5rem;
            font-weight: 700;
            color: #1f2937;
            margin-bottom: 0.5rem;
            line-height: 1.3;
        }
        
        .job-company {
            font-size: 1.1rem;
            font-weight: 500;
            color: #6b7280;
            margin-bottom: 0.75rem;
        }
        
        .job-meta {
            display: flex;
            gap: 1.5rem;
            margin-bottom: 1rem;
            flex-wrap: wrap;
        }
        
        .job-meta-item {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            font-size: 0.95rem;
            color: #6b7280;
            font-weight: 500;
        }
        
        /* Metric cards styling */
        [data-testid="metric-container"] {
            background: white;
            border: 1px solid #e5e7eb;
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
            transition: all 0.3s ease;
        }
        
        [data-testid="metric-container"]:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
        }
        
        /* Success and warning styling */
        .stSuccess {
            background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
            border: 1px solid #34d399;
            border-radius: 12px;
            padding: 1rem;
        }
        
        .stWarning {
            background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
            border: 1px solid #f59e0b;
            border-radius: 12px;
            padding: 1rem;
        }
        
        /* Link button styling */
        .stLinkButton > a {
            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
            color: white;
            text-decoration: none;
            border-radius: 10px;
            padding: 0.75rem 1.5rem;
            font-weight: 600;
            transition: all 0.3s ease;
            display: inline-block;
        }
        
        .stLinkButton > a:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
        }
        
        /* Footer styling */
        .professional-footer {
            background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
            border-radius: 16px;
            padding: 2.5rem;
            margin-top: 3rem;
            border: 1px solid #e5e7eb;
        }
        
        /* Sidebar styling */
        .css-1d391kg {
            background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%);
        }
        
        /* Loading spinner */
        .stSpinner {
            border-radius: 12px;
        }
        
        /* Professional spacing */
        .element-container {
            margin-bottom: 1rem;
        }
        </style>
        """, unsafe_allow_html=True)
    
    def setup_page_config(self):
        """Configure Streamlit page settings with better defaults"""
        st.set_page_config(
            page_title="Real-Time Job Board - Find Your Dream Job",
            page_icon="🔍",
            layout="wide",
            initial_sidebar_state="expanded",
            menu_items={
                'Get Help': 'https://github.com/your-repo/job-board',
                'Report a bug': "https://github.com/your-repo/job-board/issues",
                'About': "Real-Time Job Board - AI-powered job search with live updates from LinkedIn and other job sources."
            }
        )
    
    def initialize_session_state(self):
        """Initialize Streamlit session state variables"""
        if 'jobs' not in st.session_state:
            st.session_state.jobs = []
        if 'last_search' not in st.session_state:
            st.session_state.last_search = ""
        if 'last_update' not in st.session_state:
            st.session_state.last_update = None
        if 'auto_refresh' not in st.session_state:
            st.session_state.auto_refresh = True
        if 'search_count' not in st.session_state:
            st.session_state.search_count = 0
    
    def render_header(self):
        """Render minimal professional header"""
        st.markdown("""
        <div style="
            text-align: center;
            padding: 2rem 1rem;
            margin-bottom: 2rem;
        ">
            <h1 style="
                color: #1f2937;
                font-weight: 700;
                font-size: 2.5rem;
                margin-bottom: 0.5rem;
                letter-spacing: -0.02em;
            ">🎯 Professional Job Search</h1>
            <p style="
                color: #6b7280;
                font-size: 1.1rem;
                margin: 0;
            ">Find real-time opportunities from top companies</p>
        </div>
        """, unsafe_allow_html=True)
    
    def render_search_controls(self):
        """Render ultra-minimal search interface - just search bar"""
        # Center the search with maximum focus
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Clean, professional search input
        keywords = st.text_input(
            "Search for Jobs",
            value="",
            placeholder="e.g., Software Engineer, Data Scientist, Product Manager",
            key="job_search_input",
            help="Enter your desired job title or keywords"
        )
        
        # Single prominent search button
        search_clicked = st.button(
            "🔍 Search Jobs", 
            type="primary", 
            use_container_width=True,
            key="search_button"
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Fixed professional defaults - no user configuration needed
        hours_filter = 24  # Last 24 hours
        max_jobs = 10     # 10 unique jobs
        sort_by = "Relevance"  # Relevance-based
        
        return keywords, hours_filter, max_jobs, sort_by, search_clicked
    
    def render_search_button(self):
        """No additional controls needed - everything is in search controls"""
        return False, False
    
    def render_job_stats(self, jobs: List[JobPosting]):
        """Render job statistics"""
        if not jobs:
            return
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Jobs", len(jobs))
        
        with col2:
            companies = len(set([job.company for job in jobs if job.company]))
            st.metric("Companies", companies)
        
        with col3:
            avg_score = sum([job.relevance_score for job in jobs]) / len(jobs) if jobs else 0
            st.metric("Avg. Relevance", f"{avg_score:.2f}")
        
        with col4:
            st.metric("Search Count", st.session_state.search_count)
    
    def render_job_card(self, job: JobPosting, index: int):
        """Render individual job card with improved design"""
        with st.container():
            # Create modern card design
            st.markdown(f"""
            <div style="
                border: 1px solid #e0e0e0;
                border-radius: 12px;
                padding: 24px;
                margin: 16px 0;
                background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
                box-shadow: 0 4px 6px rgba(0,0,0,0.05);
                border-left: 4px solid #4CAF50;
            ">
            """, unsafe_allow_html=True)
            
            # Job header with better layout
            col1, col2 = st.columns([4, 1])
            
            with col1:
                # Job title with larger font
                st.markdown(f"#### 💼 {job.title}")
                
                # Company and location in one line
                col_a, col_b = st.columns([1, 1])
                with col_a:
                    st.markdown(f"🏢 **{job.company}**")
                with col_b:
                    st.markdown(f"📍 {job.location}")
                
                # Time posted with icon
                st.markdown(f"🕰️ {job.time_posted}")
                
                # Relevance score with color coding
                if hasattr(job, 'relevance_score') and job.relevance_score > 0:
                    score = job.relevance_score
                    if score > 0.7:
                        score_color = "#4CAF50"  # Green
                        score_text = "Excellent Match"
                    elif score > 0.5:
                        score_color = "#FF9800"  # Orange
                        score_text = "Good Match"
                    else:
                        score_color = "#f44336"  # Red
                        score_text = "Fair Match"
                    
                    st.markdown(f"""
                    <div style="margin: 8px 0;">
                        <span style="color: {score_color}; font-weight: bold;">★ {score_text}</span>
                        <span style="color: #666; font-size: 0.9em;"> ({score:.1%})</span>
                    </div>
                    """, unsafe_allow_html=True)
            
            with col2:
                # Apply button with better styling
                if job.link:
                    st.markdown("""
                    <style>
                    .apply-button {
                        background: linear-gradient(45deg, #4CAF50, #45a049);
                        color: white;
                        padding: 12px 24px;
                        border: none;
                        border-radius: 8px;
                        cursor: pointer;
                        font-weight: bold;
                        text-decoration: none;
                        display: inline-block;
                        text-align: center;
                        margin-top: 10px;
                        transition: all 0.3s ease;
                    }
                    .apply-button:hover {
                        background: linear-gradient(45deg, #45a049, #4CAF50);
                        transform: translateY(-2px);
                        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
                    }
                    </style>
                    """, unsafe_allow_html=True)
                    
                    st.markdown(f'<a href="{job.link}" target="_blank" class="apply-button">🎯 Apply Now</a>', unsafe_allow_html=True)
            
            # Job summary in a nice box
            if hasattr(job, 'summary') and job.summary:
                st.markdown("""
                <div style="
                    background-color: #f0f8f0;
                    border-left: 3px solid #4CAF50;
                    padding: 12px;
                    margin: 12px 0;
                    border-radius: 0 6px 6px 0;
                ">
                """, unsafe_allow_html=True)
                st.markdown(f"**📝 Summary:**")
                st.markdown(job.summary)
                st.markdown("</div>", unsafe_allow_html=True)
            
            # Job description in collapsible section
            if job.description:
                with st.expander("📄 View Full Description"):
                    description = job.description[:1000] + ("..." if len(job.description) > 1000 else "")
                    st.markdown(description)
            
            st.markdown("</div>", unsafe_allow_html=True)
            st.markdown("---")
    
    def render_simple_job_card(self, job: JobPosting, index: int):
        """Render professional job card"""
        st.markdown(f"""
        <div class="job-card">
            <div class="job-title">💼 {job.title}</div>
            <div class="job-company">🏢 {job.company}</div>
            <div class="job-meta">
                <div class="job-meta-item">
                    📍 {job.location}
                </div>
                <div class="job-meta-item">
                    🕰️ {job.time_posted}
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Professional layout for content and button
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Show enhanced summary if available
            if hasattr(job, 'summary') and job.summary:
                with st.expander("📝 View Job Details", expanded=False):
                    st.markdown(job.summary)
            
            # Show relevance score if available
            if hasattr(job, 'relevance_score') and job.relevance_score > 0:
                score_percentage = job.relevance_score * 100
                if score_percentage >= 70:
                    score_color = "#10b981"
                    score_text = "Excellent Match"
                elif score_percentage >= 50:
                    score_color = "#f59e0b"
                    score_text = "Good Match"
                else:
                    score_color = "#ef4444"
                    score_text = "Fair Match"
                
                st.markdown(f"""
                <div style="margin: 1rem 0;">
                    <span style="color: {score_color}; font-weight: 600; font-size: 0.9rem;">
                        ★ {score_text} ({score_percentage:.0f}%)
                    </span>
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            # Professional apply button
            if job.link:
                st.link_button(
                    "🎯 Apply Now", 
                    job.link, 
                    use_container_width=True
                )
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    def render_jobs_list(self, jobs: List[JobPosting]):
        """Render professional job listings"""
        if not jobs:
            st.markdown("""
            <div style="
                text-align: center;
                padding: 3rem;
                background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
                border-radius: 16px;
                margin: 2rem 0;
                border: 1px solid #e5e7eb;
            ">
                <h3 style="color: #64748b; margin-bottom: 1rem;">🔍 No opportunities found</h3>
                <p style="color: #94a3b8;">Try different keywords or check back later for new postings.</p>
            </div>
            """, unsafe_allow_html=True)
            return
        
        # Professional job statistics
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
            color: white;
            padding: 1.5rem;
            border-radius: 12px;
            text-align: center;
            margin-bottom: 2rem;
            box-shadow: 0 4px 15px rgba(16, 185, 129, 0.2);
        ">
            <h3 style="margin: 0; font-weight: 600;">🎯 {len(jobs)} Professional Opportunities Found</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Render each job with professional styling
        for i, job in enumerate(jobs):
            self.render_simple_job_card(job, i)
    
    def render_sidebar(self):
        """Render sidebar with additional controls and information"""
        with st.sidebar:
            st.markdown("## ⚙️ Job Search Settings")
            
            # Quick filters
            st.markdown("### 🎯 Quick Filters")
            
            # Job type filter
            job_type = st.selectbox(
                "Job Type",
                options=["All Types", "Full-time", "Part-time", "Contract", "Remote"],
                index=0
            )
            
            # Experience level
            experience = st.selectbox(
                "Experience Level",
                options=["All Levels", "Entry Level", "Mid Level", "Senior Level", "Executive"],
                index=0
            )
            
            # Salary range (optional)
            salary_range = st.selectbox(
                "Salary Range",
                options=["Any Salary", "$50k+", "$75k+", "$100k+", "$150k+", "$200k+"],
                index=0
            )
            
            st.markdown("---")
            
            # Instructions
            st.markdown("### 📖 How to Use")
            st.markdown("""
            1. **Enter Keywords**: Type the job role you're looking for
            2. **Set Filters**: Choose time range and preferences
            3. **Search**: Click search to find latest jobs
            4. **Apply**: Click "Apply Now" to go to job posting
            5. **Auto-refresh**: Enable for real-time updates
            """)
            
            st.markdown("---")
            
            # Data sources
            st.markdown("### 🌐 Data Sources")
            st.markdown("""
            - **LinkedIn Jobs** (Primary)
            - **Indeed** (Fallback)
            - **Glassdoor** (Fallback)
            - **Monster** (Fallback)
            - **ZipRecruiter** (Fallback)
            """)
            
            # System status
            st.markdown("---")
            st.markdown("### 📊 System Status")
            import os
            firecrawl_configured = bool(os.getenv('FIRECRAWL_API_KEY'))
            openrouter_configured = bool(os.getenv('OPENROUTER_API_KEY'))
            
            if firecrawl_configured:
                st.success("🔥 Enhanced Crawling: ON")
            else:
                st.info("🔥 Enhanced Crawling: OFF")
                
            if openrouter_configured:
                st.success("🤖 AI Summaries: ON")
            else:
                st.info("🤖 AI Summaries: OFF")
            
            return job_type, experience, salary_range
    
    def render_loading_state(self, message: str = "Searching for jobs..."):
        """Render loading state"""
        with st.spinner(message):
            progress_bar = st.progress(0)
            for i in range(100):
                time.sleep(0.01)
                progress_bar.progress(i + 1)
            progress_bar.empty()
    
    def render_error_state(self, error_message: str):
        """Render error state"""
        st.error(f"❌ {error_message}")
        st.info("💡 Try adjusting your search terms or check your internet connection.")
    
    def render_empty_state(self):
        """Render professional empty state"""
        st.markdown("""
        <div style="
            text-align: center;
            padding: 4rem 2rem;
            background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
            border-radius: 20px;
            margin: 3rem 0;
            border: 1px solid #e5e7eb;
        ">
            <h2 style="color: #334155; margin-bottom: 1rem; font-weight: 600;">
                🚀 Ready to Advance Your Career?
            </h2>
            <p style="color: #64748b; font-size: 1.1rem; margin-bottom: 2.5rem;">
                Enter your desired role above and discover professional opportunities tailored for you
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Professional quick start examples
        st.markdown("""
        <h3 style="text-align: center; color: #374151; margin-bottom: 1.5rem; font-weight: 600;">
            🔥 Popular Professional Roles
        </h3>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("💻 Senior Software Engineer", key="ex1", use_container_width=True):
                st.session_state.example_search = "senior software engineer"
                st.rerun()
        with col2:
            if st.button("📈 Senior Data Scientist", key="ex2", use_container_width=True):
                st.session_state.example_search = "senior data scientist"
                st.rerun()
        with col3:
            if st.button("📦 Product Manager", key="ex3", use_container_width=True):
                st.session_state.example_search = "product manager"
                st.rerun()
    
    def auto_refresh_handler(self):
        """Handle auto-refresh functionality"""
        if st.session_state.auto_refresh and st.session_state.last_search:
            # Auto-refresh every 60 seconds
            time.sleep(60)
            st.rerun()
    
    def update_jobs(self, jobs: List[JobPosting]):
        """Update jobs in session state"""
        st.session_state.jobs = jobs
        st.session_state.last_update = datetime.now()
        
        if jobs:
            st.session_state.search_count += 1