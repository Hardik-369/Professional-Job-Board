import os
import logging
from typing import List, Dict, Optional
from googlesearch import search
import requests
from firecrawl import FirecrawlApp
from crawler_agent import JobPosting, CrawlerAgent
import time
from urllib.parse import urlparse
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SearchAgent:
    """Agent responsible for finding job postings using Google Search as fallback"""
    
    def __init__(self, firecrawl_api_key: Optional[str] = None):
        """Initialize the search agent"""
        self.firecrawl_api_key = firecrawl_api_key or os.getenv('FIRECRAWL_API_KEY')
        if self.firecrawl_api_key:
            try:
                self.firecrawl = FirecrawlApp(api_key=self.firecrawl_api_key)
            except Exception as e:
                logger.error(f"Failed to initialize Firecrawl: {e}")
                self.firecrawl = None
        else:
            self.firecrawl = None
            
        self.crawler_agent = CrawlerAgent(firecrawl_api_key)
    
    def build_search_queries(self, keywords: str) -> List[str]:
        """Build Google search queries for job hunting"""
        queries = []
        
        # LinkedIn specific searches
        queries.extend([
            f'site:linkedin.com/jobs "{keywords}" "posted" "ago"',
            f'site:linkedin.com/jobs/{keywords.replace(" ", "-")}',
            f'linkedin jobs {keywords} recent',
        ])
        
        # Other job sites
        job_sites = ['indeed.com', 'glassdoor.com', 'monster.com', 'ziprecruiter.com']
        for site in job_sites:
            queries.append(f'site:{site} "{keywords}" jobs')
        
        # General job searches
        queries.extend([
            f'"{keywords}" jobs "posted today"',
            f'"{keywords}" hiring "apply now"',
            f'latest {keywords} job openings'
        ])
        
        return queries[:5]  # Limit to 5 queries to avoid rate limiting
    
    def google_search_jobs(self, keywords: str, max_results: int = 10) -> List[str]:
        """Search for job URLs using Google Search"""
        job_urls = []
        
        try:
            queries = self.build_search_queries(keywords)
            
            for query in queries:
                try:
                    logger.info(f"Searching Google for: {query}")
                    
                    # Use googlesearch-python with rate limiting
                    search_results = search(
                        query, 
                        num_results=max_results // len(queries) + 2,
                        sleep_interval=1,  # 1 second between requests
                        lang='en'
                    )
                    
                    for url in search_results:
                        if self.is_valid_job_url(url):
                            job_urls.append(url)
                            
                    # Rate limiting between queries
                    time.sleep(2)
                    
                except Exception as e:
                    logger.warning(f"Error in Google search for query '{query}': {e}")
                    continue
        
        except Exception as e:
            logger.error(f"Error in Google search: {e}")
        
        # Remove duplicates and limit results
        unique_urls = list(dict.fromkeys(job_urls))  # Preserves order
        return unique_urls[:max_results]
    
    def is_valid_job_url(self, url: str) -> bool:
        """Check if URL is likely a job posting"""
        if not url:
            return False
            
        # Job-related keywords in URL
        job_indicators = [
            'job', 'career', 'position', 'opening', 'hiring', 
            'employment', 'vacancy', 'work', 'apply'
        ]
        
        # Known job sites
        job_sites = [
            'linkedin.com/jobs', 'indeed.com', 'glassdoor.com',
            'monster.com', 'ziprecruiter.com', 'simplyhired.com'
        ]
        
        url_lower = url.lower()
        
        # Check for job sites
        for site in job_sites:
            if site in url_lower:
                return True
        
        # Check for job indicators
        for indicator in job_indicators:
            if indicator in url_lower:
                return True
        
        return False
    
    def extract_job_from_url(self, url: str) -> Optional[JobPosting]:
        """Extract job information from a given URL"""
        try:
            if 'linkedin.com/jobs' in url:
                return self.extract_linkedin_job(url)
            else:
                return self.extract_generic_job(url)
                
        except Exception as e:
            logger.warning(f"Error extracting job from URL {url}: {e}")
            return None
    
    def extract_linkedin_job(self, url: str) -> Optional[JobPosting]:
        """Extract job info from LinkedIn URL"""
        try:
            if self.firecrawl:
                result = self.firecrawl.scrape_url(
                    url,
                    params={
                        'formats': ['markdown'],
                        'timeout': 15000
                    }
                )
                
                if result and 'markdown' in result:
                    return self.parse_linkedin_markdown(result['markdown'], url)
            
            # Fallback to requests
            return self.extract_with_requests(url)
            
        except Exception as e:
            logger.warning(f"Error extracting LinkedIn job: {e}")
            return None
    
    def extract_generic_job(self, url: str) -> Optional[JobPosting]:
        """Extract job info from generic job URL"""
        try:
            if self.firecrawl:
                result = self.firecrawl.scrape_url(
                    url,
                    params={
                        'formats': ['markdown'],
                        'timeout': 15000
                    }
                )
                
                if result and 'markdown' in result:
                    return self.parse_generic_markdown(result['markdown'], url)
            
            # Fallback to requests
            return self.extract_with_requests(url)
            
        except Exception as e:
            logger.warning(f"Error extracting generic job: {e}")
            return None
    
    def parse_linkedin_markdown(self, markdown: str, url: str) -> Optional[JobPosting]:
        """Parse LinkedIn job from markdown content"""
        try:
            lines = markdown.split('\n')
            title = ""
            company = ""
            location = ""
            
            for i, line in enumerate(lines):
                line = line.strip()
                
                # Look for job title (usually first heading)
                if line.startswith('#') and not title:
                    title = re.sub(r'^#+\s*', '', line)
                
                # Look for company name
                if any(keyword in line.lower() for keyword in ['company:', 'at ', 'employer:']):
                    company = line.split(':')[-1].strip() if ':' in line else line
                
                # Look for location
                if any(keyword in line.lower() for keyword in ['location:', 'city:', 'remote']):
                    location = line.split(':')[-1].strip() if ':' in line else line
            
            if title:
                return JobPosting(
                    title=title,
                    company=company or "Unknown Company",
                    location=location or "Unknown Location", 
                    time_posted="Recent",
                    link=url,
                    description=markdown[:500]  # First 500 chars as description
                )
                
        except Exception as e:
            logger.warning(f"Error parsing LinkedIn markdown: {e}")
        
        return None
    
    def parse_generic_markdown(self, markdown: str, url: str) -> Optional[JobPosting]:
        """Parse generic job posting from markdown content"""
        try:
            lines = markdown.split('\n')
            title = ""
            company = ""
            location = ""
            
            # Extract domain for company name fallback
            domain = urlparse(url).netloc.replace('www.', '')
            
            for line in lines:
                line = line.strip()
                
                # Look for job title
                if line.startswith('#') and not title:
                    title = re.sub(r'^#+\s*', '', line)
                    break
            
            # Use domain as company if not found
            company = company or domain.split('.')[0].title()
            
            if title:
                return JobPosting(
                    title=title,
                    company=company,
                    location=location or "Unknown Location",
                    time_posted="Recent",
                    link=url,
                    description=markdown[:500]
                )
                
        except Exception as e:
            logger.warning(f"Error parsing generic markdown: {e}")
        
        return None
    
    def extract_with_requests(self, url: str) -> Optional[JobPosting]:
        """Fallback extraction using requests and basic parsing"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract title from page title or h1
                title = ""
                if soup.title:
                    title = soup.title.get_text().strip()
                elif soup.h1:
                    title = soup.h1.get_text().strip()
                
                # Basic company extraction
                domain = urlparse(url).netloc.replace('www.', '')
                company = domain.split('.')[0].title()
                
                if title:
                    return JobPosting(
                        title=title,
                        company=company,
                        location="Unknown Location",
                        time_posted="Recent", 
                        link=url
                    )
                    
        except Exception as e:
            logger.warning(f"Error with requests extraction: {e}")
        
        return None
    
    def search_and_extract_jobs(self, keywords: str, max_jobs: int = 10) -> List[JobPosting]:
        """Main method to search and extract jobs"""
        logger.info(f"Searching for jobs with keywords: {keywords}")
        
        # Get job URLs from Google search
        job_urls = self.google_search_jobs(keywords, max_jobs * 2)  # Get more URLs than needed
        
        jobs = []
        for url in job_urls:
            if len(jobs) >= max_jobs:
                break
                
            job = self.extract_job_from_url(url)
            if job:
                jobs.append(job)
                
            # Rate limiting
            time.sleep(1)
        
        logger.info(f"Successfully extracted {len(jobs)} jobs from search")
        return jobs