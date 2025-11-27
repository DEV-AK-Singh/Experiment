# src/crawler/data_extractor.py
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import List, Dict, Any
from ..models.data_models import *

class DataExtractor:
    """Handles data extraction from web pages"""
    
    @staticmethod
    def extract_comprehensive_data(url: str, soup: BeautifulSoup) -> PageData:
        """Extract comprehensive data from page"""
        # Basic info
        title = soup.find('title')
        title_text = title.get_text().strip() if title else "No Title"
        
        # Remove unwanted elements
        for element in soup(["script", "style", "nav", "footer", "header"]):
            element.decompose()
        
        # Extract various data types
        text_content = DataExtractor.extract_text_content(soup)
        links = DataExtractor.extract_links(soup, url)
        images = DataExtractor.extract_images(soup, url)
        tables = DataExtractor.extract_tables(soup)
        forms = DataExtractor.extract_forms(soup)
        headings = DataExtractor.extract_headings(soup)
        metadata = DataExtractor.extract_metadata(soup)
        
        return PageData(
            url=url,
            title=title_text,
            text_content=text_content,
            links=links,
            images=images,
            tables=tables,
            forms=forms,
            headings_structure=headings,
            metadata=metadata,
            links_found=len(links),
            images_found=len(images),
            tables_found=len(tables),
            forms_found=len(forms),
            timestamp=time.time()
        )
    
    @staticmethod
    def extract_text_content(soup: BeautifulSoup) -> TextContent:
        """Extract and categorize text content"""
        paragraphs = []
        lists_data = []
        bold_text = []
        italic_text = []
        code_blocks = []
        quotes = []
        
        # Paragraphs
        for p in soup.find_all('p'):
            text = p.get_text().strip()
            if text and len(text) > 10:
                paragraphs.append(text)
        
        # Lists
        for lst in soup.find_all(['ul', 'ol']):
            items = [li.get_text().strip() for li in lst.find_all('li')]
            if items:
                lists_data.append({
                    'type': lst.name,
                    'items': items
                })
        
        # Bold text
        for elem in soup.find_all(['b', 'strong']):
            text = elem.get_text().strip()
            if text:
                bold_text.append(text)
        
        # Italic text
        for elem in soup.find_all(['i', 'em']):
            text = elem.get_text().strip()
            if text:
                italic_text.append(text)
        
        # Code blocks
        for elem in soup.find_all(['code', 'pre']):
            text = elem.get_text().strip()
            if text:
                code_blocks.append(text)
        
        # Quotes
        for quote in soup.find_all('blockquote'):
            text = quote.get_text().strip()
            if text:
                quotes.append(text)
        
        # Total word count
        all_text = ' '.join(paragraphs)
        total_word_count = len(all_text.split())
        
        return TextContent(
            paragraphs=paragraphs,
            lists=lists_data,
            bold_text=bold_text,
            italic_text=italic_text,
            code_blocks=code_blocks,
            quotes=quotes,
            total_word_count=total_word_count
        )
    
    @staticmethod
    def extract_links(soup: BeautifulSoup, base_url: str) -> List[LinkData]:
        """Extract all links with context"""
        links = []
        base_domain = urlparse(base_url).netloc
        
        for a in soup.find_all('a', href=True):
            try:
                text = a.get_text().strip()
                href = str(a['href'])
                
                if href and not href.startswith(('javascript:', 'mailto:', 'tel:')):
                    full_url = urljoin(base_url, href)
                    
                    if full_url.startswith('http'):
                        is_external = urlparse(full_url).netloc != base_domain 
                        link_data = LinkData(
                            text=text[:200],
                            url=full_url,
                            title=str(a.get('title', '')),
                            is_external=is_external,
                            element_id=str(a.get('id', '')),
                            css_class=str(a.get('class', '')).split()
                        )
                        links.append(link_data)
            except Exception:
                continue
        
        return links
    
    @staticmethod
    def extract_images(soup: BeautifulSoup, base_url: str) -> List[ImageData]:
        """Extract all images with details"""
        images = []
        
        for img in soup.find_all('img', src=True):
            try:
                src = str(img.get('src'))
                if src:
                    full_src = urljoin(base_url, src)
                    
                    image_data = ImageData(
                        src=full_src,
                        alt=str(img.get('alt', 'No alt text')),
                        title=str(img.get('title', '')),
                        width=str(img.get('width', '')),
                        height=str(img.get('height', '')),
                        loading=str(img.get('loading', '')),
                        css_class=str(img.get('class', '')).split()
                    )
                    images.append(image_data)
            except Exception:
                continue
        
        return images
    
    @staticmethod
    def extract_tables(soup: BeautifulSoup) -> List[TableData]:
        """Extract table data"""
        tables = []
        
        for table in soup.find_all('table'):
            try:
                headers = []
                rows = []
                caption = table.find('caption')
                caption_text = caption.get_text().strip() if caption else ''
                
                # Extract headers
                for header in table.find_all('th'):
                    headers.append(header.get_text().strip())
                
                # Extract rows
                for row in table.find_all('tr'):
                    cells = row.find_all(['td', 'th'])
                    row_data = [cell.get_text().strip() for cell in cells]
                    if row_data:
                        rows.append(row_data)
                
                table_data = TableData(
                    headers=headers,
                    rows=rows,
                    caption=caption_text
                )
                tables.append(table_data)
            except Exception:
                continue
        
        return tables
    
    @staticmethod
    def extract_forms(soup: BeautifulSoup) -> List[FormData]:
        """Extract form data"""
        forms = []
        
        for form in soup.find_all('form'):
            try:
                inputs_data = []
                
                # Extract form inputs
                for inp in form.find_all(['input', 'textarea', 'select']):
                    input_data = {
                        'type': inp.get('type', inp.name),
                        'name': inp.get('name', ''),
                        'placeholder': inp.get('placeholder', ''),
                        'value': inp.get('value', ''),
                        'required': inp.get('required') is not None
                    }
                    inputs_data.append(input_data)
                
                form_data = FormData(
                    action=str(form.get('action', '')),
                    method=str(form.get('method', 'get')),
                    inputs=inputs_data
                )
                forms.append(form_data)
            except Exception:
                continue
        
        return forms
    
    @staticmethod
    def extract_headings(soup: BeautifulSoup) -> Dict[str, List[str]]:
        """Extract heading structure"""
        headings = {}
        for i in range(1, 7):
            h_tags = soup.find_all(f'h{i}')
            headings[f'h{i}'] = [h.get_text().strip() for h in h_tags if h.get_text().strip()]
        return headings
    
    @staticmethod
    def extract_metadata(soup: BeautifulSoup) -> Dict[str, str]:
        """Extract meta tags"""
        metadata = {}
        for meta in soup.find_all('meta'):
            name = meta.get('name') or meta.get('property')
            content = meta.get('content', '')
            if name and content:
                metadata[name] = content
        return metadata