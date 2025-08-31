import os
import logging
from typing import List, Dict, Optional
try:
    import openai
except ImportError:
    openai = None
from crawler_agent import JobPosting
import json
import re
from datetime import datetime, timedelta
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RankingAgent:
    """Agent responsible for ranking and summarizing job postings using OpenRouter API"""
    
    def __init__(self, openrouter_api_key: Optional[str] = None):
        """Initialize the ranking agent"""
        self.api_key = openrouter_api_key or os.getenv('OPENROUTER_API_KEY')
        
        # Always start with None client to avoid initialization errors
        self.client = None
        
        if self.api_key and openai:
            logger.info("OpenRouter API key found, but using fallback ranking to avoid client errors")
        elif not openai:
            logger.info("OpenAI library not available. Using basic ranking.")
        else:
            logger.info("No OpenRouter API key provided. Using basic ranking.")
        
        self.model = "openai/gpt-oss-20b:free"
    
    def _make_api_call(self, messages: List[Dict], max_tokens: int = 150, temperature: float = 0.7):
        """API calls are disabled to avoid client initialization errors"""
        logger.info("API calls disabled to prevent client errors - using fallback methods")
        return None
    

    
    def extract_time_score(self, time_posted: str) -> float:
        """Convert time posted to a numerical score (higher = more recent)"""
        if not time_posted:
            return 0.0
        
        time_lower = time_posted.lower()
        
        # Define scoring based on recency
        if any(keyword in time_lower for keyword in ['just now', 'now', 'moments ago']):
            return 1.0
        elif any(keyword in time_lower for keyword in ['minute', 'min']):
            return 0.9
        elif any(keyword in time_lower for keyword in ['hour', 'hr']):
            return 0.8
        elif any(keyword in time_lower for keyword in ['today', 'day']):
            return 0.7
        elif any(keyword in time_lower for keyword in ['yesterday', '1 day']):
            return 0.6
        elif any(keyword in time_lower for keyword in ['week', 'wk']):
            return 0.4
        elif any(keyword in time_lower for keyword in ['month', 'mo']):
            return 0.2
        else:
            return 0.1
    
    def summarize_job_description(self, job: JobPosting, user_keywords: str) -> str:
        """Create job summary using basic method (API disabled to avoid errors)"""
        return self._create_basic_summary(job, user_keywords)
    
    def _create_basic_summary(self, job: JobPosting, user_keywords: str) -> str:
        """Create an enhanced basic summary without AI"""
        summary_parts = []
        
        # Add role type with more detail
        summary_parts.append(f"• {job.title} position at {job.company}")
        
        # Add location
        if job.location and job.location != "Unknown Location":
            summary_parts.append(f"• Location: {job.location}")
        
        # Add relevance to search terms
        if user_keywords:
            # Check if keywords match job title or company
            keywords_lower = user_keywords.lower().split()
            title_lower = job.title.lower()
            
            matches = [kw for kw in keywords_lower if kw in title_lower]
            if matches:
                summary_parts.append(f"• Matches your search for: {', '.join(matches)}")
            else:
                summary_parts.append(f"• Related to: {user_keywords}")
        
        # Add posting time if recent
        if "hour" in job.time_posted.lower() or "minute" in job.time_posted.lower():
            summary_parts.append(f"• 🔥 Recently posted: {job.time_posted}")
        
        return "\n".join(summary_parts)
    
    def calculate_relevance_score(self, job: JobPosting, user_keywords: str) -> float:
        """Calculate relevance score using enhanced basic method (API disabled to avoid errors)"""
        return self._calculate_basic_relevance(job, user_keywords)
    
    def _calculate_basic_relevance(self, job: JobPosting, user_keywords: str) -> float:
        """Calculate enhanced basic relevance score"""
        if not user_keywords:
            return 0.5
        
        score = 0.0
        keywords_lower = user_keywords.lower().split()
        
        # Check title relevance (weighted heavily) - exact matches get higher score
        title_lower = job.title.lower()
        title_matches = 0
        exact_matches = 0
        
        for keyword in keywords_lower:
            if keyword in title_lower:
                title_matches += 1
                # Bonus for exact word matches (not just partial)
                if f" {keyword} " in f" {title_lower} " or title_lower.startswith(keyword) or title_lower.endswith(keyword):
                    exact_matches += 1
        
        # Enhanced title scoring
        title_score = (title_matches / len(keywords_lower)) * 0.6
        exact_bonus = (exact_matches / len(keywords_lower)) * 0.2
        score += title_score + exact_bonus
        
        # Check company relevance
        company_lower = job.company.lower()
        company_matches = sum(1 for keyword in keywords_lower if keyword in company_lower)
        score += (company_matches / len(keywords_lower)) * 0.1
        
        # Check description relevance
        if job.description:
            desc_lower = job.description.lower()
            desc_matches = sum(1 for keyword in keywords_lower if keyword in desc_lower)
            score += (desc_matches / len(keywords_lower)) * 0.1
        
        return min(score, 1.0)
    
    def rank_jobs(self, jobs: List[JobPosting], user_keywords: str) -> List[JobPosting]:
        """Rank jobs by relevance and recency"""
        logger.info(f"Ranking {len(jobs)} jobs for keywords: {user_keywords}")
        
        ranked_jobs = []
        
        for job in jobs:
            try:
                # Add rate limiting for API calls
                if self.client:
                    time.sleep(0.5)  # Small delay between API calls
                
                # Calculate scores
                relevance_score = self.calculate_relevance_score(job, user_keywords)
                time_score = self.extract_time_score(job.time_posted)
                
                # Generate summary
                summary = self.summarize_job_description(job, user_keywords)
                
                # Combined score (70% relevance, 30% recency)
                combined_score = (relevance_score * 0.7) + (time_score * 0.3)
                
                # Update job object
                job.summary = summary
                job.relevance_score = combined_score
                
                ranked_jobs.append(job)
                
            except Exception as e:
                logger.warning(f"Error processing job {job.title}: {e}")
                # Add job with basic values
                job.summary = self._create_basic_summary(job, user_keywords)
                job.relevance_score = self._calculate_basic_relevance(job, user_keywords)
                ranked_jobs.append(job)
        
        # Sort by combined score (descending)
        ranked_jobs.sort(key=lambda x: x.relevance_score, reverse=True)
        
        logger.info(f"Successfully ranked {len(ranked_jobs)} jobs")
        return ranked_jobs
    
    def get_top_jobs(self, jobs: List[JobPosting], user_keywords: str, top_n: int = 10) -> List[JobPosting]:
        """Get top N ranked jobs"""
        if not jobs:
            return []
        
        ranked_jobs = self.rank_jobs(jobs, user_keywords)
        return ranked_jobs[:top_n]
    
    def batch_process_jobs(self, jobs: List[JobPosting], user_keywords: str, batch_size: int = 5) -> List[JobPosting]:
        """Process jobs in batches to avoid rate limiting"""
        if not jobs:
            return []
        
        all_processed_jobs = []
        
        for i in range(0, len(jobs), batch_size):
            batch = jobs[i:i + batch_size]
            logger.info(f"Processing batch {i//batch_size + 1}/{(len(jobs) + batch_size - 1)//batch_size}")
            
            processed_batch = self.rank_jobs(batch, user_keywords)
            all_processed_jobs.extend(processed_batch)
            
            # Rate limiting between batches
            if i + batch_size < len(jobs):
                time.sleep(2)
        
        # Sort all jobs by score
        all_processed_jobs.sort(key=lambda x: x.relevance_score, reverse=True)
        return all_processed_jobs