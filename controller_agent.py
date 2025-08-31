import os
import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
import streamlit as st
from crawler_agent import CrawlerAgent, JobPosting
from search_agent import SearchAgent
from ranking_agent import RankingAgent
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ControllerAgent:
    """Main controller that orchestrates all other agents"""
    
    def __init__(self, firecrawl_api_key: Optional[str] = None, openrouter_api_key: Optional[str] = None):
        """Initialize the controller with all agents"""
        self.firecrawl_api_key = firecrawl_api_key
        self.openrouter_api_key = openrouter_api_key
        
        # Initialize agents
        self.crawler_agent = CrawlerAgent(firecrawl_api_key)
        self.search_agent = SearchAgent(firecrawl_api_key)
        self.ranking_agent = RankingAgent(openrouter_api_key)
        
        # Cache for results
        self.cache = {}
        self.cache_duration = timedelta(minutes=5)  # Cache for 5 minutes
        
        # Rate limiting
        self.last_request_time = {}
        self.min_request_interval = 30  # Minimum 30 seconds between requests
    
    def _get_cache_key(self, keywords: str, hours_ago: int) -> str:
        """Generate cache key for given parameters"""
        return f"{keywords.lower().strip()}_{hours_ago}"
    
    def _is_cached_valid(self, cache_key: str) -> bool:
        """Check if cached result is still valid"""
        if cache_key not in self.cache:
            return False
        
        cached_time, _ = self.cache[cache_key]
        return datetime.now() - cached_time < self.cache_duration
    
    def _should_rate_limit(self, keywords: str) -> bool:
        """Check if we should rate limit the request"""
        if keywords not in self.last_request_time:
            return False
        
        time_since_last = time.time() - self.last_request_time[keywords]
        return time_since_last < self.min_request_interval
    
    def _update_rate_limit(self, keywords: str):
        """Update rate limiting timestamp"""
        self.last_request_time[keywords] = time.time()
    
    def search_jobs_parallel(self, keywords: str, hours_ago: int = 1, max_jobs: int = 10) -> Tuple[List[JobPosting], Dict[str, any]]:
        """Search for jobs using parallel execution of multiple agents with fresh results"""
        
        # Always clear cache for real-time fresh results
        self.clear_cache()
        
        # Skip cache and rate limiting for real-time functionality
        logger.info(f"Starting fresh parallel job search for: {keywords}")
        start_time = time.time()
        
        all_jobs = []
        search_results = {
            "crawler_jobs": 0,
            "search_jobs": 0,
            "total_jobs": 0,
            "search_time": 0,
            "errors": []
        }
        
        # Use ThreadPoolExecutor for parallel execution
        with ThreadPoolExecutor(max_workers=2) as executor:
            # Submit tasks
            crawler_future = executor.submit(self._safe_crawler_search, keywords, hours_ago)
            search_future = executor.submit(self._safe_search_agent, keywords, max_jobs // 2)
            
            # Collect results as they complete
            for future in as_completed([crawler_future, search_future]):
                try:
                    jobs, source = future.result(timeout=60)  # 60 second timeout
                    if jobs:
                        all_jobs.extend(jobs)
                        search_results[f"{source}_jobs"] = len(jobs)
                        logger.info(f"{source} found {len(jobs)} jobs")
                except Exception as e:
                    error_msg = f"Error in parallel search: {e}"
                    logger.error(error_msg)
                    search_results["errors"].append(error_msg)
        
        # Remove duplicates using enhanced algorithm
        unique_jobs = self._remove_duplicates(all_jobs)
        
        # Rank and limit jobs
        if unique_jobs:
            try:
                ranked_jobs = self.ranking_agent.get_top_jobs(unique_jobs, keywords, max_jobs)
            except Exception as e:
                logger.error(f"Error ranking jobs: {e}")
                ranked_jobs = unique_jobs[:max_jobs]  # Fallback to simple truncation
        else:
            ranked_jobs = []
        
        # Update search results
        search_results["total_jobs"] = len(ranked_jobs)
        search_results["search_time"] = time.time() - start_time
        
        # Don't cache for real-time fresh results
        logger.info(f"Completed fresh job search in {search_results['search_time']:.2f}s. Found {len(ranked_jobs)} unique jobs")
        return ranked_jobs, search_results
    
    def _safe_crawler_search(self, keywords: str, hours_ago: int) -> Tuple[List[JobPosting], str]:
        """Safely execute crawler search with error handling"""
        try:
            jobs = self.crawler_agent.get_jobs(keywords, hours_ago)
            return jobs, "crawler"
        except Exception as e:
            logger.error(f"Crawler agent error: {e}")
            return [], "crawler"
    
    def _safe_search_agent(self, keywords: str, max_jobs: int) -> Tuple[List[JobPosting], str]:
        """Safely execute search agent with error handling"""
        try:
            jobs = self.search_agent.search_and_extract_jobs(keywords, max_jobs)
            return jobs, "search"
        except Exception as e:
            logger.error(f"Search agent error: {e}")
            return [], "search"
    
    def _remove_duplicates(self, jobs: List[JobPosting]) -> List[JobPosting]:
        """Remove duplicate jobs using multiple sophisticated detection methods"""
        if not jobs:
            return []
            
        seen_links = set()
        seen_signatures = set()
        unique_jobs = []
        
        for job in jobs:
            # Skip jobs with empty or invalid titles
            if not job.title or job.title.strip() == "" or job.title == "Unknown Title":
                continue
                
            # Method 1: Exact link matching
            if job.link and job.link in seen_links:
                logger.debug(f"Skipping duplicate by link: {job.title} at {job.company}")
                continue
                
            # Method 2: Create normalized signature for similarity detection
            title_clean = self._normalize_text(job.title)
            company_clean = self._normalize_text(job.company)
            location_clean = self._normalize_text(job.location)
            
            # Create multiple signatures to catch variations
            signatures = [
                f"{title_clean}|{company_clean}",  # Same title + company
                f"{title_clean}|{location_clean}" if location_clean != "unknown location" else None,  # Same title + location
                job.link if job.link else None  # Exact link
            ]
            
            # Remove None signatures
            signatures = [sig for sig in signatures if sig]
            
            # Check if any signature already exists
            is_duplicate = False
            for signature in signatures:
                if signature in seen_signatures:
                    logger.debug(f"Skipping duplicate by signature '{signature}': {job.title} at {job.company}")
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                # Add all signatures to seen set
                for signature in signatures:
                    seen_signatures.add(signature)
                    
                # Add link to seen links
                if job.link:
                    seen_links.add(job.link)
                    
                unique_jobs.append(job)
                logger.debug(f"Added unique job: {job.title} at {job.company}")
        
        logger.info(f"Filtered {len(jobs)} jobs down to {len(unique_jobs)} unique jobs")
        return unique_jobs
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text for better duplicate detection"""
        if not text:
            return ""
            
        import re
        
        # Convert to lowercase
        normalized = text.lower().strip()
        
        # Remove common variations and noise
        normalized = re.sub(r'\s+', ' ', normalized)  # Multiple spaces to single
        normalized = re.sub(r'[^a-z0-9\s]', '', normalized)  # Remove special chars
        normalized = re.sub(r'\b(remote|hybrid|on site|onsite)\b', '', normalized)  # Remove work type
        normalized = re.sub(r'\b(junior|senior|lead|staff|principal)\b', '', normalized)  # Remove seniority
        normalized = re.sub(r'\b(full time|part time|contract|freelance)\b', '', normalized)  # Remove employment type
        
        return normalized.strip()
    
    def search_jobs_sequential(self, keywords: str, hours_ago: int = 1, max_jobs: int = 10) -> Tuple[List[JobPosting], Dict[str, any]]:
        """Search for jobs using sequential execution (fallback method)"""
        logger.info(f"Starting sequential job search for: {keywords}")
        start_time = time.time()
        
        search_results = {
            "crawler_jobs": 0,
            "search_jobs": 0,
            "total_jobs": 0,
            "search_time": 0,
            "errors": []
        }
        
        all_jobs = []
        
        # Try crawler first
        try:
            crawler_jobs = self.crawler_agent.get_jobs(keywords, hours_ago)
            all_jobs.extend(crawler_jobs)
            search_results["crawler_jobs"] = len(crawler_jobs)
            logger.info(f"Crawler found {len(crawler_jobs)} jobs")
        except Exception as e:
            error_msg = f"Crawler error: {e}"
            logger.error(error_msg)
            search_results["errors"].append(error_msg)
        
        # If we need more jobs, try search agent
        if len(all_jobs) < max_jobs:
            try:
                search_jobs = self.search_agent.search_and_extract_jobs(keywords, max_jobs - len(all_jobs))
                all_jobs.extend(search_jobs)
                search_results["search_jobs"] = len(search_jobs)
                logger.info(f"Search agent found {len(search_jobs)} jobs")
            except Exception as e:
                error_msg = f"Search agent error: {e}"
                logger.error(error_msg)
                search_results["errors"].append(error_msg)
        
        # Remove duplicates and rank
        unique_jobs = self._remove_duplicates(all_jobs)
        
        if unique_jobs:
            try:
                ranked_jobs = self.ranking_agent.get_top_jobs(unique_jobs, keywords, max_jobs)
            except Exception as e:
                logger.error(f"Error ranking jobs: {e}")
                ranked_jobs = unique_jobs[:max_jobs]
        else:
            ranked_jobs = []
        
        search_results["total_jobs"] = len(ranked_jobs)
        search_results["search_time"] = time.time() - start_time
        
        logger.info(f"Sequential search completed in {search_results['search_time']:.2f}s")
        return ranked_jobs, search_results
    
    def get_jobs(self, keywords: str, hours_ago: int = 1, max_jobs: int = 10, use_parallel: bool = True) -> Tuple[List[JobPosting], Dict[str, any]]:
        """Main method to get jobs with error handling and fallbacks"""
        if not keywords or not keywords.strip():
            return [], {"error": "Keywords are required"}
        
        try:
            if use_parallel:
                return self.search_jobs_parallel(keywords, hours_ago, max_jobs)
            else:
                return self.search_jobs_sequential(keywords, hours_ago, max_jobs)
        except Exception as e:
            logger.error(f"Critical error in job search: {e}")
            return [], {"error": f"Search failed: {str(e)}"}
    
    def clear_cache(self):
        """Clear the job cache"""
        self.cache.clear()
        logger.info("Cache cleared")
    
    def get_cache_info(self) -> Dict[str, any]:
        """Get information about cached results"""
        cache_info = {
            "cache_size": len(self.cache),
            "cache_keys": list(self.cache.keys()),
            "cache_duration_minutes": self.cache_duration.total_seconds() / 60
        }
        return cache_info
    
    def health_check(self) -> Dict[str, any]:
        """Perform health check on all agents"""
        health = {
            "timestamp": datetime.now().isoformat(),
            "crawler_agent": "unknown",
            "search_agent": "unknown", 
            "ranking_agent": "unknown",
            "firecrawl_configured": bool(self.firecrawl_api_key),
            "openrouter_configured": bool(self.openrouter_api_key)
        }
        
        # Test crawler agent
        try:
            test_url = self.crawler_agent.build_linkedin_url("test")
            health["crawler_agent"] = "healthy" if test_url else "unhealthy"
        except Exception:
            health["crawler_agent"] = "unhealthy"
        
        # Test search agent
        try:
            test_queries = self.search_agent.build_search_queries("test")
            health["search_agent"] = "healthy" if test_queries else "unhealthy"
        except Exception:
            health["search_agent"] = "unhealthy"
        
        # Test ranking agent
        try:
            test_score = self.ranking_agent._calculate_basic_relevance(
                JobPosting("test", "test", "test", "test", "test"), "test"
            )
            health["ranking_agent"] = "healthy" if test_score >= 0 else "unhealthy"
        except Exception:
            health["ranking_agent"] = "unhealthy"
        
        return health