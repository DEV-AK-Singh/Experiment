# src/crawler/deep_crawler.py
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import hashlib
from urllib.parse import urlparse
from collections import deque
from typing import Dict, Any, Optional

from ..models.data_models import *
from .data_extractor import DataExtractor
from config import Config

class DeepWebCrawler:
    """Main crawler class for deep web crawling"""
    
    def __init__(self, max_depth: int = Config.MAX_DEPTH, max_pages_per_level: int = Config.MAX_PAGES_PER_LEVEL):
        self.max_depth = max_depth
        self.max_pages_per_level = max_pages_per_level
        self.visited_urls = set()
        self.crawl_data = {}
        self.driver = None
        
    def setup_driver(self) -> bool:
        """Setup Chrome driver"""
        try:
            chrome_options = Options()
            if Config.BROWSER_HEADLESS:
                chrome_options.add_argument("--headless=new")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument(f"--window-size={Config.BROWSER_WINDOW_SIZE}")
            chrome_options.add_argument(f"--user-agent={Config.USER_AGENT}")
            
            self.driver = webdriver.Chrome(options=chrome_options)
            return True
        except Exception as e:
            print(f"❌ ChromeDriver error: {e}")
            return False
    
    def get_domain(self, url: str) -> str:
        """Extract domain from URL"""
        return urlparse(url).netloc
    
    def is_same_domain(self, url1: str, url2: str) -> bool:
        """Check if two URLs belong to the same domain"""
        return self.get_domain(url1) == self.get_domain(url2)
    
    def should_crawl(self, url: str, base_domain: str) -> bool:
        """Check if URL should be crawled"""
        if url in self.visited_urls:
            return False
        
        if not url.startswith(('http://', 'https://')):
            return False
            
        # Skip non-web resources
        if any(ext in url.lower() for ext in ['.pdf', '.jpg', '.png', '.gif', '.zip', '.exe']):
            return False
            
        # Only crawl same domain
        return self.get_domain(url) == base_domain
    
    def crawl_page(self, url: str, depth: int) -> Optional[PageData]:
        """Crawl a single page"""
        if depth > self.max_depth or url in self.visited_urls:
            return None
        
        print(f"🔍 Crawling (Level {depth}): {url}")
        self.visited_urls.add(url)
        
        try:
            if self.driver is None:
                self.setup_driver()
            else:
                self.driver.get(url)
                time.sleep(Config.PAGE_LOAD_TIMEOUT)
                
                # Get page source and parse with BeautifulSoup
                page_source = self.driver.page_source
                soup = BeautifulSoup(page_source, 'html.parser')
                
                # Extract comprehensive data
                page_data = DataExtractor.extract_comprehensive_data(url, soup)
                
                if page_data:
                    # Generate unique key for this page
                    page_key = hashlib.md5(url.encode()).hexdigest()[:10]
                    self.crawl_data[page_key] = page_data
                    
                    return page_data
                else:
                    return None
                    
        except Exception as e:
            print(f"❌ Failed to crawl {url}: {e}")
            return None
    
    def deep_crawl(self, start_url: str) -> Dict[str, Any]:
        """Perform deep crawling starting from URL"""
        if not self.setup_driver():
            return {'error': 'Failed to initialize browser'}
        
        try:
            base_domain = self.get_domain(start_url)
            queue = deque([(start_url, 0)])  # (url, depth)
            
            crawl_start_time = time.time()
            
            while queue:
                url, depth = queue.popleft()
                
                # Crawl the page
                page_data = self.crawl_page(url, depth)
                
                if page_data:
                    # If not at max depth, add links to queue
                    if depth < self.max_depth:
                        internal_links = [link for link in page_data.links 
                                        if not link.is_external and self.should_crawl(link.url, base_domain)]
                        
                        # Limit links per page to avoid too many requests
                        for link in internal_links[:self.max_pages_per_level]:
                            if link.url not in self.visited_urls:
                                queue.append((link.url, depth + 1))
                                time.sleep(Config.CRAWL_DELAY)
                
                # Stop if we've crawled enough pages
                if len(self.crawl_data) >= Config.MAX_TOTAL_PAGES:
                    break
            
            crawl_end_time = time.time()
            
            return {
                'start_url': start_url,
                'base_domain': base_domain,
                'crawl_data': self.crawl_data,
                'crawl_start_time': crawl_start_time,
                'crawl_end_time': crawl_end_time,
                'total_pages_crawled': len(self.crawl_data)
            }
            
        except Exception as e:
            return {'error': f'Crawling failed: {str(e)}'}
        finally:
            if self.driver:
                self.driver.quit()