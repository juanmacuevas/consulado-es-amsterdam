import os
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from markdownify import markdownify
import time


def category_url(category_subcategory):
    url_base = "https://www.exteriores.gob.es/Consulados/amsterdam/es/ServiciosConsulares/Paginas/index.aspx"
    category_encoded = requests.utils.quote(category_subcategory[0])
    subcategory_encoded = requests.utils.quote(category_subcategory[1])
    url = f"{url_base}?scco=Pa%C3%ADses+Bajos&scd=9&scca={category_encoded}&scs={subcategory_encoded}"
    return url


def save_url_response_to_file(cat, content):
    folder_name = 'Servicios Consulares/'+cat[0]
    file_name = cat[1]+".md"
    os.makedirs(folder_name, exist_ok=True)
    file_path = os.path.join(folder_name, os.path.basename(file_name))
    with open(file_path, 'w') as f:
        f.write(content)


def content_from_page(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    wrapper_divs = soup.find_all("div", class_="single__detail-Wrapper")
    last_wrapper_div = wrapper_divs[-1]
    # Remove any <img> tags and the "title" attribute inside <a> tags with target="_blank" and title="Se abre en ventana nueva"
    for link in last_wrapper_div.find_all("a", target="_blank", title="Se abre en ventana nueva"):
        link.attrs = {k: v for k, v in link.attrs.items() if k != "title"}
        for img in link.find_all("img"):
            img.decompose()

    for link in last_wrapper_div.find_all("a", href=True):
        if link.get("href").startswith("/"):
            link["href"] = "https://www.exteriores.gob.es" + \
                requests.utils.quote(requests.utils.unquote(link.get("href")))

    return str(last_wrapper_div)


url_base = "https://www.exteriores.gob.es/Consulados/amsterdam/es/ServiciosConsulares/Paginas/index.aspx"
headers = {"User-Agent": UserAgent().random}
response = requests.get(url_base, headers=headers)
html_content = response.content
soup = BeautifulSoup(html_content, "html.parser")
selects = soup.find_all("select")
categories = [(option.get("parentcategory"), option.get("value"))
              for select in selects
              for option in select.find_all("option") if option.get("parentcategory")]

categories = [category+(category_url(category),)for category in categories]


for cat in categories:
    url = cat[-1]
    response = requests.get(url)
    html_content = content_from_page(response.content)
    content = markdownify(html_content)
    save_url_response_to_file(cat[:2], content)
    # Wait for 2 seconds
    time.sleep(2)

    # print(cat[:2], 'saved')
    # print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
