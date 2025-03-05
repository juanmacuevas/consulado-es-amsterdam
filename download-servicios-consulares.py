#!/usr/bin/env python3
import os
import time
import random
import re
import logging
import requests
from bs4 import BeautifulSoup
from markdownify import markdownify
from fake_useragent import UserAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("scraper.log"), logging.StreamHandler()]
)

# Constants
REFERRERS = [
    'https://www.google.com/',
    'https://www.bing.com/',
    'https://www.exteriores.gob.es/'
]

class ConsuladoScraper:
    def __init__(self, delay=2):
        self.session = requests.Session()
        self.base_delay = delay
        
    def get_headers(self):
        """Generate random headers for each request"""
        return {
            'User-Agent': UserAgent().random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Referer': random.choice(REFERRERS),
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
    
    def fetch_page(self, url, retries=2):
        """Fetch a page with retries and random delays"""
        for attempt in range(retries + 1):
            try:
                # Add jitter to delay
                time.sleep(self.base_delay + random.uniform(0.5, 2.0))
                
                headers = self.get_headers()
                logging.info(f"Requesting {url} with User-Agent: {headers['User-Agent']}")
                
                response = self.session.get(url, headers=headers, timeout=30)
                
                if response.status_code == 200:
                    logging.info(f"Success: {len(response.content)} bytes received")
                    return response.content
                    
                elif response.status_code == 404:
                    logging.error(f"Page not found: {url}")
                    return None
                    
                elif attempt < retries:
                    delay = random.uniform(5, 10)
                    logging.warning(f"HTTP {response.status_code}: Retrying in {delay:.1f}s")
                    time.sleep(delay)
                    
            except requests.RequestException as e:
                if attempt < retries:
                    delay = random.uniform(5, 10)
                    logging.warning(f"Request error: {e}. Retrying in {delay:.1f}s")
                    time.sleep(delay)
                else:
                    logging.error(f"Failed to fetch {url}: {e}")
                    
        return None
    
    def extract_content(self, html, url):
        """Extract and clean content from HTML"""
        if not html:
            return "<p>No content could be retrieved</p>"
            
        soup = BeautifulSoup(html, "html.parser")
        parent = BeautifulSoup("<div></div>", "html.parser").div
        
        # Find main content sections
        for section_name, selector in [
            ("main", "div.single__detail-Wrapper"), 
            ("news", "ul.newResults__list"),
            ("travel", "div.main-content-travel-recommendation"),
            ("accordion", "div.section__accordion-wrapper")
        ]:
            elements = soup.select(selector)
            if elements:
                logging.info(f"Found {len(elements)} '{section_name}' elements")
                # For main content, get the last wrapper (most specific content)
                if section_name == "main" and elements:
                    parent.append(elements[-1])
                # For others, just append the first instance
                elif elements:
                    parent.append(elements[0])
        
        # Add default message if no content found
        if not parent.contents:
            info = soup.new_tag('p')
            info.string = 'No se encontró contenido específico en esta página.'
            parent.append(info)
            logging.warning(f"No content found for {url}")
        
        # Add link to original
        link = soup.new_tag('a', href=url)
        link.string = 'Enlace a la página original'
        parent.append(link)
        
        # Clean up content
        self._fix_links(parent)
        self._remove_blank_targets(parent)
        
        return str(parent)
    
    def _fix_links(self, dom):
        """Convert relative links to absolute URLs"""
        for link in dom.find_all("a", href=True):
            if link.get("href").startswith("/"):
                link["href"] = "https://www.exteriores.gob.es" + requests.utils.quote(
                    requests.utils.unquote(link.get("href"))
                )
        return dom
    
    def _remove_blank_targets(self, dom):
        """Remove title attributes and images from blank target links"""
        for link in dom.find_all("a", target="_blank"):
            link.attrs = {k: v for k, v in link.attrs.items() if k != "title"}
            for img in link.find_all("img"):
                img.decompose()
        return dom
    
    def save_markdown(self, content, directory, filename):
        """Save content as markdown file"""
        os.makedirs(directory, exist_ok=True)
        path = os.path.join(directory, f"{filename}.md")
        
        # Apply content-specific fixes
        if filename.startswith("Noticias"):
            content = self._remove_weekdays(content)
        if filename.startswith("Recomendaciones"):
            content = self._fix_recommendations_date(content)
        
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            logging.info(f"Saved: {path}")
            return True
        except Exception as e:
            logging.error(f"Error saving {path}: {e}")
            return False
    
    def _remove_weekdays(self, text):
        """Remove weekday names from text"""
        days = ["lunes", "martes", "mi[eé]rcoles", "jueves", "viernes", "s[aá]bado", "domingo"]
        pattern = re.compile(rf'(?i)({"|".join(days)}),\s', re.MULTILINE)
        return pattern.sub('', text)
    
    def _fix_recommendations_date(self, text):
        """Remove variable dates from recommendations"""
        pattern = re.compile(r"(?i)(Recomendaciones vigentes) a \d{1,2} de [a-zA-Z]+ de \d{4}")
        return pattern.sub(r'\1', text)
    
    def process_page(self, directory, filename, url):
        """Process a single page: fetch, extract, convert, and save"""
        logging.info(f"Processing: {directory}/{filename}")
        
        html = self.fetch_page(url)
        if not html:
            return False
            
        content_html = self.extract_content(html, url)
        markdown = markdownify(content_html)
        
        return self.save_markdown(markdown, directory, filename)
    
    def get_service_pages(self):
        """Get list of service pages from the main services page"""
        url = "https://www.exteriores.gob.es/Consulados/amsterdam/es/ServiciosConsulares/Paginas/index.aspx"
        html = self.fetch_page(url)
        
        if not html:
            return []
            
        soup = BeautifulSoup(html, "html.parser")
        
        results = []
        for select in soup.find_all("select"):
            for option in select.find_all("option"):
                cat = option.get("parentcategory")
                subcat = option.get("value")
                
                if cat and subcat:
                    cat_encoded = requests.utils.quote(cat)
                    subcat_encoded = requests.utils.quote(subcat)
                    url = f"{url}?scco=Pa%C3%ADses+Bajos&scd=9&scca={cat_encoded}&scs={subcat_encoded}"
                    results.append((f"Servicios Consulares/{cat}", subcat, url))
        
        logging.info(f"Found {len(results)} service pages")
        return results
        
    def run(self, pages, test_mode=False):
        """Run the scraper on a list of pages"""
        # Try a test page first
        if pages:
            logging.info(f"Testing with first page: {pages[0][1]}")
            if not self.process_page(*pages[0]):
                logging.error("Test page failed, aborting")
                return False
            
        # Process the rest of the pages
        for i, page in enumerate(pages[1:], 2):
            logging.info(f"Processing page {i}/{len(pages)}")
            self.process_page(*page)
            
        # Get and process service pages
        service_pages = self.get_service_pages()
        if service_pages:
            # In test mode, only process first few
            if test_mode:
                service_pages = service_pages[:5]
                
            for i, page in enumerate(service_pages, 1):
                logging.info(f"Processing service page {i}/{len(service_pages)}")
                self.process_page(*page)
                
        return True


if __name__ == "__main__":
    # List of pages to scrape
    pages = [
        ('Páginas', 'Consul', 'https://www.exteriores.gob.es/Consulados/amsterdam/es/Consulado/Paginas/Consul.aspx'),
        ('Páginas', 'Consulado', 'https://www.exteriores.gob.es/Consulados/amsterdam/es/Consulado/Paginas/Consulado.aspx'),
        # Add the rest of your pages here
    ]
    
    # Create and run the scraper
    scraper = ConsuladoScraper(delay=3)
    logging.info("=== Starting web scraper ===")
    
    # Set test_mode=True to only process a few service pages
    scraper.run(pages, test_mode=True)
    
    logging.info("=== Web scraper completed ===")