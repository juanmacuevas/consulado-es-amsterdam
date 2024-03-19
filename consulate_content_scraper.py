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

def verify_unique_urls(data):
    """Verify that all URLs are unique."""
    urls = {page['url'] for page in data}
    if len(urls) != len(data):
        raise ValueError("Duplicate URLs in pages_data.yml")
    

def setup_browser():
    """Setup headless Chrome browser with random user agent."""
    user_agent = UserAgent().random
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument(f"user-agent={user_agent}")
    browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    return browser

def replace_ol_with_ul(soup):
    for ol_tag in soup.find_all('ol'):
        ul_tag = soup.new_tag('ul')
        ul_tag.attrs = ol_tag.attrs

        # Directly move each child from <ol> to the new <ul>, including non-<li> elements
        for child in list(ol_tag.children):
            ul_tag.append(child)

        ol_tag.replace_with(ul_tag)



def remove_empty_p(soup):
    for p_tag in soup.find_all('p'):
        if not p_tag.text.strip():
            p_tag.decompose()

def extract_content_from_html(html_content,url):
    soup = BeautifulSoup(html_content, "html.parser")
    parent_div = BeautifulSoup("<div></div>", "html.parser").div

    remove_empty_p(soup)
    replace_ol_with_ul(soup)

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
        html =  browser.page_source
    except Exception as e:
        print(e)
    return html

def get_html_content_with_element(url, browser,element):
    """Fetch the HTML content of a page."""
    browser.get(url)
    html = None
    try:
        section = WebDriverWait(browser, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, element))
        )        
        html = browser.page_source
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

import os

def write_to_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)


def scrape_general_pages(browser):
    """Scrape general pages."""

    ### for testing only APPLY FILTERS###
    # PAGES_DATA = [page for page in PAGES_DATA if page['type'] == 'service']
    # PAGES_DATA = [page for page in PAGES_DATA if page['title'] == 'Matrimonios']
    ### end testing only####

    sorted_pages = sorted(PAGES_DATA, key=lambda x: x['updated'])
    candidates = sorted_pages[:10]
    random.shuffle(candidates)
    for candidate in candidates:
        url = candidate['url']
        print('fetching:',)
        if candidate['type'] == 'page':
            html_content = get_html_content_with_element(url, browser,"section.body__detail-Wrapper")            
        elif candidate['type'] == 'service':
            html_content = get_html_content_with_element(url, browser,"section.section__mainSearch-wrapper")
        html = extract_content_from_html( html_content, url)
        
        # input('press enter to continue')
        content = md(str(html))  
        # exceptions to avoid periodic notifications changes
        if candidate['title'].startswith("Noticias"):
            content = substitute_dates(content)
        if candidate['title'].startswith("Recomendaciones"):
            content = remove_date_from_recomendaciones(content)

        if candidate['type'] == 'page':
            filename = 'Páginas/'+candidate['title']+'.md'
        elif candidate['type'] == 'service':
            filename = f'Servicios Consulares/{candidate["category"]}/'+candidate['title']+'.md'
        
        print('saving to:',filename)
        write_to_file(filename, content)

        for page in PAGES_DATA:
            if page['url'] == url:
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




def main():
    verify_unique_urls(PAGES_DATA)
    browser = setup_browser()
    try:
        scrape_general_pages(browser)
        # content = open('test_out.html','r').read()  
        # # in content replace ordered list OL with unordered lists ul
        # content = content.replace('<ol>','<ul>').replace('</ol>','</ul>')
        # # in content remove empty paragraphs
        # content = content.replace('<p></p>','')
        # mdown = md(str(content))  
        # print(mdown)

    
    finally:
        browser.quit()

if __name__ == "__main__":
    main()
