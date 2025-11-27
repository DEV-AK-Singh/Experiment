import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re

class SimpleScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
    
    def is_valid_url(self, url):
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False
    
    def normalize_url(self, url):
        if not url.startswith(('http://', 'https://')):
            return 'https://' + url
        return url
    
    def scrape_url(self, url):
        """Simple URL scraping"""
        try:
            print(f"Scraping: {url}")
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove scripts and styles
            for element in soup(["script", "style"]):
                element.decompose()
            
            # Get title
            title = soup.find('title')
            title_text = title.get_text().strip() if title else "No title"
            
            # Get all text
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            # Get all links
            links = []
            for a in soup.find_all('a', href=True):
                link_text = a.get_text().strip()
                href = a['href']
                if href and not href.startswith(('javascript:', 'mailto:', 'tel:')):
                    full_url = urljoin(url, href)
                    if self.is_valid_url(full_url):
                        links.append({
                            'text': link_text,
                            'url': full_url
                        })
            
            # Get images
            images = []
            for img in soup.find_all('img', src=True):
                src = img.get('src')
                if src:
                    full_src = urljoin(url, src)
                    images.append({
                        'src': full_src,
                        'alt': img.get('alt', '')
                    })
            
            return {
                'url': url,
                'title': title_text,
                'text': text[:5000],  # Limit text
                'links': links[:50],   # Limit links
                'images': images[:20]  # Limit images
            }
            
        except Exception as e:
            return {
                'error': f"Failed to scrape: {str(e)}",
                'url': url
            }
    
    def search_and_scrape(self, query):
        """Search and scrape first result"""
        try:
            print(f"Searching for: {query}")
            search_url = f"https://html.duckduckgo.com/html/?q={requests.utils.quote(query)}"
            response = self.session.get(search_url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Get first result
            first_result = soup.find('div', class_='result')
            if first_result:
                title_elem = first_result.find('a', class_='result__a')
                if title_elem:
                    link = title_elem.get('href', '')
                    # Extract actual URL from DuckDuckGo redirect
                    if '//duckduckgo.com/l/' in link:
                        match = re.search(r'uddg=([^&]+)', link)
                        if match:
                            link = requests.utils.unquote(match.group(1))
                    
                    if self.is_valid_url(link):
                        return self.scrape_url(link)
            
            return {'error': 'No results found'}
            
        except Exception as e:
            return {'error': f"Search failed: {str(e)}"}

# Simple usage
if __name__ == "__main__":
    scraper = SimpleScraper()
    
    while True:
        user_input = input("\nEnter URL or search query (or 'quit' to exit): ").strip()
        
        if user_input.lower() == 'quit':
            break
            
        if not user_input:
            continue
        
        # Check if it's a URL
        if user_input.startswith(('http://', 'https://', 'www.')):
            result = scraper.scrape_url(scraper.normalize_url(user_input))
        else:
            result = scraper.search_and_scrape(user_input)
        
        # Print results
        print("\n" + "="*50)
        if 'error' in result:
            print(f"❌ ERROR: {result['error']}")
        else:
            print(f"📄 TITLE: {result['title']}")
            print(f"🌐 URL: {result['url']}")
            print(f"\n📝 TEXT ({len(result['text'])} chars):")
            print(result['text'][:500] + "..." if len(result['text']) > 500 else result['text'])
            
            print(f"\n🔗 LINKS ({len(result['links'])}):")
            for i, link in enumerate(result['links'][:10], 1):
                print(f"  {i}. {link['text'][:50]}... -> {link['url']}")
            
            print(f"\n🖼️ IMAGES ({len(result['images'])}):")
            for i, img in enumerate(result['images'][:5], 1):
                print(f"  {i}. {img['alt'][:50]}... -> {img['src']}")
        
        print("="*50)