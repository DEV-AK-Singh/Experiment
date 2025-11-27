# src/utils/report_generator.py
from typing import Dict, Any, List
from collections import Counter
import re
from urllib.parse import urlparse

from ..models.data_models import *

class ReportGenerator:
    """Generates comprehensive reports from crawl data"""
    
    @staticmethod
    def generate_report(crawl_results: Dict[str, Any]) -> CrawlReport:
        """Generate comprehensive report from crawl results"""
        if 'error' in crawl_results:
            return CrawlReport(
                content_analysis={},
                crawl_summary=CrawlSummary(
                    start_url='',
                    base_domain='',
                    total_pages_crawled=0,
                    max_depth_reached=0,
                    crawl_duration_seconds=0,
                    total_links_found=0,
                    total_images_found=0,
                    total_tables_found=0,
                    total_words_extracted=0,
                    crawl_start_time=0,
                    crawl_end_time=0
                ),
                pages_by_depth=[],
                site_structure={},
                detailed_pages={}
            )
        
        crawl_data = crawl_results['crawl_data']
        
        # Calculate statistics
        total_links = sum(len(page.links) for page in crawl_data.values())
        total_images = sum(len(page.images) for page in crawl_data.values())
        total_tables = sum(len(page.tables) for page in crawl_data.values())
        total_words = sum(page.text_content.total_word_count for page in crawl_data.values())
        
        # Create crawl summary
        summary = CrawlSummary(
            start_url=crawl_results['start_url'],
            base_domain=crawl_results['base_domain'],
            total_pages_crawled=crawl_results['total_pages_crawled'],
            max_depth_reached=3,  # Assuming max depth from config
            crawl_duration_seconds=round(crawl_results['crawl_end_time'] - crawl_results['crawl_start_time'], 2),
            total_links_found=total_links,
            total_images_found=total_images,
            total_tables_found=total_tables,
            total_words_extracted=total_words,
            crawl_start_time=crawl_results['crawl_start_time'],
            crawl_end_time=crawl_results['crawl_end_time']
        )
        
        # Generate report sections
        pages_by_depth = list(crawl_data.keys())  # Simplified - would need depth tracking
        site_structure = ReportGenerator.analyze_site_structure(crawl_data)
        content_analysis = ReportGenerator.analyze_content(crawl_data)
        
        return CrawlReport(
            crawl_summary=summary,
            pages_by_depth=pages_by_depth,
            site_structure=site_structure,
            content_analysis=content_analysis,
            detailed_pages=crawl_data
        )
    
    @staticmethod
    def analyze_site_structure(pages: Dict[str, PageData]) -> Dict[str, Any]:
        """Analyze the overall site structure"""
        most_linked_pages = ReportGenerator.find_most_linked_pages(pages)
        unique_domains = ReportGenerator.find_unique_domains(pages)
        
        return {
            'most_linked_pages': most_linked_pages,
            'page_titles': [page.title for page in pages.values()],
            'unique_domains_linked': unique_domains
        }
    
    @staticmethod
    def analyze_content(pages: Dict[str, PageData]) -> Dict[str, Any]:
        """Analyze content across all pages"""
        content_analysis = {
            'total_content_volume': {
                'words': sum(page.text_content.total_word_count for page in pages.values()),
                'paragraphs': sum(len(page.text_content.paragraphs) for page in pages.values()),
                'images': sum(len(page.images) for page in pages.values()),
                'tables': sum(len(page.tables) for page in pages.values())
            },
            'content_types_present': ReportGenerator.identify_content_types(pages),
            'common_keywords': ReportGenerator.extract_common_keywords(pages)
        }
        
        return content_analysis
    
    @staticmethod
    def find_most_linked_pages(pages: Dict[str, PageData]) -> List[tuple]:
        """Find pages with most internal links"""
        link_counts = {}
        for page in pages.values():
            for link in page.links:
                if not link.is_external:
                    link_counts[link.url] = link_counts.get(link.url, 0) + 1
        
        return sorted(link_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    
    @staticmethod
    def find_unique_domains(pages: Dict[str, PageData]) -> List[str]:
        """Find unique external domains linked"""
        domains = set()
        for page in pages.values():
            for link in page.links:
                if link.is_external:
                    domains.add(urlparse(link.url).netloc)
        return list(domains)
    
    @staticmethod
    def identify_content_types(pages: Dict[str, PageData]) -> List[str]:
        """Identify types of content present"""
        content_types = set()
        for page in pages.values():
            if page.tables_found > 0:
                content_types.add('tables')
            if page.images_found > 0:
                content_types.add('images')
            if page.forms_found > 0:
                content_types.add('forms')
            if any([page.text_content.code_blocks, page.text_content.bold_text, page.text_content.italic_text]):
                content_types.add('formatted_text')
        
        return list(content_types)
    
    @staticmethod
    def extract_common_keywords(pages: Dict[str, PageData], top_n: int = 20) -> List[tuple]:
        """Extract common keywords from all content"""
        all_text = ''
        for page in pages.values():
            all_text += ' '.join(page.text_content.paragraphs) + ' '
        
        # Simple word frequency analysis
        words = re.findall(r'\b\w{4,}\b', all_text.lower())
        word_freq = Counter(words)
        
        return word_freq.most_common(top_n)