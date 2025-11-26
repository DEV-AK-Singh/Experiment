# deep_web_crawler.py
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import json
import os
from urllib.parse import urljoin, urlparse
from collections import deque
import hashlib

class DeepWebCrawler:
    def __init__(self, max_depth=3, max_pages_per_level=10):
        self.max_depth = max_depth
        self.max_pages_per_level = max_pages_per_level
        self.visited_urls = set()
        self.crawl_data = {}
        self.driver = None
        
    def setup_driver(self):
        """Setup Chrome driver"""
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless=new")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            
            self.driver = webdriver.Chrome(options=chrome_options)
            return True
        except Exception as e:
            print(f"❌ ChromeDriver error: {e}")
            return False
    
    def get_domain(self, url):
        """Extract domain from URL"""
        return urlparse(url).netloc
    
    def is_same_domain(self, url1, url2):
        """Check if two URLs belong to the same domain"""
        return self.get_domain(url1) == self.get_domain(url2)
    
    def normalize_url(self, url, base_url):
        """Convert relative URL to absolute"""
        return urljoin(base_url, url)
    
    def should_crawl(self, url, base_domain):
        """Check if URL should be crawled"""
        if url in self.visited_urls:
            return False
        
        if not url.startswith(('http://', 'https://')):
            return False
            
        # Skip non-web resources
        if any(ext in url.lower() for ext in ['.pdf', '.jpg', '.png', '.gif', '.zip', '.exe']):
            return False
            
        # Only crawl same domain (optional: remove this to crawl external links)
        return self.get_domain(url) == base_domain
    
    def extract_comprehensive_data(self, url, soup):
        """Extract comprehensive data from page"""
        try:
            # Basic info
            title = soup.find('title')
            title_text = title.get_text().strip() if title else "No Title"
            
            # Remove scripts and styles
            for element in soup(["script", "style", "nav", "footer", "header"]):
                element.decompose()
            
            # Text content analysis
            text_content = self.extract_text_content(soup)
            
            # Links
            links = self.extract_links(soup, url)
            
            # Images
            images = self.extract_images(soup, url)
            
            # Tables
            tables = self.extract_tables(soup)
            
            # Forms
            forms = self.extract_forms(soup)
            
            # Headings structure
            headings = self.extract_headings(soup)
            
            # Metadata
            metadata = self.extract_metadata(soup)
            
            return {
                'url': url,
                'title': title_text,
                'text_content': text_content,
                'links_found': len(links),
                'images_found': len(images),
                'tables_found': len(tables),
                'forms_found': len(forms),
                'headings_structure': headings,
                'metadata': metadata,
                'links': links,
                'images': images,
                'tables': tables,
                'forms': forms,
                'timestamp': time.time()
            }
            
        except Exception as e:
            print(f"Error extracting data from {url}: {e}")
            return None
    
    def extract_text_content(self, soup):
        """Extract and categorize text content"""
        text_data = {
            'paragraphs': [],
            'lists': [],
            'bold_text': [],
            'italic_text': [],
            'code_blocks': [],
            'quotes': [],
            'total_word_count': 0
        }
        
        # Paragraphs
        paragraphs = soup.find_all('p')
        for p in paragraphs:
            text = p.get_text().strip()
            if text and len(text) > 10:
                text_data['paragraphs'].append(text)
        
        # Lists
        lists = soup.find_all(['ul', 'ol'])
        for lst in lists:
            items = [li.get_text().strip() for li in lst.find_all('li')]
            if items:
                text_data['lists'].append({
                    'type': lst.name,
                    'items': items
                })
        
        # Bold text
        bold_elements = soup.find_all(['b', 'strong'])
        text_data['bold_text'] = [elem.get_text().strip() for elem in bold_elements if elem.get_text().strip()]
        
        # Italic text
        italic_elements = soup.find_all(['i', 'em'])
        text_data['italic_text'] = [elem.get_text().strip() for elem in italic_elements if elem.get_text().strip()]
        
        # Code blocks
        code_elements = soup.find_all(['code', 'pre'])
        text_data['code_blocks'] = [elem.get_text().strip() for elem in code_elements if elem.get_text().strip()]
        
        # Quotes
        quotes = soup.find_all('blockquote')
        text_data['quotes'] = [quote.get_text().strip() for quote in quotes if quote.get_text().strip()]
        
        # Total word count
        all_text = ' '.join(text_data['paragraphs'])
        text_data['total_word_count'] = len(all_text.split())
        
        return text_data
    
    def extract_links(self, soup, base_url):
        """Extract all links with context"""
        links = []
        for a in soup.find_all('a', href=True):
            try:
                text = a.get_text().strip()
                href = a['href']
                
                if href and not href.startswith(('javascript:', 'mailto:', 'tel:')):
                    full_url = self.normalize_url(href, base_url)
                    
                    if full_url.startswith('http'):
                        link_data = {
                            'text': text[:200],
                            'url': full_url,
                            'title': a.get('title', ''),
                            'is_external': self.get_domain(full_url) != self.get_domain(base_url),
                            'element_id': a.get('id', ''),
                            'css_class': a.get('class', [])
                        }
                        links.append(link_data)
            except:
                continue
        
        return links
    
    def extract_images(self, soup, base_url):
        """Extract all images with details"""
        images = []
        for img in soup.find_all('img', src=True):
            try:
                src = img.get('src')
                if src:
                    full_src = self.normalize_url(src, base_url)
                    image_data = {
                        'src': full_src,
                        'alt': img.get('alt', 'No alt text'),
                        'title': img.get('title', ''),
                        'width': img.get('width', ''),
                        'height': img.get('height', ''),
                        'loading': img.get('loading', ''),
                        'css_class': img.get('class', [])
                    }
                    images.append(image_data)
            except:
                continue
        
        return images
    
    def extract_tables(self, soup):
        """Extract table data"""
        tables = []
        for table in soup.find_all('table'):
            try:
                table_data = {
                    'headers': [],
                    'rows': [],
                    'caption': table.find('caption').get_text().strip() if table.find('caption') else ''
                }
                
                # Extract headers
                headers = table.find_all('th')
                table_data['headers'] = [header.get_text().strip() for header in headers]
                
                # Extract rows
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    row_data = [cell.get_text().strip() for cell in cells]
                    if row_data:
                        table_data['rows'].append(row_data)
                
                tables.append(table_data)
            except:
                continue
        
        return tables
    
    def extract_forms(self, soup):
        """Extract form data"""
        forms = []
        for form in soup.find_all('form'):
            try:
                form_data = {
                    'action': form.get('action', ''),
                    'method': form.get('method', 'get'),
                    'inputs': []
                }
                
                # Extract form inputs
                inputs = form.find_all(['input', 'textarea', 'select'])
                for inp in inputs:
                    input_data = {
                        'type': inp.get('type', inp.name),
                        'name': inp.get('name', ''),
                        'placeholder': inp.get('placeholder', ''),
                        'value': inp.get('value', ''),
                        'required': inp.get('required') is not None
                    }
                    form_data['inputs'].append(input_data)
                
                forms.append(form_data)
            except:
                continue
        
        return forms
    
    def extract_headings(self, soup):
        """Extract heading structure"""
        headings = {}
        for i in range(1, 7):
            h_tags = soup.find_all(f'h{i}')
            headings[f'h{i}'] = [h.get_text().strip() for h in h_tags if h.get_text().strip()]
        return headings
    
    def extract_metadata(self, soup):
        """Extract meta tags"""
        metadata = {}
        meta_tags = soup.find_all('meta')
        for meta in meta_tags:
            name = meta.get('name') or meta.get('property')
            content = meta.get('content', '')
            if name and content:
                metadata[name] = content
        return metadata
    
    def crawl_page(self, url, depth):
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
                # Wait for page to load
                time.sleep(3)
                
                # Get page source and parse with BeautifulSoup
                page_source = self.driver.page_source
                soup = BeautifulSoup(page_source, 'html.parser')
                
                # Extract comprehensive data
                page_data = self.extract_comprehensive_data(url, soup)
                
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
    
    def deep_crawl(self, start_url):
        """Perform deep crawling starting from URL"""
        if not self.setup_driver():
            return {'error': 'Failed to initialize browser'}
        
        try:
            base_domain = self.get_domain(start_url)
            queue = deque([(start_url, 0)])  # (url, depth)
            results = {
                'start_url': start_url,
                'base_domain': base_domain,
                'max_depth': self.max_depth,
                'total_pages_crawled': 0,
                'crawl_start_time': time.time(),
                'pages': {}
            }
            
            while queue:
                url, depth = queue.popleft()
                
                # Crawl the page
                page_data = self.crawl_page(url, depth)
                
                if page_data:
                    results['total_pages_crawled'] += 1
                    page_key = hashlib.md5(url.encode()).hexdigest()[:10]
                    results['pages'][page_key] = page_data
                    
                    # If not at max depth, add links to queue
                    if depth < self.max_depth:
                        internal_links = [link for link in page_data['links'] 
                                        if not link['is_external'] and self.should_crawl(link['url'], base_domain)]
                        
                        # Limit links per page to avoid too many requests
                        for link in internal_links[:self.max_pages_per_level]:
                            if link['url'] not in self.visited_urls:
                                queue.append((link['url'], depth + 1))
                
                # Stop if we've crawled enough pages
                if results['total_pages_crawled'] >= 50:  # Safety limit
                    break
            
            results['crawl_end_time'] = time.time()
            results['crawl_duration'] = results['crawl_end_time'] - results['crawl_start_time']
            
            return results
            
        finally:
            if self.driver:
                self.driver.quit()
    
    def generate_report(self, crawl_results):
        """Generate comprehensive report"""
        if 'error' in crawl_results:
            return crawl_results
        
        # Calculate statistics
        total_pages = crawl_results['total_pages_crawled']
        total_links = sum(len(page['links']) for page in crawl_results['pages'].values())
        total_images = sum(len(page['images']) for page in crawl_results['pages'].values())
        total_tables = sum(len(page['tables']) for page in crawl_results['pages'].values())
        total_words = sum(page['text_content']['total_word_count'] for page in crawl_results['pages'].values())
        
        # Generate report
        report = {
            'crawl_summary': {
                'start_url': crawl_results['start_url'],
                'base_domain': crawl_results['base_domain'],
                'total_pages_crawled': total_pages,
                'max_depth_reached': self.max_depth,
                'crawl_duration_seconds': round(crawl_results['crawl_duration'], 2),
                'total_links_found': total_links,
                'total_images_found': total_images,
                'total_tables_found': total_tables,
                'total_words_extracted': total_words
            },
            'pages_by_depth': self.organize_pages_by_depth(crawl_results),
            'site_structure': self.analyze_site_structure(crawl_results),
            'content_analysis': self.analyze_content(crawl_results),
            'detailed_pages': crawl_results['pages']
        }
        
        return report
    
    def organize_pages_by_depth(self, crawl_results):
        """Organize pages by their crawl depth"""
        # This would require tracking depth for each page
        # For simplicity, we'll just return the pages
        return list(crawl_results['pages'].keys())
    
    def analyze_site_structure(self, crawl_results):
        """Analyze the overall site structure"""
        pages = crawl_results['pages']
        
        structure = {
            'most_linked_pages': self.find_most_linked_pages(pages),
            'page_titles': [page['title'] for page in pages.values()],
            'unique_domains_linked': self.find_unique_domains(pages)
        }
        
        return structure
    
    def analyze_content(self, crawl_results):
        """Analyze content across all pages"""
        pages = crawl_results['pages']
        
        content_analysis = {
            'total_content_volume': {
                'words': sum(page['text_content']['total_word_count'] for page in pages.values()),
                'paragraphs': sum(len(page['text_content']['paragraphs']) for page in pages.values()),
                'images': sum(len(page['images']) for page in pages.values()),
                'tables': sum(len(page['tables']) for page in pages.values())
            },
            'content_types_present': self.identify_content_types(pages),
            'common_keywords': self.extract_common_keywords(pages)
        }
        
        return content_analysis
    
    def find_most_linked_pages(self, pages):
        """Find pages with most internal links"""
        link_counts = {}
        for page in pages.values():
            for link in page['links']:
                if not link['is_external']:
                    link_counts[link['url']] = link_counts.get(link['url'], 0) + 1
        
        return sorted(link_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    
    def find_unique_domains(self, pages):
        """Find unique external domains linked"""
        domains = set()
        for page in pages.values():
            for link in page['links']:
                if link['is_external']:
                    domains.add(self.get_domain(link['url']))
        return list(domains)
    
    def identify_content_types(self, pages):
        """Identify types of content present"""
        content_types = set()
        for page in pages.values():
            if page['tables_found'] > 0:
                content_types.add('tables')
            if page['images_found'] > 0:
                content_types.add('images')
            if page['forms_found'] > 0:
                content_types.add('forms')
            if any(page['text_content'][key] for key in ['code_blocks', 'bold_text', 'italic_text']):
                content_types.add('formatted_text')
        
        return list(content_types)
    
    def extract_common_keywords(self, pages, top_n=20):
        """Extract common keywords from all content"""
        from collections import Counter
        import re
        
        all_text = ''
        for page in pages.values():
            all_text += ' '.join(page['text_content']['paragraphs']) + ' '
        
        # Simple word frequency analysis
        words = re.findall(r'\b\w{4,}\b', all_text.lower())
        word_freq = Counter(words)
        
        return word_freq.most_common(top_n)

# Flask Web Interface
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Deep Web Crawler</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }
        input[type="text"] { width: 70%; padding: 12px; font-size: 16px; border: 2px solid #ddd; border-radius: 5px; }
        button { padding: 12px 30px; font-size: 16px; background: #3498db; color: white; border: none; border-radius: 5px; cursor: pointer; margin-left: 10px; }
        button:hover { background: #2980b9; }
        .loading { display: none; background: #fff3cd; padding: 20px; border-radius: 5px; margin: 20px 0; }
        .result { margin-top: 30px; }
        .summary-card { background: #e8f4fd; padding: 20px; border-radius: 5px; margin: 15px 0; }
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0; }
        .stat-card { background: white; padding: 15px; border-radius: 5px; text-align: center; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        .page-item { background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #3498db; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🌐 Deep Web Crawler (3 Levels)</h1>
        <p>Enter a website URL to crawl up to 3 levels deep and generate a comprehensive report.</p>
        
        <form onsubmit="startCrawl(); return false;">
            <input type="text" id="urlInput" placeholder="https://example.com" value="https://react.dev">
            <button type="submit">Start Deep Crawl</button>
        </form>
        
        <div id="loading" class="loading">
            <h3>🔄 Crawling Website...</h3>
            <p>This may take 2-5 minutes as we're crawling multiple levels deep.</p>
            <p>Currently crawling: <span id="currentUrl">Initializing...</span></p>
            <p>Pages crawled: <span id="pagesCrawled">0</span></p>
        </div>
        
        <div id="result"></div>
    </div>

    <script>
        async function startCrawl() {
            const url = document.getElementById('urlInput').value.trim();
            const loading = document.getElementById('loading');
            const resultDiv = document.getElementById('result');
            
            if (!url) {
                alert('Please enter a URL');
                return;
            }
            
            loading.style.display = 'block';
            resultDiv.innerHTML = '';
            
            try {
                const response = await fetch('/deep-crawl', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({url: url, max_depth: 3})
                });
                
                const data = await response.json();
                loading.style.display = 'none';
                
                if (data.success) {
                    displayReport(data.report);
                } else {
                    resultDiv.innerHTML = `
                        <div style="background: #f8d7da; color: #721c24; padding: 20px; border-radius: 5px;">
                            <h3>❌ Error</h3>
                            <p>${data.error}</p>
                        </div>
                    `;
                }
            } catch (error) {
                loading.style.display = 'none';
                resultDiv.innerHTML = `
                    <div style="background: #f8d7da; color: #721c24; padding: 20px; border-radius: 5px;">
                        <h3>❌ Network Error</h3>
                        <p>${error.message}</p>
                    </div>
                `;
            }
        }
        
        function displayReport(report) {
            const summary = report.crawl_summary;
            const pages = report.detailed_pages;
            
            let html = `
                <div class="summary-card">
                    <h2>📊 Crawl Summary</h2>
                    <div class="stats-grid">
                        <div class="stat-card">
                            <h3>${summary.total_pages_crawled}</h3>
                            <p>Pages Crawled</p>
                        </div>
                        <div class="stat-card">
                            <h3>${summary.total_links_found}</h3>
                            <p>Total Links</p>
                        </div>
                        <div class="stat-card">
                            <h3>${summary.total_images_found}</h3>
                            <p>Images Found</p>
                        </div>
                        <div class="stat-card">
                            <h3>${summary.total_tables_found}</h3>
                            <p>Tables Found</p>
                        </div>
                        <div class="stat-card">
                            <h3>${summary.total_words_extracted}</h3>
                            <p>Words Extracted</p>
                        </div>
                        <div class="stat-card">
                            <h3>${summary.crawl_duration_seconds}s</h3>
                            <p>Crawl Time</p>
                        </div>
                    </div>
                </div>
                
                <h2>📄 Pages Crawled</h2>
            `;
            
            Object.keys(pages).forEach(pageKey => {
                const page = pages[pageKey];
                html += `
                    <div class="page-item">
                        <h3><a href="${page.url}" target="_blank">${page.title}</a></h3>
                        <p><strong>URL:</strong> ${page.url}</p>
                        <p><strong>Stats:</strong> ${page.links_found} links, ${page.images_found} images, ${page.tables_found} tables, ${page.text_content.total_word_count} words</p>
                        <details>
                            <summary>View Details</summary>
                            <div style="margin-top: 10px;">
                                <h4>Content Preview:</h4>
                                <textarea style="width: 100%; height: 100px; font-size: 12px;" readonly>${page.text_content.paragraphs.slice(0, 3).join('\\n\\n')}</textarea>
                                
                                <h4>Links (${page.links.length}):</h4>
                                <ul>
                                    ${page.links.slice(0, 5).map(link => 
                                        `<li>${link.text} -> ${link.url}</li>`
                                    ).join('')}
                                </ul>
                                
                                ${page.links.length > 5 ? `<p>... and ${page.links.length - 5} more links</p>` : ''}
                            </div>
                        </details>
                    </div>
                `;
            });
            
            // Add download button
            html += `
                <div style="margin-top: 20px;">
                    <button onclick="downloadReport()" style="background: #27ae60;">📥 Download Full Report (JSON)</button>
                </div>
                <script>
                    function downloadReport() {
                        const report = ${JSON.stringify(report)};
                        const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(report, null, 2));
                        const downloadAnchor = document.createElement('a');
                        downloadAnchor.setAttribute("href", dataStr);
                        downloadAnchor.setAttribute("download", "deep_crawl_report.json");
                        document.body.appendChild(downloadAnchor);
                        downloadAnchor.click();
                        downloadAnchor.remove();
                    }
               <\/script>
            `;
            
            document.getElementById('result').innerHTML = html;
        }
    </script>
</body>
</html>
'''

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/deep-crawl', methods=['POST'])
def deep_crawl():
    data = request.get_json()
    url = data.get('url', '').strip()
    max_depth = data.get('max_depth', 3)
    
    if not url:
        return jsonify({'error': 'No URL provided'})
    
    print(f"🚀 Starting deep crawl: {url} (max depth: {max_depth})")
    
    crawler = DeepWebCrawler(max_depth=max_depth)
    crawl_results = crawler.deep_crawl(url)
    
    if 'error' in crawl_results:
        return jsonify({'success': False, 'error': crawl_results['error']})
    
    # Generate comprehensive report
    report = crawler.generate_report(crawl_results)
    
    return jsonify({
        'success': True,
        'report': report
    })

if __name__ == '__main__':
    print("🚀 Starting Deep Web Crawler...")
    print("💡 This crawler will go up to 3 levels deep into websites")
    app.run(debug=True, host='0.0.0.0', port=5000)