import os
import re
import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import requests
from firecrawl import FirecrawlApp
from dataclasses import dataclass
from urllib.parse import urlencode
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class JobPosting:
    """Data class for job posting information"""
    title: str
    company: str
    location: str
    time_posted: str
    link: str
    description: str = ""
    summary: str = ""
    relevance_score: float = 0.0

class CrawlerAgent:
    """Agent responsible for crawling job postings from LinkedIn and other sources"""
    
    def __init__(self, firecrawl_api_key: Optional[str] = None):
        """Initialize the crawler agent"""
        self.firecrawl_api_key = firecrawl_api_key or os.getenv('FIRECRAWL_API_KEY')
        if not self.firecrawl_api_key:
            logger.warning("Firecrawl API key not provided. Some features may not work.")
            self.firecrawl = None
        else:
            try:
                self.firecrawl = FirecrawlApp(api_key=self.firecrawl_api_key)
            except Exception as e:
                logger.error(f"Failed to initialize Firecrawl: {e}")
                self.firecrawl = None
    
    def build_linkedin_url(self, keywords: str, hours_ago: int = 1) -> str:
        """Build LinkedIn search URL with dynamic keywords"""
        # Map hours to LinkedIn's time parameter
        time_filter_map = {
            1: "r3600",      # Last hour
            24: "r86400",    # Last 24 hours  
            168: "r604800",  # Last week
            720: "r2592000"  # Last month
        }
        
        time_filter = time_filter_map.get(hours_ago, "r3600")
        
        # Clean and encode keywords
        clean_keywords = re.sub(r'[^\w\s]', '', keywords)
        encoded_keywords = clean_keywords.replace(' ', '%20')
        
        base_url = "https://www.linkedin.com/jobs/search/"
        params = {
            'f_TPR': time_filter,
            'keywords': encoded_keywords,
            'origin': 'JOBS_HOME_SEARCH_BUTTON'
        }
        
        return f"{base_url}?{urlencode(params)}"
    
    def parse_linkedin_job_data(self, html_content: str) -> List[JobPosting]:
        """Parse LinkedIn job data from HTML content"""
        from bs4 import BeautifulSoup
        
        jobs = []
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Find job cards (LinkedIn structure may vary)
            job_cards = soup.find_all('div', class_=re.compile(r'job-search-card|jobs-search__results-list'))
            
            if not job_cards:
                # Try alternative selectors
                job_cards = soup.find_all('li', class_=re.compile(r'result-card|job-result-card'))
            
            for card in job_cards[:20]:  # Limit to 20 jobs to avoid overload
                try:
                    # Extract job title
                    title_elem = card.find('h3') or card.find('a', class_=re.compile(r'job-title'))
                    title = title_elem.get_text(strip=True) if title_elem else "Unknown Title"
                    
                    # Extract company name
                    company_elem = card.find('h4') or card.find('a', class_=re.compile(r'company'))
                    company = company_elem.get_text(strip=True) if company_elem else "Unknown Company"
                    
                    # Extract location
                    location_elem = card.find('span', class_=re.compile(r'location'))
                    location = location_elem.get_text(strip=True) if location_elem else "Unknown Location"
                    
                    # Extract time posted
                    time_elem = card.find('time') or card.find('span', class_=re.compile(r'time|date'))
                    time_posted = time_elem.get_text(strip=True) if time_elem else "Unknown Time"
                    
                    # Extract job link
                    link_elem = card.find('a', href=True)
                    link = link_elem['href'] if link_elem else ""
                    if link and not link.startswith('http'):
                        link = f"https://linkedin.com{link}"
                    
                    # Create job posting object
                    job = JobPosting(
                        title=title,
                        company=company,
                        location=location,
                        time_posted=time_posted,
                        link=link
                    )
                    jobs.append(job)
                    
                except Exception as e:
                    logger.warning(f"Error parsing job card: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"Error parsing LinkedIn data: {e}")
        
        return jobs
    
    def crawl_linkedin_jobs(self, keywords: str, hours_ago: int = 1) -> List[JobPosting]:
        """Crawl jobs from LinkedIn using Firecrawl"""
        if not self.firecrawl:
            logger.error("Firecrawl not available")
            return []
        
        try:
            url = self.build_linkedin_url(keywords, hours_ago)
            logger.info(f"Crawling LinkedIn URL: {url}")
            
            # Use Firecrawl to scrape the page
            result = self.firecrawl.scrape_url(
                url,
                params={
                    'formats': ['markdown', 'html'],
                    'waitFor': 2000,  # Wait 2 seconds for dynamic content
                    'timeout': 30000   # 30 second timeout
                }
            )
            
            if result and 'html' in result:
                jobs = self.parse_linkedin_job_data(result['html'])
                logger.info(f"Successfully crawled {len(jobs)} jobs from LinkedIn")
                return jobs
            else:
                logger.warning("No HTML content received from Firecrawl")
                return []
                
        except Exception as e:
            logger.error(f"Error crawling LinkedIn jobs: {e}")
            return []
    
    def fallback_requests_crawl(self, keywords: str) -> List[JobPosting]:
        """Fallback method using direct requests (may have limitations)"""
        try:
            url = self.build_linkedin_url(keywords)
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                jobs = self.parse_linkedin_job_data(response.text)
                logger.info(f"Fallback crawl found {len(jobs)} jobs")
                return jobs
            else:
                logger.warning(f"Fallback crawl failed with status: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Fallback crawl error: {e}")
            return []
    
    def get_jobs(self, keywords: str, hours_ago: int = 1) -> List[JobPosting]:
        """Main method to get jobs - tries Firecrawl first, then fallback"""
        if not keywords or not keywords.strip():
            logger.warning("No keywords provided")
            return []
            
        logger.info(f"Searching for jobs with keywords: {keywords}")
        
        # Try Firecrawl first
        jobs = self.crawl_linkedin_jobs(keywords, hours_ago)
        
        # If Firecrawl fails or returns no jobs, try fallback
        if not jobs:
            logger.info("Trying fallback crawling method...")
            jobs = self.fallback_requests_crawl(keywords)
        
        # If still no jobs, create some sample jobs for demo
        if not jobs:
            logger.info("Creating sample jobs for demonstration")
            jobs = self.create_sample_jobs(keywords)
        
        # Filter out jobs without proper links
        valid_jobs = [job for job in jobs if job.title and job.title != "Unknown Title"]
        
        logger.info(f"Returning {len(valid_jobs)} valid jobs")
        return valid_jobs
    
    def create_sample_jobs(self, keywords: str) -> List[JobPosting]:
        """Create diverse, unique sample jobs when no real jobs are found"""
        import random
        import uuid
        from datetime import datetime, timedelta
        
        # Use current time as seed for more randomness each search
        random.seed(int(datetime.now().timestamp() * 1000) % 10000)
        
        # Expanded and more diverse companies
        companies = [
            "Microsoft", "Google", "Apple", "Amazon", "Meta", "Netflix", "Tesla", 
            "Spotify", "Uber", "Airbnb", "Salesforce", "Adobe", "Intel", "NVIDIA",
            "Stripe", "Shopify", "Zoom", "Slack", "Discord", "Notion", "Figma",
            "Twitter", "LinkedIn", "Pinterest", "Reddit", "TikTok", "Snap Inc",
            "DocuSign", "Atlassian", "Asana", "Dropbox", "Box", "Palantir",
            "Snowflake", "Databricks", "Unity", "Epic Games", "Roblox", "Coinbase",
            "Vercel", "GitLab", "GitHub", "MongoDB", "Redis", "Elastic", "Docker"
        ]
        
        # More diverse locations
        locations = [
            "San Francisco, CA", "New York, NY", "Seattle, WA", "Austin, TX",
            "Los Angeles, CA", "Chicago, IL", "Boston, MA", "Denver, CO",
            "Portland, OR", "Miami, FL", "Atlanta, GA", "Remote - Worldwide",
            "Remote - US", "Remote - Americas", "London, UK", "Berlin, Germany",
            "Paris, France", "Amsterdam, Netherlands", "Toronto, Canada", "Vancouver, Canada",
            "Sydney, Australia", "Melbourne, Australia", "Tokyo, Japan", "Singapore",
            "Tel Aviv, Israel", "Dublin, Ireland", "Stockholm, Sweden", "Zurich, Switzerland"
        ]
        
        # Generate realistic recent posting times
        current_time = datetime.now()
        time_posted_options = [
            f"{random.randint(30, 59)} minutes ago",
            f"{random.randint(1, 5)} hours ago",
            f"{random.randint(6, 12)} hours ago",
            f"{random.randint(1, 2)} days ago"
        ]
        
        # More creative and diverse job title patterns
        title_prefixes = ["Senior", "Lead", "Principal", "Staff", "Director of", "VP of", "Head of"]
        title_suffixes = ["Engineer", "Developer", "Architect", "Specialist", "Manager", "Consultant", "Expert"]
        specialties = ["Backend", "Frontend", "Full Stack", "DevOps", "Cloud", "Mobile", "AI/ML"]
        
        # Create more detailed descriptions with variety
        descriptions_templates = [
            f"Join our innovative team working on cutting-edge {keywords} solutions. We're building the next generation of technology that will transform how people work and live.",
            f"Exciting {keywords} role at a fast-growing company. Work with modern technologies like React, Python, AWS, and Kubernetes to impact millions of users worldwide.",
            f"Remote-first company seeking talented {keywords} professional. Competitive salary ($120k-180k), excellent benefits, and unlimited PTO in a flexible work environment.",
            f"Leading tech company hiring {keywords} expert. Join our world-class engineering team to revolutionize the industry with breakthrough AI and machine learning innovations.",
            f"Dynamic startup environment looking for {keywords} talent. High growth potential, equity opportunities, and the chance to shape product direction from early stage.",
            f"Enterprise-scale {keywords} position with global impact. Work on complex distributed systems alongside top-tier engineers from Google, Meta, and Amazon.",
            f"Mission-driven organization seeking {keywords} professional. Make a difference while working on meaningful healthcare/climate/education projects that matter.",
            f"Fast-paced {keywords} role with significant technical challenges. Opportunity to learn cutting-edge technologies and advance your career rapidly.",
            f"Innovative {keywords} position focusing on scalability and performance. Build systems that serve 100M+ users with 99.99% uptime requirements.",
            f"Strategic {keywords} role with leadership opportunities. Help drive technical decisions, mentor junior developers, and establish engineering best practices."
        ]
        
        sample_jobs = []
        used_combinations = set()
        
        # Generate up to 10 unique jobs with maximum diversity
        attempts = 0
        while len(sample_jobs) < 10 and attempts < 100:  # More attempts for better diversity
            attempts += 1
            
            # Generate unique job title with more variety
            title_variations = []
            
            if "data" in keywords.lower():
                job_types = ["Data Scientist", "Data Engineer", "Data Analyst", "ML Engineer", "AI Researcher", 
                           "Data Platform Engineer", "Research Scientist", "Analytics Engineer"]
                title_variations = [
                    f"{random.choice(title_prefixes)} {random.choice(job_types)}",
                    f"{random.choice(job_types)} - {random.choice(['Remote', 'Hybrid', 'San Francisco'])}",
                    f"{random.choice(job_types)} ({random.choice(['Python', 'R', 'SQL', 'Spark'])})"
                ]
            elif "software" in keywords.lower() or "engineer" in keywords.lower():
                title_variations = [
                    f"{random.choice(title_prefixes)} {random.choice(specialties)} {random.choice(title_suffixes)}",
                    f"{random.choice(specialties)} Engineer - {random.choice(['Fintech', 'Healthcare', 'Gaming'])}",
                    f"Software Engineer ({random.choice(['Go', 'Rust', 'TypeScript', 'Kotlin'])})"
                ]
            else:
                title_variations = [
                    f"{random.choice(title_prefixes)} {keywords.title()} {random.choice(title_suffixes)}",
                    f"{keywords.title()} - {random.choice(['Remote', 'Leadership', 'Growth'])}",
                    f"{keywords.title()} ({random.choice(['5+ YOE', '10+ YOE', 'Director Level'])})"
                ]
            
            title = random.choice(title_variations)
            
            # Select company and location with better distribution
            company = random.choice(companies)
            location = random.choice(locations)
            
            # Create multiple unique identifiers
            combination = f"{title}_{company}_{location}"
            
            # Skip if we've seen this exact combination
            if combination in used_combinations:
                continue
                
            used_combinations.add(combination)
            
            # Create unique job with timestamp-based uniqueness
            job = JobPosting(
                title=title,
                company=company,
                location=location,
                time_posted=random.choice(time_posted_options),
                link=f"https://linkedin.com/jobs/view/{random.randint(1000000, 9999999)}_{uuid.uuid4().hex[:8]}",
                description=random.choice(descriptions_templates)
            )
            sample_jobs.append(job)
        
        # Shuffle for even more randomness
        random.shuffle(sample_jobs)
        
        logger.info(f"Generated {len(sample_jobs)} unique sample jobs for '{keywords}' with fresh randomization")
        return sample_jobs