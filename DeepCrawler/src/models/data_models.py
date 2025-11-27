# src/models/data_models.py
from dataclasses import dataclass, asdict
from typing import List, Dict, Any
import time

@dataclass
class LinkData:
    """Data model for extracted links"""
    text: str
    url: str
    title: str
    is_external: bool
    element_id: str
    css_class: List[str]
    
    def to_dict(self):
        return asdict(self)

@dataclass
class ImageData:
    """Data model for extracted images"""
    src: str
    alt: str
    title: str
    width: str
    height: str
    loading: str
    css_class: List[str]
    
    def to_dict(self):
        return asdict(self)

@dataclass
class TableData:
    """Data model for extracted tables"""
    headers: List[str]
    rows: List[List[str]]
    caption: str
    
    def to_dict(self):
        return asdict(self)

@dataclass
class FormData:
    """Data model for extracted forms"""
    action: str
    method: str
    inputs: List[Dict[str, Any]]
    
    def to_dict(self):
        return asdict(self)

@dataclass
class TextContent:
    """Data model for text content"""
    paragraphs: List[str]
    lists: List[Dict[str, Any]]
    bold_text: List[str]
    italic_text: List[str]
    code_blocks: List[str]
    quotes: List[str]
    total_word_count: int
    
    def to_dict(self):
        return asdict(self)

@dataclass
class PageData:
    """Data model for complete page data"""
    url: str
    title: str
    text_content: TextContent
    links: List[LinkData]
    images: List[ImageData]
    tables: List[TableData]
    forms: List[FormData]
    headings_structure: Dict[str, List[str]]
    metadata: Dict[str, str]
    links_found: int
    images_found: int
    tables_found: int
    forms_found: int
    timestamp: float
    
    def to_dict(self):
        data = asdict(self)
        # Convert nested objects
        data['text_content'] = self.text_content.to_dict()
        data['links'] = [link.to_dict() for link in self.links]
        data['images'] = [image.to_dict() for image in self.images]
        data['tables'] = [table.to_dict() for table in self.tables]
        data['forms'] = [form.to_dict() for form in self.forms]
        return data

@dataclass
class CrawlSummary:
    """Data model for crawl summary"""
    start_url: str
    base_domain: str
    total_pages_crawled: int
    max_depth_reached: int
    crawl_duration_seconds: float
    total_links_found: int
    total_images_found: int
    total_tables_found: int
    total_words_extracted: int
    crawl_start_time: float
    crawl_end_time: float
    
    def to_dict(self):
        return asdict(self)

@dataclass
class CrawlReport:
    """Data model for complete crawl report"""
    crawl_summary: CrawlSummary
    pages_by_depth: List[str]
    site_structure: Dict[str, Any]
    content_analysis: Dict[str, Any]
    detailed_pages: Dict[str, PageData]
    
    def to_dict(self):
        data = asdict(self)
        data['crawl_summary'] = self.crawl_summary.to_dict()
        data['detailed_pages'] = {k: v.to_dict() for k, v in self.detailed_pages.items()}
        return data