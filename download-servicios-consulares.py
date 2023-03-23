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


def save_url_response_to_file(path, content):
    folder_name,file_name = path
    file_name = file_name+".md"
    os.makedirs(folder_name, exist_ok=True)
    file_path = os.path.join(folder_name, os.path.basename(file_name))
    with open(file_path, 'w') as f:
        f.write(content)

def fix_links(dom):
    for link in dom.find_all("a", href=True):
        if link.get("href").startswith("/"):
            link["href"] = "https://www.exteriores.gob.es" + requests.utils.quote(requests.utils.unquote(link.get("href")))
    return dom


def fix_target_bank(dom):
    for link in dom.find_all("a", target="_blank"):
        link.attrs = {k: v for k, v in link.attrs.items() if k != "title"}
        for img in link.find_all("img"):
            img.decompose()
    return dom 

def content_from_page(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    wrapper_divs = soup.find_all("div", class_="single__detail-Wrapper")
    last_wrapper_div = wrapper_divs[-1]
    # Remove any <img> tags and the "title" attribute inside <a> tags with target="_blank" and title="Se abre en ventana nueva"
    for link in last_wrapper_div.find_all("a", target="_blank", title="Se abre en ventana nueva"):
        link.attrs = {k: v for k, v in link.attrs.items() if k != "title"}
        for img in link.find_all("img"):
            img.decompose()
    last_wrapper_div = fix_links(last_wrapper_div)
    return str(last_wrapper_div)


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

def save_markdown_content(page,wait = 0):
    directory,filename,url = page
    response = requests.get(url)
    div = extract_content_from_html(response.content,url)
    content = markdownify(str(div))
    save_url_response_to_file((directory,filename), content)
    print(url)
    time.sleep(0)

def fetch_pages_servicios():
    url_base = "https://www.exteriores.gob.es/Consulados/amsterdam/es/ServiciosConsulares/Paginas/index.aspx"
    headers = {"User-Agent": UserAgent().random}
    response = requests.get(url_base, headers=headers)
    html_content = response.content
    soup = BeautifulSoup(html_content, "html.parser")
    selects = soup.find_all("select")
    servicios = [(option.get("parentcategory"), option.get("value"))
                for select in selects
                for option in select.find_all("option") if option.get("parentcategory")]
    return [('Servicios Consulares/'+category[0],category[1],category_url(category))for category in servicios]


pages = [('Páginas', 'Consul', 'https://www.exteriores.gob.es/Consulados/amsterdam/es/Consulado/Paginas/Consul.aspx'),
('Páginas', 'Consulado', 'https://www.exteriores.gob.es/Consulados/amsterdam/es/Consulado/Paginas/Consulado.aspx'),
('Páginas', 'Demarcación', 'https://www.exteriores.gob.es/Consulados/amsterdam/es/Consulado/Paginas/Demarcaci%c3%b3n.aspx'),
('Páginas', 'Horario, localización y contacto', 'https://www.exteriores.gob.es/Consulados/amsterdam/es/Consulado/Paginas/Horario,-localizaci%c3%b3n-y-contacto.aspx'),
('Páginas', 'Ofertas de empleo', 'https://www.exteriores.gob.es/Consulados/amsterdam/es/Consulado/Paginas/Ofertas-de-empleo.aspx'),
('Páginas', 'Tasas consulares 2023', 'https://www.exteriores.gob.es/Consulados/amsterdam/es/Consulado/Paginas/TASAS-CONSULARES-2023.aspx'),
('Páginas', 'Establecerse', 'https://www.exteriores.gob.es/Consulados/amsterdam/es/ViajarA/Paginas/Establecerse.aspx'),
('Páginas', 'Trabajar', 'https://www.exteriores.gob.es/Consulados/amsterdam/es/ViajarA/Paginas/Trabajar.aspx'),
('Páginas', 'Educación y sanidad', 'https://www.exteriores.gob.es/Consulados/amsterdam/es/ViajarA/Paginas/Educaci%c3%b3n-y-sanidad.aspx'),
('Páginas', 'Enlaces de interés', 'https://www.exteriores.gob.es/Consulados/amsterdam/es/ViajarA/Paginas/Enlaces-de-inter%c3%a9s.aspx'),
('Páginas', 'Seguridad y otros aspectos', 'https://www.exteriores.gob.es/Consulados/amsterdam/es/ViajarA/Paginas/Seguridad-y-otros-aspectos.aspx'),
('Páginas', 'Consejode Residentes-Españoles', 'https://www.exteriores.gob.es/Consulados/amsterdam/es/ViajarA/Paginas/Consejo-de-Residentes-Espa%c3%b1oles.aspx'),
('Páginas', 'Documentación y trámites', 'https://www.exteriores.gob.es/Consulados/amsterdam/es/ViajarA/Paginas/Documentaci%c3%b3n-y-tr%c3%a1mites.aspx'),
('Páginas', 'Conoce Espana', 'https://www.exteriores.gob.es/es/ServiciosAlCiudadano/Paginas/Conoce-Espana.aspx'),
('Páginas', 'Recomendaciones de viaje', 'https://www.exteriores.gob.es/Consulados/amsterdam/es/ViajarA/Paginas/Recomendaciones-de-viaje.aspx'),
('Páginas', 'Noticias', 'https://www.exteriores.gob.es/Consulados/amsterdam/es/Comunicacion/Noticias/Paginas/index.aspx'),
# paginas web de la embajada
('Páginas', 'Embajador-a',"https://www.exteriores.gob.es/Embajadas/lahaya/es/Embajada/Paginas/Embajador.aspx"),
('Páginas', 'Contacto. Embajada',"https://www.exteriores.gob.es/Embajadas/lahaya/es/Embajada/Paginas/Contacto.aspx"),
('Páginas', 'Embajada',"https://www.exteriores.gob.es/Embajadas/lahaya/es/Embajada/Paginas/Embajada.aspx"),
('Páginas', 'Consulados',"https://www.exteriores.gob.es/Embajadas/lahaya/es/Embajada/Paginas/Consulados.aspx"),
('Páginas', 'Horario, localización y contacto. Embajada',"https://www.exteriores.gob.es/Embajadas/lahaya/es/Embajada/Paginas/Horario,-localizaci%c3%b3n-y-contacto.aspx"),
('Páginas', 'Ofertas de empleo. Embajada',"https://www.exteriores.gob.es/Embajadas/lahaya/es/Embajada/Paginas/Ofertas-de-empleo.aspx"),
('Páginas', 'Documentación y trámites. Embajada',"https://www.exteriores.gob.es/Embajadas/lahaya/es/ViajarA/Paginas/Documentaci%c3%b3n-y-tr%c3%a1mites.aspx"),
('Páginas', 'Establecerse. Embajada',"https://www.exteriores.gob.es/Embajadas/lahaya/es/ViajarA/Paginas/Establecerse.aspx"),
('Páginas', 'Educación y sanidad. Embajada',"https://www.exteriores.gob.es/Embajadas/lahaya/es/ViajarA/Paginas/Educaci%c3%b3n-y-Sanidad.aspx"),
('Páginas', 'Trabajar. Embajada',"https://www.exteriores.gob.es/Embajadas/lahaya/es/ViajarA/Paginas/Trabajar.aspx"),
('Páginas', 'Enlaces de interés. Embajada',"https://www.exteriores.gob.es/Embajadas/lahaya/es/ViajarA/Paginas/Enlaces-de-inter%c3%a9s.aspx"),
('Páginas', 'Recomendaciones de viaje. Embajada',"https://www.exteriores.gob.es/Embajadas/lahaya/es/ViajarA/Paginas/Recomendaciones-de-viaje.aspx"),
('Páginas', 'Noticias. Embajada',"https://www.exteriores.gob.es/Embajadas/lahaya/es/Comunicacion/Noticias/Paginas/index.aspx")
 ]



pages += fetch_pages_servicios()
for p in pages:    
    save_markdown_content(p,3)

    