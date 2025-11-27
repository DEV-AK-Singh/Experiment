# config.py
import os
from datetime import datetime

class Config:
    """Configuration settings for the web crawler"""
    
    # Crawler settings
    MAX_DEPTH = 3
    MAX_PAGES_PER_LEVEL = 10
    MAX_TOTAL_PAGES = 50
    PAGE_LOAD_TIMEOUT = 10
    CRAWL_DELAY = 1
    
    # Browser settings
    BROWSER_HEADLESS = True
    BROWSER_WINDOW_SIZE = "1920,1080"
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    
    # File paths
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
    REPORTS_DIR = os.path.join(OUTPUT_DIR, "reports")
    EXPORTS_DIR = os.path.join(OUTPUT_DIR, "exports")
    LOGS_DIR = os.path.join(BASE_DIR, "logs")
    
    # Ensure directories exist
    @classmethod
    def create_directories(cls):
        """Create necessary directories"""
        directories = [cls.OUTPUT_DIR, cls.REPORTS_DIR, cls.EXPORTS_DIR, cls.LOGS_DIR]
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    @classmethod
    def get_report_filename(cls, domain):
        """Generate report filename"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"crawl_report_{domain}_{timestamp}.json"
    
    @classmethod
    def get_export_filename(cls, domain):
        """Generate export filename"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"crawl_export_{domain}_{timestamp}.json"

# Initialize directories
Config.create_directories()