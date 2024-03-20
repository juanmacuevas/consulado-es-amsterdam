from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from markdownify import markdownify 
from fake_useragent import UserAgent
from selenium import webdriver
from bs4 import BeautifulSoup
import requests
import random
import time
import yaml
import os


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

def clean_html_content(html_content,url):
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

def fetch_html(browser,page):
    print('fetching:',page['title'])
    """Fetch the HTML content of a page."""
    browser.get(page['url'])
    element = {
        'page':'section.body__detail-Wrapper',
        'service':'section.section__mainSearch-wrapper'}[page['page_type']]
    html = None
    try:
        section = WebDriverWait(browser, 10).until( EC.visibility_of_element_located((By.CSS_SELECTOR, element)) )        
        html = browser.page_source
    except Exception as e:
        print(e)
    return html


def parse_html_to_markdown(html_content):
    """Parse HTML content and convert it to Markdown."""
    soup = BeautifulSoup(html_content, 'html.parser')
    markdown_content = md(str(soup))
    return markdown_content


def save_file(page, content):
    filename = get_filename(page)
    print('saving to:',filename)   
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

def pick_next_candidates(amount):
    """Pick the next pages to scrape."""
    sorted_pages = sorted(PAGES_DATA, key=lambda x: x['updated'])
    candidates = sorted_pages[:min(amount,len(sorted_pages))]
    random.shuffle(candidates)
    return candidates

def substitute_dates(text):
    days = ["lunes", "martes", "mi[eé]rcoles", "jueves", "viernes", "s[aá]bado", "domingo"]
    days_pattern = "|".join(days)
    pattern = re.compile(rf'(?i)({days_pattern}),\s', re.MULTILINE)
    return pattern.sub('', text)

def remove_date_from_recomendaciones(text):
    pattern = re.compile(r"(?i)(Recomendaciones vigentes) a \d{1,2} de [a-zA-Z]+ de \d{4}")
    return pattern.sub(r'\1', text)

def clean_markdown(content,title):
    """ exceptions to avoid periodic notifications changes """
    if title.startswith("Noticias"):
            return substitute_dates(content)
    elif title.startswith("Recomendaciones"):
            return remove_date_from_recomendaciones(content)

def get_filename(page):        
    if page['type'] == 'page':
        return 'Páginas/'+page['title']+'.md'
    elif page['type'] == 'service':
        return f'Servicios Consulares/{page["category"]}/'+page['title']+'.md'


def update_status(url):
    # update list
    for page in PAGES_DATA:
        if page['url'] == url:
            page['updated'] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            break
    # save list to  pages_data.yml
    with open('pages_data.yml', 'w') as file:
        yaml.dump(PAGES_DATA, file, default_flow_style=False, allow_unicode=True)
        print('updated pages_data.yml')

def convert_to_markdown(html_content,page):
    html = clean_html_content( html_content, page['url'])        
    content =  markdownify(str(html))  
    return  clean_markdown(content,page['title'])

def main():
    # verify_unique_urls(PAGES_DATA)
    browser = setup_browser()
    try:
        candidates = pick_next_candidates(20)    
        for candidate in candidates:            
            html_content = fetch_html(browser, candidate)                            
            content = convert_to_markdown(html_content,candidate)                       
            save_file(candidate, content)
            update_status(url)
            
            time.sleep(random.uniform(4, 8))  # Random wait to mimic human behavior
    finally:
        browser.quit()

if __name__ == "__main__":
    main()
