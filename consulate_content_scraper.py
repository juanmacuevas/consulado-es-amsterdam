import time
import random
import yaml
import requests
from selenium import webdriver
from fake_useragent import UserAgent
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from markdownify import markdownify as md




# Constants

PAGES_DATA = yaml.safe_load(open('pages_data.yml', 'r'))
PATH_MAP = {'page':'Páginas/'}
SERVICE_INDEX_URL = "service_index_url"  # Replace with actual service index URL


def setup_browser():
    """Setup headless Chrome browser with random user agent."""
    user_agent = UserAgent().random
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument(f"user-agent={user_agent}")
    browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    return browser

def extract_content_from_html(html_content,url):
    soup = BeautifulSoup(html_content, "html.parser")
    parent_div = BeautifulSoup("<div></div>", "html.parser").div

    section_content = soup.find_all("div", class_="single__detail-Wrapper")[-1]
    if section_content:
        parent_div.append(section_content)
    
    news_section = soup.find("ul", class_="newResults__list")
    if news_section:
        parent_div.append(news_section)

    travel = soup.find("div", class_="main-content-travel-recommendation")
    if travel:
        parent_div.append(travel)

    accordeon = soup.find("div", class_="section__accordion-wrapper")
    if accordeon:
        parent_div.append(accordeon)

    # link to original page
    original_link = soup.new_tag('a', href=url)
    original_link.string = 'Enlace a la página original'
    parent_div.append(original_link)

    parent_div = fix_target_bank(parent_div)    
    parent_div = fix_links(parent_div)
    return parent_div



def fix_target_bank(dom):
    for link in dom.find_all("a", target="_blank"):
        link.attrs = {k: v for k, v in link.attrs.items() if k != "title"}
        for img in link.find_all("img"):
            img.decompose()
    return dom 



def fix_links(dom):
    for link in dom.find_all("a", href=True):
        if link.get("href").startswith("/"):
            link["href"] = "https://www.exteriores.gob.es" + requests.utils.quote(requests.utils.unquote(link.get("href")))
    return dom

def fetch_page_content(url, browser):
    """Fetch the HTML content of a page."""
    browser.get(url)
    html = None
    try:
        section = WebDriverWait(browser, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "section.body__detail-Wrapper"))
        )        
        html = extract_content_from_html( browser.page_source, url)
    except Exception as e:
        print(e)
    return html

def parse_html_to_markdown(html_content):
    """Parse HTML content and convert it to Markdown."""
    soup = BeautifulSoup(html_content, 'html.parser')
    markdown_content = md(str(soup))
    return markdown_content

def update_last_fetched(url):
    """Update the last fetched timestamp for a URL."""
    try:
        with open(LAST_FETCHED_FILE, 'r') as file:
            last_fetched = json.load(file)
    except FileNotFoundError:
        last_fetched = {}
    
    last_fetched[url] = time.time()
    
    with open(LAST_FETCHED_FILE, 'w') as file:
        json.dump(last_fetched, file)



def scrape_general_pages(browser):
    """Scrape general pages."""
    sorted_pages = sorted(PAGES_DATA, key=lambda x: x['updated'])
    candidates = sorted_pages[:10]
    random.shuffle(candidates)
    for candidate in candidates:
                
        print('fetching:',candidate['url'])
        html_content = fetch_page_content(candidate['url'], browser)
        content = md(str(html_content))                
        filename = PATH_MAP[candidate['type']]+candidate['title']+'.md'
        print('saving to:',filename)
        open(filename, 'w').write(content)
        for page in PAGES_DATA:
            if page['url'] == candidate['url']:
                page['updated'] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
                break
        # save updated pages_data.yml
        with open('pages_data.yml', 'w') as file:
            yaml.dump(PAGES_DATA, file, default_flow_style=False, allow_unicode=True)
            print('updated pages_data.yml')

        #wait random time
        time.sleep(random.uniform(4, 12))  # Random wait to mimic human behavior
        

    # markdown_content = parse_html_to_markdown(html_content)
    # # Save markdown_content to file or process as needed
    # update_last_fetched(url)

def scrape_service_pages(browser):
    """Scrape service pages."""
    # Fetch and parse the service index page to get a list of service URLs
    service_urls = []  # Implement fetching and parsing of service URLs
    for url in service_urls:
        html_content = fetch_page_content(url, browser)
        markdown_content = parse_html_to_markdown(html_content)
        # Save markdown_content to file or process as needed
        update_last_fetched(url)

def main():
    browser = setup_browser()
    try:
        scrape_general_pages(browser)
        # scrape_service_pages(browser)
    finally:
        browser.quit()

if __name__ == "__main__":
    main()
