from fake_useragent import UserAgent
from markdownify import markdownify
from bs4 import BeautifulSoup
import requests
import hashlib
import re
import os

## prepare the list of pages to scrape
pages = [('Páginas', 'Consul', 'https://www.exteriores.gob.es/Consulados/amsterdam/es/Consulado/Paginas/Consul.aspx'),
('Páginas', 'Consulado', 'https://www.exteriores.gob.es/Consulados/amsterdam/es/Consulado/Paginas/Consulado.aspx')]

url_base = "https://www.exteriores.gob.es/Consulados/amsterdam/es/ServiciosConsulares/Paginas/index.aspx"
response = requests.get(url_base, headers={"User-Agent": UserAgent().random})
html = BeautifulSoup(response.content, "html.parser")

services = []
for select in html.find_all("select"):
    for option in select.find_all("option"):
        if option.get("parentcategory"):
            category = option.get("parentcategory")
            page = option.get("value")            
            path = 'Servicios Consulares/'+category
            url = f"{url_base}?scco=Pa%C3%ADses+Bajos&scd=9&scca={requests.utils.quote(path)}&scs={requests.utils.quote(page)}"
            services.append((path, page, url))

changes = False
## begin page scraping
for page in pages+services:    
    directory,filename,url = page
    print(url)  
    
    # fetch and parse the page
    html_content = requests.get(url).content
    soup = BeautifulSoup(html_content, "html.parser")
    container = BeautifulSoup("<div></div>", "html.parser").div
    
    # extract the relevant content
    section_content = soup.find_all("div", class_="single__detail-Wrapper")[-1]
    if section_content:
        container.append(section_content)
    
    news_section = soup.find("ul", class_="newResults__list")
    if news_section:
        container.append(news_section)

    travel = soup.find("div", class_="main-content-travel-recommendation")
    if travel:
        container.append(travel)

    accordeon = soup.find("div", class_="section__accordion-wrapper")
    if accordeon:
        container.append(accordeon)

    # clean up the content
    for link in container.find_all("a", target="_blank"):
        link.attrs = {k: v for k, v in link.attrs.items() if k != "title"}
        for img in link.find_all("img"):
            img.decompose()

    for link in container.find_all("a", href=True):
        if link.get("href").startswith("/"):
            link["href"] = "https://www.exteriores.gob.es" + requests.utils.quote(requests.utils.unquote(link.get("href")))

    # add a link to the original page
    original_link = soup.new_tag('a', href=url)
    original_link.string = 'Enlace a la página original'
    container.append(original_link)
    # convert to markdown
    md_content = markdownify(str(container))
    
    # clean up the markdown
    if filename.startswith("Noticias"):
        days = ["lunes", "martes", "mi[eé]rcoles", "jueves", "viernes", "s[aá]bado", "domingo"]
        days_pattern = "|".join(days)
        pattern = re.compile(rf'(?i)({days_pattern}),\s', re.MULTILINE)
        md_content = pattern.sub('', md_content)
        
    if filename.startswith("Recomendaciones"):
        pattern = re.compile(r"(?i)(Recomendaciones vigentes) a \d{1,2} de [a-zA-Z]+ de \d{4}")
        md_content = pattern.sub(r'\1', md_content)

    # save the markdown file and check for changes
    os.makedirs(directory, exist_ok=True)
    file_path = os.path.join(directory, os.path.basename( filename+".md"))
    if not os.path.exists(file_path):
        with open(file_path, "w") as file:
            file.write(md_content)
        changes |= True 
    else:        
        with open(file_path, "rb") as file:
            file_content = file.read()
            old_hash = hashlib.sha256(file_content).hexdigest()
        new_hash = hashlib.sha256(md_content.encode()).hexdigest()
        if old_hash != new_hash:
            with open(file_path, "w") as file:
                file.write(md_content)
                changes |= True

# send a notification to telegram
if changes:
    bot_token , chat_id = open('bot-token.txt', 'r').read().split(',')
    payload = {
        "chat_id": chat_id,
        "text": f'[🔄 Cambios web consulado](https://github.com/JuanMaCuevas/consulado-es-amsterdam/commits/develop/)',
        "parse_mode": "MarkdownV2",
        "disable_web_page_preview": True
    }
    requests.post(f"https://api.telegram.org/bot{bot_token}/sendMessage", data=payload)


