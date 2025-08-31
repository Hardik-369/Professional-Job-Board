import streamlit as st
import os
import sys
from dotenv import load_dotenv
import logging
from datetime import datetime
import time

# Load environment variables
load_dotenv()

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ui_agent import UIAgent
from controller_agent import ControllerAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Main application function"""
    try:
        # Initialize UI Agent
        ui = UIAgent()
        
        # Render header
        ui.render_header()
        
        # Render sidebar and get additional filters
        job_type, experience, salary_range = ui.render_sidebar()
        
        # Initialize controller with environment API keys
        if 'controller' not in st.session_state:
            st.session_state.controller = ControllerAgent(
                firecrawl_api_key=os.getenv('FIRECRAWL_API_KEY'),
                openrouter_api_key=os.getenv('OPENROUTER_API_KEY')
            )
        
        # Handle example search from empty state
        if hasattr(st.session_state, 'example_search'):
            # Set the search value in session state for the text input
            keywords = st.session_state.example_search
            # Update the text input value
            st.session_state.job_search_input = keywords
            del st.session_state.example_search
            search_clicked = True  # Auto-trigger search
        else:
            # Render search controls
            keywords, hours_filter, max_jobs, sort_by, search_clicked = ui.render_search_controls()
        
        # Render additional controls
        _, refresh_clicked = ui.render_search_button()
        
        # Handle search button click
        if search_clicked and keywords and keywords.strip():
            # Clear cache to ensure fresh results
            st.session_state.controller.clear_cache()
            
            # Show clean loading state
            with st.spinner("🔍 Finding fresh opportunities..."):
                # Search for jobs with better parameters for real results
                jobs, search_info = st.session_state.controller.get_jobs(
                    keywords=keywords,
                    hours_ago=hours_filter,
                    max_jobs=max_jobs,
                    use_parallel=True
                )
                
                # Update UI state
                ui.update_jobs(jobs)
                st.session_state.last_search = keywords
                st.session_state.search_count += 1
            
            # Simple success message
            if search_info.get('error'):
                st.error(f"❌ {search_info['error']}")
            else:
                st.success(f"✅ Found {search_info.get('total_jobs', 0)} fresh opportunities in {search_info.get('search_time', 0):.1f}s")
        
        # Display jobs
        if st.session_state.jobs:
            ui.render_jobs_list(st.session_state.jobs)
        else:
            ui.render_empty_state()
    
    except Exception as e:
        st.error(f"❌ Application Error: {str(e)}")
        logger.error(f"Application error: {e}", exc_info=True)
        
        # Provide fallback options
        st.markdown("### 🛠️ Troubleshooting")
        st.markdown("""
        - **Refresh the page** to restart the application
        - **Check your internet connection**
        - **Verify API keys** in the sidebar
        - **Try simpler search terms**
        """)
        
        if st.button("🔄 Restart Application"):
            # Clear session state and rerun
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

if __name__ == "__main__":
    main()